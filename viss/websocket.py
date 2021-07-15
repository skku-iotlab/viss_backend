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

def validate_token(token):
    print(token)
    try:
        body = jwt.decode(token, SIMPLE_JWT['SIGNING_KEY'], SIMPLE_JWT['ALGORITHM'])
        print(body)
        return True
    except jwt.ExpiredSignatureError:
        print(jwt.ExpiredSignatureError)
        return False
    except jwt.InvalidTokenError:
        print(jwt.InvalidTokenError)
        return False
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

async def accept(websocket, path):
        print("client connected")
        while True:
            data = await websocket.recv(); #wait for client
            dl = json.loads(data)
            response_json = {}

            with open('viss/vss_final.json') as generated_data:
                vehicle_data = json.loads(generated_data.read())

            action = action_(dl)
            requestId = requestId_(dl)
            url_path = url_path_(dl)

            print('A')
            if is_request_authorized(dl):
                print('B')
                print(dl["authorization"])
                if validate_token(dl["authorization"]):
                    print('C')
                    # token is exist && token is valid
                    if action == 'get':
                        if "filter" not in dl:
                            response_json = read(url_path, vehicle_data)
                        else:
                            op_type = op_type_(dl)
                            op_value = op_value_(dl)

                            if op_type == 'paths':
                                response_json = search_read(url_path, vehicle_data, op_value)
                            elif op_type == 'history':
                                response_json = history_read(url_path, vehicle_data, op_value)
                            elif op_type == 'metadata':
                                with open('viss/vss_release_2.1.json') as file_origin:
                                    vss_json_file = json.loads(file_origin.read())
                                response_json = service_discovery_read(url_path, vss_json_file, op_value)

                    elif action == 'set':
                        if "filter" not in dl:
                            response_json = update(url_path, vehicle_data, dl)
                    
                    else:
                        pass
                else:
                    #token is exist && token is not valid
                    pass
            else:
                #token not exist
                pass

            #dt = datetime.now()
            #s = str(dt.microsecond)
            #response_json = '{"action":"get","requestId":"%s","value":"2372", "timestamp":"%s"}' % (id, s) 

            response_json["action"] = action
            response_json["requestId"] = requestId
            print(json.dumps(response_json))
            await websocket.send(json.dumps(response_json))