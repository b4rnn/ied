import os
import re
import uuid
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
UPLOAD_FOLDER = os.path.join(path, '/var/www/html/quotas')
UPLOAD_FOLDER_IMAGE = '/var/www/html/cbi'

# Make directory if quotas is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_IMAGE'] = UPLOAD_FOLDER_IMAGE

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['jpg','png','jpeg', 'gif', 'webp', 'svg', 'ico', 'cur','tif','tiff','avif'])

tf_queue = queue.Queue()
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))

app.config['MONGO_DBNAME'] = 'photo_bomb'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/photo_bomb'

mongo = PyMongo(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')

#POIs
@app.route('/api/poi/all', methods=['GET'])
def get_all_persons_of_interest():
  persons = mongo.db.person_of_interest
  output = []
  for person in persons.find():
    output.append({'url':['http://127.0.0.1'],'photo' : 'http://127.0.0.1' + person['photo'], 'name' : person['name'], 'residence' : person['residence'], 'age' : person['age'], 'gender' : person['gender'], 'social_media_profile' : person['social_media_profile'], 'place_of_birth' : person['place_of_birth'], 'id' : person['id'], 'nationality' : person['nationality'], 'education' : person['education'], 'arrest_details' : person['arrest_details']})
  return jsonify({'result' : output})

dd = defaultdict(list)
@app.route('/api/poi/<id>', methods=['GET'])
def get_one_person_of_interest(id):
    person = mongo.db.person_of_interest
    _person = person.find_one({'id' : id})
    if _person:
        output={'id' : _person['id'],'url':['http://127.0.0.1'],'photo' : 'http://127.0.0.1' + _person['photo'], 'name' : _person['name'], 'residence' : _person['residence'], 'age' : _person['age'], 'gender' : _person['gender'], 'social_media_profile' : _person['social_media_profile'], 'place_of_birth' : _person['place_of_birth'], 'id' : _person['id'], 'nationality' : _person['nationality'], 'education' : _person['education'], 'arrest_details' : _person['arrest_details']}
    else:
        output = "No such photo"
    return jsonify({'result' : output})

@app.route('/', methods=['POST','PUT'])
def webhook():
    #request.headers.get('X-SSL-CERT')
    gId = request.form['sId']
    dType = request.form['dType']
    social_media_profile =request.form['social_media_profile']
    name =request.form['name']
    residence =request.form['residence']
    #age = request.form['age']
    age ='18'
    gender =request.form['gender']
    education =request.form['education']
    arrest_details =request.form['arrest_details']
    nationality =request.form['nationality']
    place_of_birth =request.form['place_of_birth']
    image= request.files['photo']
    QueryPost_list = []
    files = request.files.to_dict() 
    for file in files:
        if file and allowed_file(files[file].filename):
            print(files[file]) 
            #filename = secure_filename(file.filename)
            filename = files[file].filename
            filename=filename.replace(" ", "")
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            files[file].save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], filename))
            _residence={'residence':str(residence)}
            _age={'age':str(age)}
            QueryPost_list.append(_age)
            _gender={'gender':str(gender)}
            QueryPost_list.append(_gender)
            _social_media_profile={'social_media_profile':str(social_media_profile)}
            QueryPost_list.append(_social_media_profile)
            _place_of_birth={'place_of_birth':str(place_of_birth)}
            QueryPost_list.append(_place_of_birth)
            _nationality={'nationality':str(nationality)}
            QueryPost_list.append(_nationality)
            _education={'education':str(education)}
            QueryPost_list.append(_education)
            _arrest_details={'arrest_details':str(arrest_details)}
            QueryPost_list.append(_arrest_details)
            _name={'name':str(name)}
            QueryPost_list.append(_name)
            _snapshot={'snapshot':'/var/www/html/cbi/'+str(filename)}
            QueryPost_list.append(_snapshot)
    proc = subprocess.Popen(["/home/thewindisanillusion/Videos/poi/build/POI",str(QueryPost_list)])
    return jsonify(QueryPost_list)
    
    '''

    # BEGIN SEARCH PROCESS
    FEATURE_EXTRACTION_LOGIC(gId, dType, filename_path , social_media_profile , name , residence , age , gender ,place_of_birth , nationality , education , arrest_details)
    try:
        for search_result in fileinput.FileInput("results/results.txt",inplace=1):
                search_results_list.append(search_result.strip())
        search_results_list = list(filter(None, search_results_list))
        print(len(search_results_list))
        print(search_results_list[0])
        print(len(search_results_list))
        dd = defaultdict(list)
        for d in search_results_list:
            _d=ast.literal_eval(d)
            for key, val in sorted(_d.items()):
                q= ''.join(v for v in val)
                dd[key].append(q)
        return dd
    except Exception as e:
        return 'photo not uploaded'
    '''

