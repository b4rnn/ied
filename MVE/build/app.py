import os
import string
import random
import subprocess
import itertools
import threading, queue
from flask import Flask, flash, request, redirect, render_template ,jsonify
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from collections import defaultdict
from bson.objectid import ObjectId
from bson.json_util import dumps
from collections import defaultdict

app=Flask(__name__)


cors = CORS(app, resources={

    r"/*": {
        "origins": "*"

    }
})

app.secret_key = "secret key"
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, '/var/www/html/uploads')

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['webp','m4v','vob', 'wmv', 'mov', 'mkv', 'webm', 'gif','mp4','avi','flv'])

tf_queue = queue.Queue()
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))

app.config['MONGO_DBNAME'] = 'photo_bomb'
app.config['MONGO_URI'] = 'mongodb://192.168.0.51:27017/photo_bomb'

mongo = PyMongo(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')

def Merge(dict1, dict2):
    return(dict2.update(dict1))
    
#post video api
@app.route('/videos/' , methods=['POST'])
def upload_file():
    if request.method == 'POST':
        QueryPost = {}
        QueryPost_list = []
        QueryCpp = {}
        QueryCpp_list = []

        #files = request.files.getlist('files[]')
        files = request.files.to_dict() 

        for file in files:
            if file and allowed_file(files[file].filename):
                print(files[file]) 
                #filename = secure_filename(file.filename)
                filename = files[file].filename
                filename=filename.replace(" ", "")
                filename = ''.join(e for e in filename if e.isalnum())
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                files[file].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                random_letters = string.ascii_lowercase
                channel_name =''.join(random.choice(random_letters) for i in range(11))
                QueryPost = {'id':str(channel_name),'videourl':"https://str.appb.casa:227/uploads/"+filename,'imageExtracted':[]}
                QueryPost_list.append(QueryPost)
                QueryCpp = {str(channel_name+':/var/www/html/uploads/'+filename)}
                QueryCpp_list.append(QueryCpp)
        proc = subprocess.Popen(["./IED",str(QueryCpp_list)])
        return jsonify(QueryPost_list)

#get video api
@app.route('/videos/api/file/<id>' , methods=['GET'])
def video(id):
    try:
        videos = mongo.db.videos
        output = []
        for  video in videos.find({'id' : { "$eq" : id}}):
            output.append({'id' : video['id'], 'image' : video['image'], 'videourl' : video['videourl'], 'time' : video['time'], 'progress' : video['progress'], 'streamurl' : video['streamurl']})
        dd = defaultdict(list)
        for d in output:
            for key, val in sorted(d.items()):
                dd[key].append(val)

        result = {}
        result_list = []
        image_list = []
        time_list = []
        progress_list = []

        for k,v in sorted(dd.items()):
            result[k]=list(set(v))
            if k == 'id':
                result[k] = ' '.join(set(map(str, v)))
            if k == 'videourl':
                result[k] = ' '.join(set(map(str, v)))
            if k=='streamurl':
                result[k] = ' '.join(set(map(str, v)))

            if k == 'image':
                for value in range(len(v)):
                    image_dict = {}
                    image_dict['image'] = v[value]
                    image_list.append(image_dict)
                result[k] = image_list
            
            if k == 'time':
                for value in range(len(v)):
                    time_dict = {}
                    time_dict['time'] = v[value]
                    time_list.append(time_dict)
                result[k] = time_list
            
            if k == 'progress':
                for value in range(len(v)):
                    progress_list.append(v[value])
                result[k] = progress_list[-1]
        result['imageExtracted'] = result.pop('image')
        result['videoTimestamp'] = result.pop('time')
        return jsonify(result)
    except KeyError:
        result ={"keyError":"No faces were found"}
        return jsonify(result)

'''
if __name__ == "__main__":
    app.run(host='localhost',port=5005,debug=True,threaded=False)
'''
