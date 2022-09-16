from flask import Flask , request, abort,jsonify
import requests
import random
import string
import simplejson as json
import pandas as pd
import threading
from pymongo import MongoClient
from time import sleep

import amqpstorm
from amqpstorm import Message
from amqpstorm import Connection
from collections import defaultdict

app = Flask(__name__)

class RpcClient(object):
    def __init__(self, host, username, password, rpc_queue):
        self.queue = {}
        self.host = host
        self.final_results ={}
        self.query_file_name =None
        self.queue_response=[]
        self.username = username
        self.password = password
        self.channel = None
        self.connection = None
        self.callback_queue = None
        self.callback_event = 0
        self.rpc_queue = rpc_queue
        self.open()

    def open(self):
        """Open Connection."""
        self.connection = amqpstorm.Connection(self.host, self.username,
                                               self.password)
        self.channel = self.connection.channel()
        self.channel.queue.declare(self.rpc_queue)
        result = self.channel.queue.declare(exclusive=True)
        #self.callback_queue = result['queue']
        self.callback_queue = self.rpc_queue
        self.channel.basic.consume(self._on_response, no_ack=True,
                                   queue=self.callback_queue)
        self._create_process_thread()

    def _create_process_thread(self):
        """Create a thread responsible for consuming messages in response
        RPC requests.
        """
        thread = threading.Thread(target=self._process_data_events)
        thread.setDaemon(True)
        thread.start()

    def _process_data_events(self):
        """Process Data Events using the Process Thread."""
        self.channel.start_consuming()
    
    def _on_response(self, message):
        self.callback_event = self.callback_event +1
        self.queue_response.append(json.loads(message.body))
        if(self.callback_event==int(11)):
            if isinstance(self.queue, dict):
                for k in self.queue:
                    self.queue[k] = self._on_index_response(self.queue_response)

    def _sort_response(self, json_dict):
        #convert json result to a dataframe
        df = pd.DataFrame(json_dict, columns=json_dict.keys())
        #pick top k of the results to display where @k{25}
        df = df.nlargest(25, 'confidence')
        #sort dataframe by confidence column in desending order
        df = df.sort_values('confidence',ascending=False)
        #format the dataframe back to dictionary with list as values
        df = df.to_dict(orient='list')
        return df

    def _on_index_response(self, pooling_results):
        print(len(list(filter(None,pooling_results))))
        results=list(filter(None,pooling_results))
        if len(results) == int(0):
            self.final_results={'result':[{},{'query_file_name':str(self.query_file_name)}]}
        if len(results) > int(0):
            dd = defaultdict(list)
            for d in results:
                for key, val in sorted(d.items()): 
                    for v in val:
                        dd[key].append(v)
            self.final_results = {'result':[self._sort_response(dict(dd)),{'query_file_name':str(self.query_file_name)}]}
        return self.final_results

    def send_request(self, payload):
        # Create the Message object.
        message = Message.create(self.channel, payload)
        message.reply_to = self.callback_queue
        # Create an entry in our local dictionary, using the automatically
        # generated correlation_id as our key.
        self.queue[message.correlation_id] = None
        #mirror query input to clusters
        url = "http://127.0.0.1:8000"
        headers = {'Content-type': 'application/json'}
        requests.post(url, data=json.dumps(payload), headers=headers,timeout=10)
        self.query_file_name=payload['qfm']
        # Return the Unique ID used to identify the request.
        return message.correlation_id

@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        letters = string.ascii_lowercase
        query_session_name =''.join(random.choice(letters) for i in range(3))
        RPC_CLIENT=RpcClient('localhost', 'guest', 'guest', str(query_session_name))
        payload=request.json
        payload.update({'qsm':str(query_session_name)})
        # Send the request and store the requests Unique ID.
        corr_id = RPC_CLIENT.send_request(payload)
        # Wait until we have received a response.
        # TODO: Add a timeout here and clean up if it fails!
        while RPC_CLIENT.queue[corr_id] is None:
            sleep(0.1)

        # Return the response to the user.
        return RPC_CLIENT.queue[corr_id]
        #return RPC_CLIENT.queue.pop(corr_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001,use_reloader=False)
