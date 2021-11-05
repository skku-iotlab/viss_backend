import asyncio
from asyncio.tasks import sleep                    
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
working_subscriptionIds = {} # 현재 활성화되어있는 subscription의 id를 관리
DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME = 1
jwt_req_hist = {} 
uns_req_hist = {}
s_req_hist = {}
# for manage various IPaddress
JWT_SPAM_COUNT = 10
JWT_SPAM_TIME = 60
SPAM_COUNT = 20
SPAM_TIME = 60

###################
#      tools      #
###################
def read_vehicle_data():
    try:
        with open('viss/vss_final.json') as generated_data:
            return json.loads(generated_data.read())
    except:
        # data generation과 겹칠 경우, 기다렸다가 다시 open <- 간헐적으로 data_generation과 동시에 open해서 error 발생했었음
        sleep(0.05)
        with open('viss/vss_final.json') as generated_data:
            return json.loads(generated_data.read())

def read_vehicle_metadata():
    try:
        with open('viss/vss_metadata.json') as generated_data:
            return json.loads(generated_data.read())
    except:
        # data generation과 겹칠 경우, 기다렸다가 다시 open <- 간헐적으로 data_generation과 동시에 open해서 error 발생했었음
        sleep(0.05)
        with open('viss/vss_metadata.json') as generated_data:
            return json.loads(generated_data.read())

def is_request_authorized(json):
    if "authorization" in json: return True
    else: return False

def action_(json):
    return json["action"]

def requestId_(json):
    return json["requestId"]

def type_(json):
    return json["filter"]["type"]

def value_(json):
    return json["filter"]["value"]

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
        # working_subscriptionIds에 해당 subscriptionId가 있는 이상, 반복
        final_json = sub_response_maker(dl)
        response_json = search_read(url_path_(dl), read_vehicle_data())
        for key in response_json:
            final_json[key] = response_json[key]
        await websocket.send(json.dumps(final_json))
        await asyncio.sleep(int(dl["filter"]["value"]["period"]))
        # period만큼 sleep했다가 반복

async def sub_range(dl, websocket, subscriptionId):
    final_json = sub_response_maker(dl)
    logic_op_list = []
    if type(dl["filter"]["value"]) == dict:
        logic_op_list.append(dl["filter"]["value"]) # op-extra값이 여러개인 경우
    else:
        logic_op_list = dl["filter"]["value"] # op-extra값이 1개인 경우
    
    while True:
        if not(subscriptionId in working_subscriptionIds):
            break
        print(logic_op_list)
        for condition in logic_op_list:
            logic_op = condition["logic-op"]
            boundary = float(condition["boundary"])
            data = read(url_path_(dl), read_vehicle_data())
            #해당 path data 읽어오기
            print(data)
            dp = float(data['data']['dp']['value'])
            if logic_op == "eq" and dp == boundary:
                continue
            elif logic_op == "ne" and dp != boundary:
                continue
            elif logic_op == "gt" and dp > boundary:
                continue
            elif logic_op == "gte" and dp >= boundary:
                continue
            elif logic_op == "lt" and dp < boundary:
                continue
            elif logic_op == "lte" and dp <= boundary:
                continue
            else:
                break
        else:
            # for-else : for문을 break으로 빠져나오지 않았을때 실행
            # break으로 빠져나오지 않았을 때 = 원하는 boundary와 조건을 만족하는 값이 있을 때, client에 값을 전송
            for key in data:
                final_json[key] = data[key]
            await websocket.send(json.dumps(final_json))
            # del working_subscriptionIds[subscriptionId] #완료 -> 해당 subscription 삭제
            # break
        # 이번 dp는 특정 조건에서 continue를 돌지 못하고 break로 빠져나옴: 대기 후 새로운 dp에 대하여 반복
        await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)


async def sub_change(dl, websocket, subscriptionId):
    final_json = sub_response_maker(dl)
    logic_op_list = []
    if type(dl["filter"]["value"]) == dict:
        logic_op_list.append(dl["filter"]["value"])
    else:
        logic_op_list = dl["filter"]["value"]
    data = read(url_path_(dl), read_vehicle_data())
    while True:
        if not(subscriptionId in working_subscriptionIds):
            break
        print('init data:', data['data']['dp']['value'])
        new_data = read(url_path_(dl), read_vehicle_data())
        if new_data['data']['dp']['ts'] == data['data']['dp']['ts']:
            pass
        else:
            for condition in logic_op_list:
                logic_op = condition["logic-op"]
                diff = float(condition["diff"])
                current_diff = float(new_data['data']['dp']['value']) - float(data['data']['dp']['value'])
                # given diff와 logic-op에 부합하는 값이 발생했을 때, response
                print('init data:', float(data['data']['dp']['value']))
                print("..........") #testcode
                print(current_diff) #testcode
                dp = float(data['data']['dp']['value'])
                if logic_op == "eq" and current_diff == diff:
                    continue
                elif logic_op == "ne" and current_diff != diff:
                    continue
                elif logic_op == "gt" and current_diff > diff:
                    continue
                elif logic_op == "gte" and current_diff >= diff:
                    continue
                elif logic_op == "lt" and current_diff < diff:
                    continue
                elif logic_op == "lte" and current_diff <= diff:
                    continue
                else:
                    break
            else:
                # for-else : for문을 break으로 빠져나오지 않았을때 실행
                # break으로 빠져나오지 않았을 때 = 원하는 boundary와 조건을 만족하는 값이 있을 때, client에 값을 전송
                for key in data:
                    final_json[key] = new_data[key]
                await websocket.send(json.dumps(final_json))
                # del working_subscriptionIds[subscriptionId]
                # break
            # 이번 dp는 특정 조건에서 continue를 돌지 못하고 break로 빠져나옴: 대기 후 새로운 dp에 대하여 반복
            # data = new_data
        await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)

