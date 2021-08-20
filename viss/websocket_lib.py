import asyncio                    
import json
import uuid
import time
from datetime import datetime
import jwt

from viss.bufferedCurve import * 
from viss.error_message import get_error_code
from viss.lib import *
from testdjango.settings import SIMPLE_JWT

###################
#    variables    #
###################

too_many_requests_Ips = {}
too_many_attempts_Ips = {}
working_subscriptionIds = {}
DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME = 1

###################
#      tools      #
###################
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

def sub_response_maker(dl):
    final_json = {}
    final_json["action"] = "subscription"
    final_json["requestId"] = requestId_(dl)
    return final_json

# Deprecated #
def error_response_maker(number, reason, message):
    print("Deprecated: plz use viss.error_message get_error_code()")
    new_json = {}
    new_json["error"] = {}
    new_json["error"]["number"] = number
    new_json["error"]["reason"] = reason
    new_json["error"]["message"] = message
    new_json["ts"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return new_json

###################
#  subscriptions  #
###################
async def sub_time_based(dl, websocket, subscriptionId):
    while subscriptionId in working_subscriptionIds:
        final_json = sub_response_maker(dl)
        response_json = search_read(url_path_(dl), read_vehicle_data())
        for key in response_json:
            final_json[key] = response_json[key]
        await websocket.send(json.dumps(final_json))
        await asyncio.sleep(int(dl["filter"]["op-extra"]["period"]))

async def sub_range(dl, websocket, subscriptionId):
    final_json = sub_response_maker(dl)
    response_json = None
    logic_op = dl["filter"]["op-extra"]["logic-op"]
    if logic_op not in ["eq", "ne", "gt", "gte", "lt", "lte"]:
        response_json = get_error_code("filter_invalid")
    boundary = float(dl["filter"]["op-extra"]["boundary"])
    while True:
        if not(subscriptionId in working_subscriptionIds):
            break
        data = read(url_path_(dl), read_vehicle_data())
        dp = float(data['data']['dp']['value'])
        print("..........") #testcode
        print(dp) #testcode
        if logic_op == "eq" and dp == boundary:
            response_json = data
        elif logic_op == "ne" and dp != boundary:
            response_json = data
        elif logic_op == "gt" and dp > boundary:
            response_json = data
        elif logic_op == "gte" and dp >= boundary:
            response_json = data
        elif logic_op == "lt" and dp < boundary:
            response_json = data
        elif logic_op == "lte" and dp <= boundary:
            response_json = data
        if response_json != None:
            for key in response_json:
                final_json[key] = response_json[key]
            await websocket.send(json.dumps(final_json))
            del working_subscriptionIds[subscriptionId]
            break                
        await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)

async def sub_change(dl, websocket, subscriptionId):
    final_json = sub_response_maker(dl)
    response_json = None
    logic_op = dl["filter"]["op-extra"]["logic-op"]
    if logic_op not in ["eq", "ne", "gt", "gte", "lt", "lte"]:
        response_json = get_error_code("filter_invalid")
    diff = float(dl["filter"]["op-extra"]["diff"])
    data = read(url_path_(dl), read_vehicle_data())
    await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)
    while True:
        if not(subscriptionId in working_subscriptionIds):
            break
        new_data = read(url_path_(dl), read_vehicle_data())
        if new_data['data']['dp']['ts'] == data['data']['dp']['ts']:
            pass
        else:
            current_diff = float(new_data['data']['dp']['value']) - float(data['data']['dp']['value'])
            print("..........") #testcode
            print(current_diff) #testcode
            if logic_op == "eq" and current_diff == diff:
                response_json = new_data
            elif logic_op == "ne" and current_diff != diff:
                response_json = new_data
            elif logic_op == "gt" and current_diff > diff:
                response_json = new_data
            elif logic_op == "gte" and current_diff >= diff:
                response_json = new_data
            elif logic_op == "lt" and current_diff < diff:
                response_json = new_data
            elif logic_op == "lte" and current_diff <= diff:
                response_json = new_data
            if response_json != None:
                for key in response_json:
                    final_json[key] = response_json[key]
                await websocket.send(json.dumps(final_json))
                del working_subscriptionIds[subscriptionId]
                break
            data = new_data
        await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)