#IMAGES
@app.route('/images/' , methods=['POST'])
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
                filename_extension=filename.split(".")[-1]
                filename=filename.replace(" ", "")
                filename = ''.join(e for e in filename if e.isalnum())
                size = len(filename)
                _filename = filename[:size - 3]+'.'+filename_extension
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                files[file].save(os.path.join(app.config['UPLOAD_FOLDER'], _filename))
                random_letters = string.ascii_lowercase
                channel_name =''.join(random.choice(random_letters) for i in range(11))
                QueryPost = {'id':str(channel_name),'imageurl':"http://127.0.0.1/quotas/"+_filename,'imageExtracted':[]}
                QueryPost_list.append(QueryPost)
                QueryCpp = {str(channel_name+':/var/www/html/quotas/'+ _filename)}
                QueryCpp_list.append(QueryCpp)
        #tf_queue.put(QueryCpp_list)
        print(QueryCpp_list)
        proc = subprocess.Popen(["./IED",str(QueryCpp_list)])
        return jsonify(QueryPost_list)

@app.route('/images/api/file/<id>' , methods=['GET'])
def video(id):
    try:
        images = mongo.db.images
        output = []
        for  video in images.find({'id' : { "$eq" : id}}):
            output.append({'id' : video['id'], 'image' : video['image'], 'imageurl' : video['imageurl']})
        dd = defaultdict(list)
        for d in output:
            for key, val in sorted(d.items()):
                dd[key].append(val)

        result = {}
        image_list = []
        time_list = []
        progress_list = []

        for k,v in sorted(dd.items()):
            result[k]=list(set(v))
            if k == 'id':
                result[k] = ' '.join(set(map(str, v)))
            if k == 'videourl':
                result[k] = ' '.join(set(map(str, v)))
            if k == 'image':
                for value in range(len(v)):
                    image_dict = {}
                    image_dict['image'] = v[value]
                    image_list.append(image_dict)
                result[k] = image_list
        try:
            result['imageExtracted'] = result.pop('image')
            return jsonify(result)
        except KeyError:
            return jsonify(result)
    except KeyError:
        result ={"keyError":"No faces were found"}
        return jsonify(result)

#CAMERAS
@app.route('/api/locations/', methods=['POST','PUT'])
def register_camera_and_locations():
    result = []
    locationname = request.form['locationname']
    _type= request.form['type']
    address = request.form['address']
    active = request.form['active']
    no_of_cams = request.form['no_of_cams']
    cameraList = request.form['camDetails']
    cam_location = mongo.db.live_cams_locations
    #validate camera locat
    _locationname = cam_location.find_one({'locationname' : locationname})
    if _locationname:
        #select camera from list
        camera_list = ''.join(camera for camera in cameraList)
        if len(camera_list) > 2 :
            single_camera=json.dumps(camera_list[1:-1])
            single_camera_string = single_camera.replace("\"","").replace("'", "\"")
            number_of_string_dictionaries=single_camera_string.count('}')
            if number_of_string_dictionaries == 1:
                single_camera_dict = json.loads(single_camera_string)
                single_camera_dict['id']=location_id
                single_camera_dict.update({'channel_name':str(_locationname['channel_name'])})
                #insert camera
                camera = mongo.db.live_cams.insert(single_camera_dict)
                if camera :
                    result.append(" camera id " + location_id)
                else :
                    result.append(" camera not created")

            if number_of_string_dictionaries > 1:
                cameras=re.findall(r'\{.*?\}', single_camera_string)
                for _camera in cameras:
                    single_camera_dict = json.loads(_camera)
                    single_camera_dict['id']=location_id
                    single_camera_dict.update({'channel_name':str(_locationname['channel_name'])})
                    #insert camera
                    camera = mongo.db.live_cams.insert(single_camera_dict)
                    if camera :
                        result.append(" camera id " + location_id)
                    else :
                        result.append(" camera not created")
        else:
            result.append("add 1 or more camera")
    else:
        #generate channel key 
        letters = string.ascii_lowercase
        #registe queue channel
        channel_name =''.join(random.choice(letters) for i in range(11))
        #register location and camera first time
        camera_location=mongo.db.live_cams_locations.insert({'id' :str(uuid.uuid4()) ,'locationname':locationname,'type' : _type,'address' : address,'active' : active,'no_of_cams': no_of_cams,'channel_name':channel_name})
        if camera_location:
            #select camera from list
            camera_list = ''.join(camera for camera in cameraList)
            if len(camera_list) > 2:
                single_camera=json.dumps(camera_list[1:-1])
                single_camera_string = single_camera.replace("\"","").replace("'", "\"")
                number_of_string_dictionaries=single_camera_string.count('}')
                if number_of_string_dictionaries == 1:
                    single_camera_dict = json.loads(single_camera_string)
                    single_camera_dict['id']=str(camera_location)
                    single_camera_dict.update({'channel_name':channel_name})
                    print(single_camera_dict)
                    #insert camera
                    camera = mongo.db.live_cams.insert(single_camera_dict)
                    if camera :
                        channel_name = ''
                        result.append(" camera id " + str(camera_location))
                    else :
                        result.append(" camera not created")

                if number_of_string_dictionaries > 1:
                    cameras=re.findall(r'\{.*?\}', single_camera_string)
                    for _camera in cameras:
                        single_camera_dict = json.loads(_camera)
                        single_camera_dict['id']=str(camera_location)
                        single_camera_dict.update({'channel_name':channel_name})
                        #insert camera
                        camera = mongo.db.live_cams.insert(single_camera_dict)
                        if camera :
                            channel_name = ''
                            result.append(" camera id " + str(camera_location))
                        else :
                            result.append(" camera not created")
            else:
                result.append("add 1 or more camera") 
    return jsonify({'result' : result})

