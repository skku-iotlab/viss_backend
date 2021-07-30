import asyncio                    
import json
import uuid
import time
from datetime import datetime
import jwt

from viss.lib import *
from testdjango.settings import SIMPLE_JWT

working_subscriptionIds = []

def read_vehicle_data():
    with open('viss/vss_final.json') as generated_data:
        return json.loads(generated_data.read())

def is_request_authorized(json):
    if "authorization" in json: return True
    else: return False

def action_(json):
    return json["action"]

def requestId_(json):
    return json["requestId"]

def op_type_(json):
    return json["filter"]["op-type"]

def op_value_(json):
    return json["filter"]["op-value"]

def url_path_(json):
    url_path = json["path"][0:len(json["path"])]
    if url_path[len(url_path)-1] == "/":
        url_path = url_path[0:len(url_path)-1]
    return url_path

def default_response_maker(dl):
    final_json = {}
    final_json["action"] = action_(dl)
    final_json["requestId"] = requestId_(dl)
    return final_json

def error_response_maker(number, reason, message):
    new_json = {}
    new_json["error"] = {}
    new_json["error"]["number"] = number
    new_json["error"]["reason"] = reason
    new_json["error"]["message"] = message
    new_json["ts"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return new_json

#
#
#

async def sub_time_based(dl, websocket, subscriptionId):
    print("now on")
    while subscriptionId in working_subscriptionIds:
        vehicle_data = read_vehicle_data()
        final_json = default_response_maker(dl)
        print(search_read(url_path_(dl), vehicle_data))
        response_json = search_read(url_path_(dl), vehicle_data)
        for key in response_json:
            final_json[key] = response_json[key]
        await websocket.send(json.dumps(final_json))
        await asyncio.sleep(int(dl["filter"]["op-extra"]["period"]))

async def sub_range(dl, websocket, subscriptionId):
    pass

async def sub_change(dl, websocket, subscriptionId):
    pass

async def sub_curve_logging(dl, websocket, subscriptionId):
    pass

def sub_manager(dl, vehicle_data, websocket):
    if action_(dl) == 'subscribe':

        response_json = search_read(url_path_(dl), vehicle_data)
        if "Error Code" not in response_json:
            #success   
            subscriptionId = str(uuid.uuid4())
            working_subscriptionIds.append(subscriptionId)

            if op_value_(dl) == "time-based":
                task = asyncio.create_task(sub_time_based(dl, websocket, subscriptionId))

            elif op_value_(dl) == "range":
                task = asyncio.create_task(sub_range(dl, websocket, subscriptionId))

            elif op_value_(dl) == "change":
                task = asyncio.create_task(sub_change(dl, websocket, subscriptionId))

            elif op_value_(dl) == "curve-logging":
                task = asyncio.create_task(sub_curve_logging(dl, websocket, subscriptionId))

            return {"subscriptionId" : subscriptionId, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
        else:
            #fail
            return response_json

        #task.cancel()

    elif action_(dl) == 'unsubscribe':
        try:
            subscriptionId = dl["subscriptionId"]
            working_subscriptionIds.remove(subscriptionId)
            return {"subscriptionId" : subscriptionId, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
        except:
            return {"error" : {"number" : "404", "reason" : "invalid_subscriptionId", "message": "The specified subscription was not found"}, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
#
#
#

def get_response_based_on_request(dl, vehicle_data, websocket):
    if action_(dl) == 'get':
        if "filter" not in dl:
            return read(url_path_(dl), vehicle_data)
        else:
            if op_type_(dl) == 'paths':
                return search_read(url_path_(dl), vehicle_data, op_value_(dl))
            elif op_type_(dl) == 'history':
                return history_read(url_path_(dl), vehicle_data, op_value_(dl))
            elif op_type_(dl) == 'metadata':
                with open('viss/vss_release_2.1.json') as file_origin:
                    vss_json_file = json.loads(file_origin.read())
                return service_discovery_read(url_path_(dl), vss_json_file, op_value_(dl))
    elif action_(dl) == 'set':
        if "filter" not in dl:
            return update(url_path_(dl), vehicle_data, dl)
    elif action_(dl) == 'subscribe':
        #response_json = 
        return sub_manager(dl, vehicle_data, websocket)
    elif action_(dl) == 'unsubscribe':
        return sub_manager(dl, vehicle_data, websocket)

async def accept(websocket, path):
    print("client connected")
    while True:
        data = await websocket.recv(); #wait for client
        dl = json.loads(data)
        response_json = {}
        vehicle_data = read_vehicle_data()
        print('A')
        if is_request_authorized(dl):
            print('B')
            try:
                body = jwt.decode(dl["authorization"], SIMPLE_JWT['SIGNING_KEY'], SIMPLE_JWT['ALGORITHM'])
                print(body)
                print('C')
                response_json = get_response_based_on_request(dl, vehicle_data, websocket)
            except jwt.ExpiredSignatureError:
                response_json = error_response_maker("401", "token_expired", "Access token has expired.") 
            except jwt.InvalidTokenError:
                response_json = error_response_maker("401", "token_invalid", "Access token is invalid.")      
            else:
                #token_missing
                #too_many_attempts
                pass
        else:
            response_json = get_response_based_on_request(dl, vehicle_data, websocket) 
        if "Error Code" in response_json:
            response_json = error_response_maker(response_json["Error Code"][0:3], response_json["Error Reason"], response_json["message"]) #WEEK POINT: possible hazard
        final_json = default_response_maker(dl)
        for key in response_json:
            final_json[key] = response_json[key]
        print(json.dumps(final_json))
        await websocket.send(json.dumps(final_json))