async def sub_curve_logging(dl, websocket, subscriptionId):
    final_json = sub_response_maker(dl)
    max_err = float(dl["filter"]["op-extra"]["max-err"])
    buf_size = int(dl["filter"]["op-extra"]["buf-size"])
    data_curve = Curve(bufferSize=buf_size, allowedError=max_err, errorType=Distance.VERTICAL)
    time_recorder = []
    data = read(url_path_(dl), read_vehicle_data())
    await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)
    j = 0
    while j < buf_size:
        if not(subscriptionId in working_subscriptionIds):
            break
        new_data = read(url_path_(dl), read_vehicle_data())
        if new_data['data']['dp']['ts'] == data['data']['dp']['ts']:
            pass
        else:
            time_recorder.append(data['data']['dp']['ts'])
            data_curve.add_point(j, float(data['data']['dp']['value']))
            print('buffer #', j, float(data['data']['dp']['value'])) #testcode
            j += 1
        data = new_data
        await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)
    else:
        output_data = data_curve.get_reduced_points()
        response_json = {}
        response_json["data"] = {}
        response_json["data"]["path"] = url_path_(dl)
        response_json["data"]["dp"] = []
        for i in range(0, len(output_data)):
            dp = {}
            dp["ts"] = time_recorder[output_data[i][0]]
            dp["value"] = output_data[i][1]
            response_json["data"]["dp"].append(dp)
        for key in response_json:
            final_json[key] = response_json[key]
        await websocket.send(json.dumps(final_json))
        del working_subscriptionIds[subscriptionId]

def sub_manager(dl, vehicle_data, websocket, sessionId):
    response_json = search_read(url_path_(dl), vehicle_data)
    print(response_json)
    if "error" in response_json['data']:
        return response_json
    subscriptionId = str(uuid.uuid1()) #mac addr and time based
    working_subscriptionIds[subscriptionId] = sessionId

    if op_value_(dl) == "time-based":
        task = asyncio.create_task(sub_time_based(dl, websocket, subscriptionId))

    elif op_value_(dl) == "range":
        with open('viss/vss_release_2.1.json') as file_origin:
            path_list = url_path_(dl).split("/")
            last_path = path_list.pop()
            json_file = json.loads(file_origin.read())
            for i in path_list:
                json_file  = json_file[i]["children"]
            if json_file[last_path]["datatype"] in ["boolean", "string", "string[]", "uint8[]"]:
                return get_error_code("filter_invalid", True)
        try: 
            float(dl["filter"]["op-extra"]["boundary"])
        except:
            return get_error_code("bad_request", True)
        task = asyncio.create_task(sub_range(dl, websocket, subscriptionId))

    elif op_value_(dl) == "change":
        with open('viss/vss_release_2.1.json') as file_origin:
            path_list = url_path_(dl).split("/")
            last_path = path_list.pop()
            json_file = json.loads(file_origin.read())
            for i in path_list:
                json_file  = json_file[i]["children"]
            if json_file[last_path]["datatype"] in ["boolean", "string", "string[]", "uint8[]"]:
                return get_error_code("filter_invalid", True)
        try: 
            float(dl["filter"]["op-extra"]["diff"])
        except:
            return get_error_code("bad_request", True)
        task = asyncio.create_task(sub_change(dl, websocket, subscriptionId))

    elif op_value_(dl) == "curve-logging":
        task = asyncio.create_task(sub_curve_logging(dl, websocket, subscriptionId))

    return {"subscriptionId" : subscriptionId, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    #task.cancel() # test code

def unsub_manager(dl, sessionId):
    subscriptionId = dl["subscriptionId"]
    try:
        if working_subscriptionIds[subscriptionId] == sessionId:
            del working_subscriptionIds[subscriptionId]
            return {"subscriptionId" : subscriptionId, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
        else:
            return get_error_code("user_forbidden", True)
    except:
        return get_error_code("invalid_subscriptionId", True)

###################
# request handler #
###################

def get_response_based_on_request(dl, vehicle_data, websocket, sessionId):
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
        return sub_manager(dl, vehicle_data, websocket, sessionId)
    elif action_(dl) == 'unsubscribe':
        return unsub_manager(dl, sessionId)
        