@app.route('/api/locations/all/', methods=['GET'])
def get_all_camera_locations():
  locations = mongo.db.live_cams_locations
  output = []
  _output = []
  _camera_location = {}
  _camDetails = []
  cameras = mongo.db.live_cams
  for location in locations.find():
      if location:
          _camera_location = {'id': str(location['_id']),'locationname' : location['locationname'], 'type' : location['type'], 'address' : location['address'], 'no_of_cams' : location['no_of_cams'],'channel_name' : location['channel_name']}
          for camera in cameras.find({'id' :str(location['_id'])}):
              if camera:
                  _camDetails.append({'id': str(camera['_id']),'location_id': str(camera['id']),'cameraname' : camera['cameraname'], 'camera_ip' : camera['camera_ip'], 'camera_gps' : camera['camera_gps'], 'camera_type' : camera['camera_type'], 'active' : camera['active'], 'createdAt' : camera['createdAt'],'channel_name' : camera['channel_name'], 'displayname' : camera['displayname']})
              else:
                   _camDetails = []
          _output = [i for n, i in enumerate(_camDetails) if i not in _camDetails[n + 1:]]
          res = [i for i in _output if not (i['channel_name'] != location['channel_name'])]
          _camera_location.update({'camDetails':res})
      output.append(_camera_location)
  return jsonify({'result' : output})

@app.route('/api/locations/<id>', methods=['GET'])
def get_one_camera_location(id):
    location = mongo.db.live_cams_locations
    _location = location.find_one({'_id' : ObjectId(str(id))})
    output = []
    _camera_location = {}
    _camDetails = []
    cameras = mongo.db.live_cams
    if _location:
         _camera_location ={'id': str(_location['_id']),'locationname' : _location['locationname'], 'type' : _location['type'], 'address' : _location['address'], 'no_of_cams' : _location['no_of_cams'],'channel_name' : _location['channel_name']}
         for camera in cameras.find({'id' :str(id)}):
            if camera:
                _camDetails.append({'id': str(camera['_id']),'location_id': str(camera['id']),'cameraname' : camera['cameraname'], 'camera_ip' : camera['camera_ip'], 'camera_gps' : camera['camera_gps'], 'camera_type' : camera['camera_type'], 'active' : camera['active'], 'createdAt' : camera['createdAt'],'channel_name' : camera['channel_name'] , 'displayname' : camera['displayname']})
            else:
                _camDetails = []
         _camera_location.update({'camDetails':_camDetails})
         output.append(_camera_location)
    else:
        output = "No such location"
    return jsonify({'result' : output})

@app.route('/api/locations/camera/all', methods=['GET'])
def get_all_cameras():
  cameras = mongo.db.live_cams
  output = []
  for camera in cameras.find():
    output.append({'id': str(camera['_id']),'location_id': str(camera['id']),'cameraname' : camera['cameraname'], 'camera_ip' : camera['camera_ip'], 'camera_gps' : camera['camera_gps'], 'camera_type' : camera['camera_type'], 'active' : camera['active'], 'createdAt' : camera['createdAt'],'channel_name' : camera['channel_name'] , 'displayname' : camera['displayname']})
  return jsonify({'result' : output})

