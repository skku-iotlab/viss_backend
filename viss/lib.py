import copy
from datetime import datetime, timedelta
import random
import json
from types import resolve_bases

from viss.error_message import get_error_code
from django.http import response


def read(url_path, vehicle_data):
    # filter 조건 없이 하나의 값만 get
    path_list = url_path.split("/")
    response_data = {}

    error_data = get_error_code("invalid_path")
    try:
        for path in path_list:
            vehicle_data = vehicle_data[path]
            # access sub-directory
            # views.py로부터 전달받은 data를 이용해서 하위 directory로 반복해서 끝단까지 접근
        temp_data = {
            "path": url_path,
            "dp": {
                "value": vehicle_data[0]['value'],
                "ts": vehicle_data[0]['ts']
            }
        }
        response_data['data'] = temp_data
        #response 형식을 맞추기 위해 response_data['data']에 temp_data를 넣어주기 
    except:
        #fail to access sub-directory
        response_data = error_data
        return response_data
    return response_data


def search_read(url_path, vehicle_data, op_value = None):
    # sub directory search (애초에 request에서 중간 level까지 주고 + filter로 하위 path를 전달 (single 값이 아닌 경우도 O)
    op_value_list = []
    # op_value가 여러개의 값으로 들어올 수 있음
    if type(op_value) is str:
        op_value_list.append(op_value)
    elif type(op_value) is list:
        op_value_list = op_value
    else:
        op_value_list = [None]

    final_response_data = []
    for i in op_value_list:
        # 각 단일 경로를 만들어주고, 해당 경로에 대해서 search를 실행
        op_value = i
        if op_value != None: 
            search_url_path = url_path + "/" + op_value
            # 실제로 접근해야할 path를 만들어주기 (기존 path + op_value로 들어온 하위 path)
        else:
            search_url_path = url_path
        # print(search_url_path) #make full url path ex. /Vehicle/Cabin/Door/*/*/IsOpen
        path_list = search_url_path.split("/") # 합쳐진 url path를 / 기준으로 잘라서 각 level에 접근할 수 있도록 list화 하기
        data_path = []
        response_data = [] # wildcard yes -> mutiple return value -> list
        if check_wildcard(search_url_path):
            search_read_type = 'wildcard'
        else:
            search_read_type = 'no_wildcard'
        recursive_read(vehicle_data, path_list, data_path, response_data, search_read_type)

        if not bool(response_data):
            #wildcard -> data in list
            #response_data["data"] list가 비어있을 때 == 아무것도 반환하지 않음 => ERROR
            #final_response_data = error_data
            error_data = get_error_code("invalid_path")

            return error_data

        else:
            for j in response_data:
                for k in final_response_data:
                    if k['path'] == j['path']:
                        break
                else:
                    final_response_data.append(j)
                    # 이번 단일 경로에 접근해서 얻어온 값을 final_response_data에 append
                    # 다음 op_value_list에 있는 값으로 다음 path를 만들어서 search해야함 -> append를 한 것임


    if len(final_response_data) >= 2:
        final_response_data = {'data' : final_response_data}
    else:
        print(final_response_data)
        final_response_data = {'data' : final_response_data[0]}

    return final_response_data


def check_wildcard(op_value):
    for path in op_value.split("/"):
        if path == "*":
            return True
    return False

# last path?
# -> No -> add data_path_copy, pop path_list_copy, pass sub directory data and path_list[0](which is not poped)
# -> Yes -> check if last path is in given data 

# -> No -> return 
# -> Yes -> check if last path if leaf node = if given data is list type
#           -> Yes -> make data and append(wildcard) or insert(no wildcard) data
#           -> No  -> append last path to data_path and call recursive_branch_read

