import asyncio              
import websockets          
import json
import time
from datetime import datetime
import jwt

from viss.lib import *
from testdjango.settings import SIMPLE_JWT

def is_request_authorized(json):
    if "authorization" in json:
        return True
    else:
        return False

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

def error_response_maker(number, reason, message):
    new_json = {}
    new_json["error"] = {}
    new_json["error"]["number"] = number
    new_json["error"]["reason"] = reason
    new_json["error"]["message"] = message
    new_json["ts"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return new_json

def get_response_based_on_request(dl, vehicle_data):
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
        if op_value_(dl) == "time-based":
            return {}
        elif op_value_(dl) == "range":
            return {}
        elif op_value_(dl) == "change":
            return {}
        elif op_value_(dl) == "curve-logging":
            return {}
    elif action_(dl) == 'unsubscribe':
        return {}

async def accept(websocket, path):
    print("client connected")
    while True:
        data = await websocket.recv(); #wait for client
        dl = json.loads(data)
        response_json = {}

        with open('viss/vss_final.json') as generated_data:
            vehicle_data = json.loads(generated_data.read())

        print('A')
        if is_request_authorized(dl):
            print('B')
            try:
                body = jwt.decode(dl["authorization"], SIMPLE_JWT['SIGNING_KEY'], SIMPLE_JWT['ALGORITHM'])
                print(body)
                print('C')

                response_json = get_response_based_on_request(dl, vehicle_data)

            except jwt.ExpiredSignatureError:
                response_json = error_response_maker("401", "token_expired", "Access token has expired.")
                
            except jwt.InvalidTokenError:
                response_json = error_response_maker("401", "token_invalid", "Access token is invalid.")
                
            else:
                #token_missing
                #too_many_attempts
                pass

        else:
            response_json = get_response_based_on_request(dl, vehicle_data)
        
        if "Error Code" in response_json:
            response_json = error_response_maker(response_json["Error Code"][0:3], response_json["Error Reason"], response_json["message"]) #WEEK POINT: possible hazard

        final_json = {}
        final_json["action"] = action_(dl)
        final_json["requestId"] = requestId_(dl)
        for key in response_json:
            final_json[key] = response_json[key]

        print(json.dumps(final_json))
        await websocket.send(json.dumps(final_json))