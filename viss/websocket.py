import asyncio              
import websockets          
import json
import time
from datetime import datetime

def decide_request_type(json):
    if json["action"] == "get":
        if not("filter" in json): 
            return "Read" #Case 1

        elif ("filter" in json):
            if json["filter"]["op-type"] == "paths":
                return "Search Read" #Case 2

            elif json["filter"]["op-type"] == "history":
                return "History Read" #Case 3

    elif json["action"] == "set":
        return "Update" #Case 4

    elif json["action"] == "subscribe":
        if json["filter"]["op-value"] == "time-based":
            return "Subscribe" #Case 5

        elif json["filter"]["op-value"] == "range":
            return "Curve Logging Subscribe" #Case 6

    elif json["action"] == "unsubscribe":
        return "Unsubscribe" #Case 7

    else:
        return "Action Not Defind" #Case 8

def is_request_authorized(json):
    if "authorization" in json:
        return True
    else:
        return False

async def accept(websocket, path):
        print("client connected")
        while True:
            data = await websocket.recv(); #wait for client
            #print("receive : " + data)

            data_load=json.loads(data)
            request_type = decide_request_type(data_load)

            if request_type == "Read":
                pass

            elif request_type == "Search Read":
                pass

            elif request_type == "History Read":
                pass

            elif request_type == "Update":
                pass

            elif request_type == "Subscribe":
                pass

            elif request_type == "Curve Logging Subscribe":
                pass

            elif request_type == "Unsubscribe":
                pass

            elif request_type == "Action Not Defind":
                pass

            print(decide_request_type(data_load))
            print(is_request_authorized(data_load))

            dt = datetime.now()
            s = str(dt.microsecond)
    
            id=data_load["requestId"]
            response_json = '{"action":"get","requestId":"%s","value":"2372", "timestamp":"%s"}' % (id, s) 

            await websocket.send(response_json); #send response