def recursive_read(vehicle_data, path_list, data_path, response_data, search_read_type):
    
    path_list_copy = copy.deepcopy(path_list)
    if len(path_list_copy) != 1:
        # last level이 아닐 때
        if path_list_copy[0] != "*": #not wildcard
            # data path : empty at first 
            data_path_copy = copy.deepcopy(data_path)
            data_path_copy.append(path_list_copy[0]) # poped path is added to data_path_copy
            path_list_copy.pop(0) #remove from front
            
            try:
                tmp=vehicle_data[path_list[0]]
                recursive_read(vehicle_data[path_list[0]], path_list_copy, data_path_copy, response_data, search_read_type)
            except:
                print("no path")

            # recursive_read(vehicle_data[path_list[0]], path_list_copy,data_path_copy, response_data, search_read_type)
            # path_list_copy에서 pop, path_list에서는 pop안함 -> path_list[0]를 vehicle_data 인자로 전달 
            # pop한 path_list_copy를 다음 recursive_read의 path_list로 전달. 
        else: # with wildcard
            path_list_copy.pop(0) #일단 wildcard pop
            for path in vehicle_data: #passed vehicle data(decreased hierarchy level)
                data_path_copy = copy.deepcopy(data_path)
                data_path_copy.append(path) # 와일드카드가 있던 level의 모든 항목을 돌면서 recursive read하기 
                recursive_read(vehicle_data[path], path_list_copy, data_path_copy, response_data, search_read_type)
    else: #len(path_list_copy) == 1 : last level

        if path_list[0] in vehicle_data:
            #if path_list[0] in vehicle_data: => Left 아래에는 IsOpen있지만, LeftCount 아래에는 IsOpen 없음
            if type(vehicle_data[path_list[0]]) == list:
                # list type means last path is leaf node
                last_path = path_list[0]
                data_path = "/".join(data_path) # list to string data path
                #Vehicle/Cabin/Door/Row1/Left
                data_path = data_path + "/" + last_path #last path = IsOpen
                # Vehicle/Cabin/Door/Row1/Left/IsOpen
                # add last path to data path

                temp_data = {
                    "path": data_path,
                    "dp": {
                        "value": vehicle_data[last_path][0]['value'],
                        "ts": vehicle_data[last_path][0]['ts']
                        # latest data
                    }
                }
                if search_read_type == 'wildcard':
                    response_data.append(temp_data)
                    print(response_data)
                    # multiple data -> append
                elif search_read_type == 'no_wildcard':
                    response_data.append(temp_data)
                    print(response_data)
                    # single data
            else: # branch
                #전달받은 path의 마지막 값인데, leaf node가 아닌 경우 
                data_path.append(path_list[0])

                if search_read_type == 'wildcard':
                    branch_data = response_data
                elif search_read_type == 'no_wildcard':
                    branch_data = response_data
                    # not deep copy -> recursive_branch_read에서 branch_data에 저장해도 response_data가 바뀐다.
                    # branch_data = []


                recursive_branch_read(vehicle_data[path_list[0]], data_path, branch_data)
                    # pass 
                    # vehicle_data[Row1] -> Left, LeftCount, Right, RightCount
                    # 지금까지 data_path

                    #recursive_branch_read에서 모든 하위 data append 


def recursive_branch_read(vehicle_data, data_path, branch_data):
    for path in vehicle_data:
        # 해당 level아래 있는 모든 값에 대해서 loop
        data_path_copy = copy.deepcopy(data_path)
        data_path_copy.append(path)
        #if 'value' in vehicle_data[path]:
        if type(vehicle_data[path]) == list: #leaf
            data_path_copy = "/".join(data_path_copy)
            temp_data = {
                "path": data_path_copy,
                "dp": {
                    "value": vehicle_data[path][0]['value'],
                    "ts": vehicle_data[path][0]['ts']
                }
            }
            branch_data.append(temp_data) # given branch data에 계속 추가 
            
        else: # until branch
            recursive_branch_read(vehicle_data[path], data_path_copy, branch_data)