@app.route('/api/camera/<id>', methods=['GET'])
def get_one_camera(id):
    cameras = mongo.db.live_cams
    camera = cameras.find_one({'_id' : ObjectId(str(id))})
    output = []
    if camera:
         output.append({'id': str(camera['_id']),'location_id': str(camera['id']),'cameraname' : camera['cameraname'], 'camera_ip' : camera['camera_ip'], 'camera_gps' : camera['camera_gps'], 'camera_type' : camera['camera_type'], 'active' : camera['active'], 'createdAt' : camera['createdAt'],'channel_name' : camera['channel_name']})
    else:
        output = "No such camera"
    return jsonify({'result' : output})

@app.route('/api/location/', methods=['POST'])
def register_locations():
    result = []
    request_data = request.get_json()  # getting data from client
    # Movie.add_movie(request_data["title"], request_data["year"],
    #                 request_data["genre"])
    # print(request_data)
    locationname =request_data["locationname"]
    #locationname = request_data['locationname']
    _type= request_data['type']
    address = request_data['address']
    active = request_data['active']
    no_of_cams = request_data['no_of_cams']
    cameraList = request_data['camDetails']
    cam_location = mongo.db.live_cams_locations
    #validate camera locat
    _locationname = cam_location.find_one({'locationname' : locationname})
    # if location exist save camera
    if _locationname:
        location_id =str(_locationname['_id'])
        for index in range(len(cameraList)):
            for camera in cameraList: 
                # single_camera_dict = json.loads(single_camera_string)
                single_camera_dict = {}
                single_camera_dict['id']=location_id
                single_camera_dict['active']=str(camera['active'])
                single_camera_dict['camera_gps']=str(camera['camera_gps'])
                single_camera_dict['camera_ip']=str(camera['camera_ip'])
                single_camera_dict['camera_type']=str(camera['camera_type'])
                single_camera_dict['cameraname']=str(camera['cameraname'])
                single_camera_dict['displayname']=str(camera['displayname'])
                single_camera_dict['createdAt']=str(now.strftime("%m/%d/%Y"))

                #check if camera exists in
                _cameraList =  mongo.db.live_cams.find_one({'camera_ip' : str(camera['camera_ip'])})
                if _cameraList:
                    print(" camera with  id " + str(_cameraList['_id']) + " exists")
                else:
                    single_camera_dict.update({'channel_name':str(_locationname['channel_name'])})            
                    #insert camera
                    camera = mongo.db.live_cams.insert(single_camera_dict)
                    if camera :
                        result.append(" camera id " + location_id)
                    else :
                        result.append(" camera not created")       
                    #return jsonify(dumps(camera))
            return jsonify(dumps({}))
    else:
          #generate channel key 
        letters = string.ascii_lowercase
        #registe queue channel
        channel_name =''.join(random.choice(letters) for i in range(11))
        #register location and camera first time
        camera_location=mongo.db.live_cams_locations.insert({'id' :str(uuid.uuid4()) ,'locationname':locationname,'type' : _type,'address' : address,'active' : active,'no_of_cams': no_of_cams,'channel_name':channel_name})
        print('camera_location ===')

        _locationname = cam_location.find_one({'locationname' : locationname})
    
        # if location exist save camera
        if _locationname:
            print('\n\n\n\n\n\n')
            print(str(_locationname['_id']))

            print('\n\n\n\n\n\n')
            location_id =str(_locationname['_id'])
            for camera in cameraList:  
                # single_camera_dict = json.loads(single_camera_string)
                single_camera_dict = {}
                single_camera_dict['id']=location_id
                single_camera_dict['active']=str(camera['active'])
                single_camera_dict['camera_gps']=str(camera['camera_gps'])
                single_camera_dict['camera_ip']=str(camera['camera_ip'])
                single_camera_dict['camera_type']=str(camera['camera_type'])
                single_camera_dict['cameraname']=str(camera['cameraname'])
                single_camera_dict['displayname']=str(camera['displayname'])
                single_camera_dict['createdAt']=str(now.strftime("%m/%d/%Y"))
                single_camera_dict.update({'channel_name':str(_locationname['channel_name'])})
                #insert camera
                camera = mongo.db.live_cams.insert(single_camera_dict)
                if camera :
                    result.append(" camera id " + location_id)
                else :
                    result.append(" camera not created")       
                return jsonify(dumps(camera))
