import asyncio              
import websockets          
import json
import time
from datetime import datetime

from viss.lib import *

# def decide_request_type(json):
#     if json["action"] == "get":
#         if not("filter" in json): 
#             return "Read" #Case 1

#         elif ("filter" in json):
#             if json["filter"]["op-type"] == "paths":
#                 return "Search Read" #Case 2

#             elif json["filter"]["op-type"] == "history":
#                 return "History Read" #Case 3

#     elif json["action"] == "set":
#         return "Update" #Case 4

#     elif json["action"] == "subscribe":
#         if json["filter"]["op-value"] == "time-based":
#             return "Subscribe" #Case 5

#         elif json["filter"]["op-value"] == "range":
#             return "Curve Logging Subscribe" #Case 6

#     elif json["action"] == "unsubscribe":
#         return "Unsubscribe" #Case 7

#     else:
#         return "Action Not Defind" #Case 8

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

async def accept(websocket, path):
        print("client connected")
        while True:
            data = await websocket.recv(); #wait for client
            dl = json.loads(data)

            with open('viss/vss_final.json') as generated_data:
                vehicle_data = json.loads(generated_data.read())

            action = action_(dl)
            requestId = requestId_(dl)
            url_path = url_path_(dl)

            print(is_request_authorized(dl))

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

            #dt = datetime.now()
            #s = str(dt.microsecond)
            #response_json = '{"action":"get","requestId":"%s","value":"2372", "timestamp":"%s"}' % (id, s) 

            response_json["action"] = action
            response_json["requestId"] = requestId
            print(json.dumps(response_json))
            await websocket.send(json.dumps(response_json))