from flask import Flask , request, abort,jsonify
import pandas as pd
import sys
import os
import re
import sys
import json
import os.path
import hnswlib
import argparse 
import glob
import numpy as np
#import pika
import amqpstorm
import amqpstorm_pool
from pathlib import Path
from collections import defaultdict

app = Flask(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

#SET SEARCH PARAMS
path = Path(__file__).parent.absolute()

def load_all_models():
    """A function to load models.
    :return: list of models
    :rtype: list
    """
    models = glob.glob(f"{str(path)}/*.bin")
    return ''.join(str(e) for e in models)

def rename_img(image_path):
    wrong_image_name = str(image_path).split('/')[-1]
    correct_image_name = str(image_path).split('/')[-2] + '.png'
    correct_image_path = str(image_path).replace(wrong_image_name, correct_image_name)
    return correct_image_path

def res_desc(json_dict):
	#convert json result to a dataframe
	df = pd.DataFrame(json_dict, columns=json_dict.keys())
	#sort dataframe by confidence column in desending order
	df = df.sort_values('confidence',ascending=False)
	#format the dataframe back to dictionary with list as values
	df = df.to_dict(orient='list')
	return df

def data_prep(dataset_path):
    #df = pd.DataFrame(list_val)
    df = pd.read_json(dataset_path, lines=True)
    df['facial_weights'] = df.apply(lambda df: df['facial_weights'], axis=1)
    return df

df = data_prep(str(path)+"/bin_path")
print(df)
covix = []
len_covix =len(df['facial_weights'].values.tolist())
covix_nested_list =df['facial_weights'].values.tolist()
#set hwlib params
dim = 512
num_elements = len_covix
# Declaring index
p = hnswlib.Index(space = 'l2', dim = dim) # possible options are l2, cosine or ip
#Get pretrained model path
model_path=load_all_models()
p.load_index(str(model_path), max_elements = num_elements)

#connect to broker
uri = 'amqp://guest:guest@localhost:5672/%2F?heartbeat=60'
pool = amqpstorm_pool.QueuedPool(
    create=lambda: amqpstorm.UriConnection(uri),
    max_size=10,
    max_overflow=10,
    timeout=10,
    recycle=3600,
    stale=45,
)
#channel = connection.channel()

def lookup_known_face(query_file_name , face_encoding ,query_session_name):
	json_result ={}
	queryResults=[]

	queryResults.clear()

	# Query dataset, k - number of closest elements (returns 2 numpy arrays)
	labels, distances = p.knn_query(face_encoding, k=10)
	#computing threshold
	hits = {}
	for l in labels.tolist():
		for d in distances.tolist():
			hits = dict(zip(l,d))
	
	#accuracy threshold (1-0.04)*100%
	res = {k: v for k, v in hits.items() if float(v) <=0.50}
	#get the results
	try:
		for l,s in zip(res.keys(),res.values()):
			model_result=df.iloc[l].to_dict() 
			model_result.update({'confidence':np.round(float(float(1.0)-float(s))*100,5)})
			model_result.update({'query_session_name':str(query_session_name)})
			queryResults.append(model_result)

		dd = defaultdict(list)

		json_result={}
		for d in queryResults:
			for key, val in sorted(d.items()): 
				dd[key].append(val)
		d=dict(dd)
		#remove unwanted k,v pairs
		d={i:d[i] for i in d if i!='_id'}
		d={i:d[i] for i in d if i!='img'}
		d={i:d[i] for i in d if i!='score'}
		d={i:d[i] for i in d if i!='facial_weights'}
		#rename url key to img
		d['img']=d.pop('url')
		#assert that all image names are subdirectory
		tmp_img = []
		for item in d['img']:
			correctname = rename_img(item)
			tmp_img.append(correctname)
		d['img'] = tmp_img
		json_result = d

	except KeyError:
		json_result = {}

	return json_result

def int64(obj):
	if isinstance(obj, np.integer):
		return int(obj)
	elif isinstance(obj, np.floating):
		return float(obj)
	elif isinstance(obj, np.ndarray):
		return obj.tolist()
	elif isinstance(obj, datetime.datetime):
		return obj.__str__()

@app.route("/", methods=['POST','GET'])
def home():
	result = {}
	if request.method == 'POST':
		#Get data as dictionary from api endpoint
		dict=request.json
		facial_embending =dict.get('emb')
		query_file_name   =dict.get('qfm')
		query_session_name =dict.get('qsm')
		#query_session_name = 'hello'
		result = lookup_known_face(query_file_name , facial_embending , query_session_name)
		#publish message 
		with pool.acquire() as cxn:
			cxn.channel.queue.declare(str(query_session_name))
			cxn.channel.basic.publish(
				body=json.dumps(result, default=int64),
				exchange='',
				routing_key=str(query_session_name),
				properties={
					'content_type': 'text/plain',
					'headers': {'key': 'value'}
				}
			)
		return 'sucess 200'

if __name__ == "__main__":
    app.run(port=5000,use_reloader=False)