def history_read(url_path, vehicle_data, op_value):
    # ISO 8601 Durations Format
    # PnYnMnDTnHnMnS
    # PnW
    # P<date>T<time>
    # i.e, "op-value": "PdddDThhHmmMssS"
    period = get_time_for_op_value(op_value)
    request_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    request_time = datetime.strptime(request_time, "%Y-%m-%dT%H:%M:%SZ")

    error_data = get_error_code("invalid_path")

    # request_time : 현재 시간(request_time) - 요청 시간(period)
    for key in period:
        if key == "days_ago":
            request_time = request_time - timedelta(days=period[key])
        elif key == "hours_ago":
            request_time = request_time - timedelta(hours=period[key])
        elif key == "minutes_ago":
            request_time = request_time - timedelta(minutes=period[key])
        elif key == "second_ago":
            request_time = request_time - timedelta(seconds=period[key])

    path_list = url_path.split("/")

    for path in path_list:
        try:
            vehicle_data = vehicle_data[path]
            #access sub-directory
        except:
            #fail to access sub-directory
            response_data = error_data
            return response_data

    response_data = {
        'data': {
            'path': url_path,
            'dp': []
        }
    }
    for index, data in enumerate(vehicle_data):
        if index == 0:
            continue
        else:
            if datetime.strptime(data['ts'], "%Y-%m-%dT%H:%M:%SZ") > request_time:
                # 계산된 request_time 이후에 나온 data들 append
                response_data['data']['dp'].append(data)
                #data만 append, path는 동일 

    return response_data


def get_time_for_op_value(op_value):
    period = {}
    op_value = op_value.split("P")[1]

    if len(op_value.split("D")) != 1:
        #day value exists
        period['days_ago'] = int(op_value.split("D")[0])
        op_value = op_value.split("D")[1]
        #rest part
    if len(op_value.split("T")) != 1:
        op_value = op_value.split("T")[1]
        if len(op_value.split("H")) != 1:
            period['hours_ago'] = int(op_value.split("H")[0])
            op_value = op_value.split("H")[1]
        if len(op_value.split("M")) != 1:
            period['minutes_ago'] = int(op_value.split("M")[0])
            op_value = op_value.split("M")[1]
        if len(op_value.split("S")) != 1:
            period['second_ago'] = int(op_value.split("S")[0])
            op_value = op_value.split("S")[1]
    # for key in period:
    #     print("{0}: {1}".format(key, period[key]))
    return period


def service_discovery_read(url_path, vss_json_file, op_value):

    error_data = get_error_code("invalid_path")

    if op_value == '':
        path_list = url_path.split("/")
        for path in path_list:
            if 'children' in vss_json_file:
                # print("vss_json_file1")
                try:
                    vss_json_file=vss_json_file['children']
                except:
                    response_data=error_data
                    return response_data

            try:
                vss_json_file = vss_json_file[path]
            except:
                response_data=error_data
                return response_data
    elif op_value == 'dynamic':
        return get_error_code("not_yet_dev")
    else:
        return get_error_code("filter_invalid")

    response_data = {
        'metadata': vss_json_file,
        'ts': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    return response_data


def update(url_path, vehicle_data, request_data):
    path_list = url_path.split("/")
    error_data = get_error_code("invalid_path")

    response_data = {}
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    temp_vehicle_data = vehicle_data
    # not deep copy
    # for path in path_list:
    #     temp_vehicle_data = temp_vehicle_data[path]

    for path in path_list:
        try:
            temp_vehicle_data = temp_vehicle_data[path]
            #access sub-directory
        except:
            #fail to access sub-directory
            response_data = error_data
            return response_data

    try:
        float(request_data['value'])
        # update하려는 값이 float인 경우
        try:
            float(temp_vehicle_data[0]['value'])
            # 대체하려는 값도 float -> success
        except:
            # update하려는 값은 float인데, 대체하려는 값이 float이 아님
            return get_error_code("bad_request")
    except:
        # update하려는 값이 float이 아님
        try:
            float(temp_vehicle_data[0]['value'])
            # 대체하려는 값이 float임 -> error
            return get_error_code("bad_request")
        except:
            # 대체하려는 값도 float이 아님 -> success
            pass

    temp_vehicle_data[0]['value'] = request_data['value']
    temp_vehicle_data[0]['ts'] = ts
    
    
    with open('viss/vss_final.json', 'w') as file_final:
        file_final.write(json.dumps(vehicle_data))
        # 덮어쓰기 

    response_data['ts'] = ts

    return response_data