async def sub_curve_logging(dl, websocket, subscriptionId):
    final_json = sub_response_maker(dl)
    max_err = float(dl["filter"]["value"]["maxerr"])
    buf_size = int(dl["filter"]["value"]["bufsize"])
    data = read(url_path_(dl), read_vehicle_data())
    await asyncio.sleep(DEFAULT_VEHICLE_DATA_ACCESS_REFRESH_TIME)
    while True:
        data_curve = Curve(bufferSize=buf_size, allowedError=max_err, errorType=Distance.VERTICAL)
        time_recorder = []
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
            # del working_subscriptionIds[subscriptionId]

def sub_manager(dl, vehicle_data, websocket, sessionId):
    # subscription 요청이 들어왔을 때, request와 
    response_json = search_read(url_path_(dl), vehicle_data)
    print(response_json)
    #일단 접근 가능한 경로인지 확인
    if "error" in response_json:
        return response_json
    subscriptionId = str(uuid.uuid1()) #mac addr and time based
    working_subscriptionIds[subscriptionId] = sessionId
    # subscription Id 생성

    print(type_(dl))
    # if type_(dl) != "capture":
    #     return get_error_code("filter_invalid", True)

    if type_(dl) == "timebased":
        task = asyncio.create_task(sub_time_based(dl, websocket, subscriptionId))
        #range, change, curve-logging과 다르게 data type에 의한 제한 없음

    else:
        with open('viss/vss_release_2.1.json') as file_origin:
            path_list = url_path_(dl).split("/")
            last_path = path_list.pop()
            json_file = json.loads(file_origin.read())
            for i in path_list:
                json_file  = json_file[i]["children"]
            if json_file[last_path]["datatype"] in ["string", "string[]", "uint8[]"]: 
                # range, change, curve-logging sub하려는 target값이 float또는 boolean이 아닐때 -> error
                return get_error_code("invalid_path", True)

        if type_(dl) == "range":
            #error check start
            logic_op_list = []
            if type(dl["filter"]["value"]) == dict:
                logic_op_list.append(dl["filter"]["value"])
            else:
                logic_op_list = dl["filter"]["value"]
            for condition in logic_op_list:
                logic_op = condition["logic-op"]
                boundary = condition["boundary"]
                if logic_op not in ["eq", "ne", "gt", "gte", "lt", "lte"]:
                    return get_error_code("filter_invalid", True)
                try: 
                    float(boundary) #boundary값이 float이 아닌 경우 -> 비교 불가 
                except:
                    return get_error_code("filter_invalid", True)
            #error check end

            task = asyncio.create_task(sub_range(dl, websocket, subscriptionId))

        elif type_(dl) == "change":
            #error check start
            logic_op_list = []
            if type(dl["filter"]["value"]) == dict:
                logic_op_list.append(dl["filter"]["value"])
            else:
                logic_op_list = dl["filter"]["value"]
            for condition in logic_op_list:
                logic_op = condition["logic-op"]
                diff = condition["diff"]
                if logic_op not in ["eq", "ne", "gt", "gte", "lt", "lte"]:
                    return get_error_code("filter_invalid", True)
                try: 
                    float(diff)
                except:
                    return get_error_code("filter_invalid", True)
            #error check end

            task = asyncio.create_task(sub_change(dl, websocket, subscriptionId))

        elif type_(dl) == "curvelog":
            
            #error check start
            try:
                maxerr = float(dl["filter"]["value"]["maxerr"])
                bufsize = float(dl["filter"]["value"]["bufsize"])
            except:
                return get_error_code("filter_invalid")      
            if maxerr < 0:
                return get_error_code("filter_invalid")
            if bufsize < 0:
                return get_error_code("filter_invalid")
            #error check end

            task = asyncio.create_task(sub_curve_logging(dl, websocket, subscriptionId))
        
        else:
            return get_error_code("filter_invalid", True)

    return {"subscriptionId" : subscriptionId, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    #task.cancel() # test code

def unsub_manager(dl, sessionId):
    subscriptionId = dl["subscriptionId"]
    try:
        if working_subscriptionIds[subscriptionId] == sessionId:
            del working_subscriptionIds[subscriptionId]
            return {"subscriptionId" : subscriptionId, "ts" : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
        else:
            return get_error_code("device_forbidden", True)
    except:
        return get_error_code("invalid_subscriptionId", True)

###################
# request handler #
###################

def get_response_based_on_request(dl, vehicle_data, vehicle_metadata, websocket, sessionId):
    if action_(dl) == 'get':
        if "filter" not in dl:
            return read(url_path_(dl), vehicle_data)
        else:
            if type_(dl) == 'paths':
                return search_read(url_path_(dl), vehicle_data, value_(dl))
            elif type_(dl) == 'history':
                return history_read(url_path_(dl), vehicle_data, value_(dl))
            elif type_(dl) == 'static-metadata':
                with open('viss/vss_release_2.1.json') as file_origin:
                    vss_json_file = json.loads(file_origin.read())
                return service_discovery_read(url_path_(dl), vss_json_file, value_(dl))
            elif type_(dl) == 'dynamic-metadata':
                # metadata 해당 경로의 metadata를 가져오기
                return service_discovery_read_2(url_path_(dl), vehicle_metadata, value_(dl))
            else:
                return get_error_code("filter_invalid", True)
    elif action_(dl) == 'set':
        if "filter" not in dl:
            return update(url_path_(dl), vehicle_data, dl)
    elif action_(dl) == 'subscribe':
        return sub_manager(dl, vehicle_data, websocket, sessionId)
    elif action_(dl) == 'unsubscribe':
        return unsub_manager(dl, sessionId)
        