import copy
from datetime import datetime, timedelta
import random
import json
from types import resolve_bases

from django.http import response


def read(url_path, vehicle_data):
    path_list = url_path.split("/")
    response_data = {}

    error_data = {
        "Error Code":"404 (Not Found)",
        "Error Reason" : "invalid_path",
        "message": "The specified data path does not exist."
    }
    
    for path in path_list:
        try:
            vehicle_data = vehicle_data[path]
            #access sub-directory
        except:
            #fail to access sub-directory
            response_data = error_data
            return response_data
     
    temp_data = {
        "path": url_path,
        "dp": {
            "value": vehicle_data[0]['value'],
            "ts": vehicle_data[0]['ts']
        }
    }
    response_data['data'] = temp_data

    return response_data


def search_read(url_path, vehicle_data, op_value = None):
    # sub directory search
    op_value_list = []
    if type(op_value) is str:
        op_value_list.append(op_value)
        # print("op-value is str")
    elif type(op_value) is list:
        op_value_list = op_value
        # print("op-value is list")
    else:
        op_value_list = [None]

    final_response_data = []
    print('out')
    for i in op_value_list:
        print('in for loop')
        op_value = i
        if op_value != None: 
            search_url_path = url_path + "/" + op_value
        else:
            search_url_path = url_path
        print(search_url_path) #make full url path ex. /Vehicle/Cabin/Door/*/*/IsOpen
        path_list = search_url_path.split("/") # make url path into list to search each level
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
            error_data={
                "path":search_url_path,
                "error":{
                    "Error Code":"404 (Not Found)",
                    "Error Reason" : "invalid_path",
                    "Error Message": "The specified data path does not exist."
                }
            }
            final_response_data.append(error_data)

        else:
            for j in response_data:
                for k in final_response_data:
                    if k['path'] == j['path']:
                        break
                else:
                    final_response_data.append(j)


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
        # last path가 아닐 때
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

            # recursive_read(vehicle_data[path_list[0]], path_list_copy,
            #                data_path_copy, response_data, search_read_type)
            #path_list_copy에서 pop, path_list에서는 pop안함 -> path_list[0]를 vehicle_data 인자로 전달 
        else: # with wildcard
            path_list_copy.pop(0) #일단 wildcard pop
            for path in vehicle_data: #passed vehicle data(decreased hierarchy level)
                data_path_copy = copy.deepcopy(data_path)
                data_path_copy.append(path) # wild card -> add additional paths to search with next hierarchy level 
                recursive_read(vehicle_data[path], path_list_copy, data_path_copy, response_data, search_read_type)
    else: #len(path_list_copy) == 1 : last path

        if path_list[0] in vehicle_data:
            #if 'value' in vehicle_data[path_list[0]]: => Left 아래에는 IsOpen있지만, LeftCount 아래에는 IsOpen 없음
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
                data_path.append(path_list[0])

                if search_read_type == 'wildcard':
                    branch_data = response_data
                elif search_read_type == 'no_wildcard':
                    branch_data = response_data
                    # branch_data = []


                recursive_branch_read(vehicle_data[path_list[0]], data_path, branch_data)
                    # pass 
                    # vehicle_data[Row1] -> Left, LeftCount, Right, RightCount
                    # 지금까지 data_path

                    #recursive_branch_read에 모든 하위 data append 


def recursive_branch_read(vehicle_data, data_path, branch_data):
    for path in vehicle_data:
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

    error_data = {
        "Error Code":"404 (Not Found)",
        "Error Reason" : "invalid_path",
        "message": "The specified data path does not exist."
    }

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

    error_data = {
        "Error Code":"404 (Not Found)",
        "Error Reason" : "invalid_path",
        "message": "The specified data path does not exist."
    }

    if op_value == 'static':
        path_list = url_path.split("/")
        for path in path_list:
            if 'children' in vss_json_file:
                # print("vss_json_file")
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

    response_data = {
        'metadata': vss_json_file,
        'ts': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    return response_data


def update(url_path, vehicle_data, request_data):
    path_list = url_path.split("/")
    error_data={
        "Error Code":"404 (Not Found)",
        "Error Reason" : "invalid_path",
        "message": "The specified data path does not exist."
    }
    response_data = {}
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    temp_vehicle_data = vehicle_data
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

    temp_vehicle_data[0]['value'] = request_data['value']
    temp_vehicle_data[0]['ts'] = ts

    with open('viss/vss_final.json', 'w') as file_final:
        file_final.write(json.dumps(vehicle_data))

    response_data['ts'] = ts

    return response_data
