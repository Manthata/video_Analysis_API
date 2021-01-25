from flask import Flask, request, jsonify 
from pymongo import MongoClient 
from flask_restful import Api, Resource
from datetime import datetime as d
from flask_cors import CORS
import json
from PIL import Image
import PIL
import base64
import io
import os
from dotenv import load_dotenv
import numpy as np
project_folder = os.path.expanduser(
    '~/nodejs/customerCounter/API_count/web/')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

#Mongo URI 
# uri = os.environ.get('URI')
# create clinet for mongo db 
client = MongoClient('mongo', 27017)
db = client.aNewDB
CustomerCounter = db["Counter"]
# instanciate flask app 
# sio = socketio.Server(async_mode = 'threading', logger=True,
#                       async_handlers=True, always_connect=True)
app = Flask(__name__)
# app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
CORS(app)


#create flask api 
api = Api(app)

# Helper function to check if the camera exis

def time():
    date = d.now()
    date_now = date.strftime("%Y-%m-%d %H:%M:%S")
    return date_now
# def save(frame):
#     date = time()
#     image_bin = base64.b64decode(frame)
#     # print(image_bin)
#     jpg_as_np = np.frombuffer(image_bin, dtype=np.uint8)
#     img = cv2.imdecode(jpg_as_np, cv2.IMREAD_ANYCOLOR)
#     if img.size :
#         print("we supposed to be writting an image")
#         cv2.imwrite('frame'+str(date)+'.jpg', img)







class Count(Resource):
    def post(self):

        # get the posted data
        postedData = request.get_json()
        print("[INFO]",postedData)
        #unpack the data and save it
        date = time()

        CustomerCounter.insert_one({
            "timestamp": date,
            "count": postedData["count"],
            
        })
        
        
        retjson = {
            "Message": "Successfully stored the count",
            "Status": 200
        }

        return jsonify(retjson)
class Retrieve(Resource):
    def post(self): 

        # get posted data 
        postedData = request.get_json()
        print(postedData)

        # if len(Object.values(postedData)) == 1:
        #     data = db.Counter.find({"timestamp": {"$gte": "2016-03-07 11:33:48", "$lt": "2016-03-07 11:34:48"}})


        # retrieve the data accoording to the queries 
        print(postedData)
        querie = {"$gte": postedData["date"][0], "$lt": postedData["date"][1]}
        
        # data = db.Counter.aggregate(
        #     {"timestamp":querie}

            
        #     )
        # print(list(data))
        data = list(db.Counter.aggregate([
            {"$match": {
                "timestamp": querie,
            }},
            
            {"$unset": ["_id"]}
            ]))
        
        # print(data)

        retjson = {
            "Message": "you have successfully retrived all the data",
            "Status": 200,
            "data": data
        }
     
        return jsonify(retjson)
class Latest(Resource):
    def get(self):

        data = list(db.Counter
        .find({}, {'_id': False})
        .limit(10).sort([("$natural", -1)]))
        print(data)
        
        retjson = {
              "Message": "You have successfully retrieved the latest data",
              "Status": 200,
              "data": data
          }

        return jsonify(retjson)
class Retrieve_By_Date(Resource):
    def post(self):
        #get the posted data 
        postedData = request.get_json()
        #change the data into a list of strings 
        day_time = list(postedData["date"][0])

        #delete the strings of time and replace them with min and max time
        for i in range(8):
            day_time.pop(-1)

        print(day_time)
        min_time = ['0', '0', ':', '0', '0', ':', '0', '0']
        max_time = ['2', '3', ':', '5', '9', ':', '5', '9']
    
        begin_day = ''.join(day_time + min_time)
        end_day = ''.join(day_time + max_time)
        print(begin_day)
        print(end_day)
        querie = {"$gte": begin_day, "$lt": end_day}
        data = list(db.Counter.aggregate([
            {"$match": {
                "timestamp": querie,
            }},

            {"$unset": ["_id"]}
        ]))
        print(data)
        # data = list(db.Counter.find({"timestamp": postedData["date"]}, {"_id": False}).sort([("$natural", -1)]))

        if len(data) == 0 :
            retjson = {
                "Message": "The data you requested does not exist, try another date! thank you",
                "Status": 301,
                "Data": "No data"

            }
            return jsonify(retjson)
        else:
            retjson = {
                "Message": "you have succesfully retrieved the data for " + postedData["date"][0],
                "Status": 200,
                "Data": data
                }
            
            return jsonify(retjson)


class Save_video(Resource):
    def post(self):
        date = time()
        # path = os.getcwd()

        postedData = request.get_json()
        img_str = postedData["frame"]
        image_64_decode = base64.decodebytes(bytes(img_str, "utf-8"))
        # create a writable image and write the decoding result
        image_result = open('/data/web/'+'frame'+str(date)+'.jpg', 'wb')
        image_result.write(image_64_decode)

        retjson = {
            "Message": "You have successfully saved video frames",
            "Statsu ": 200
        }

        return jsonify(retjson)



        


api.add_resource(Count, "/store", methods=['GET', 'POST'])
api.add_resource(Retrieve, "/retrieve", methods=['GET', 'POST'])
api.add_resource(Latest, "/latest", methods=["GET"] )
api.add_resource(Retrieve_By_Date, "/ret_by_date", methods=["POST"])
api.add_resource(Save_video, "/save_video", methods=["POST"])

#listen and set up the host 
if __name__ == "__main__":
    app.run( host="0.0.0.0", port=5000, debug=True)
