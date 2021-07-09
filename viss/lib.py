import copy
from datetime import datetime, timedelta
import random
import json

# def getVehicleData():
#     ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
#     utcnow = datetime.utcnow()
#     data = {
#         'Vehicle' : {
#             'Acceleration': {
#                 'Longitudinal': [
#                     {
#                         'value': random.uniform(0,0.2),
#                         'ts': (utcnow - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
#                     },
#                     {
#                         'value': random.uniform(0,0.2),
#                         'ts': (utcnow - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
#                     },
#                     {
#                         'value': random.uniform(0,0.2),
#                         'ts': (utcnow - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
#                     },
#                     {
#                         'value': random.uniform(0,0.2),
#                         'ts': (utcnow - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
#                     },
#                     {
#                         'value': random.uniform(0,0.2),
#                         'ts': (utcnow - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
#                     },
#                     {
#                         'value': random.uniform(0,0.2),
#                         'ts': ts
#                     }
#                 ]
#             },
#             'AverageSpeed': [
#                 {
#                     'value': random.randrange(0,80),
#                     'ts': ts
#                 }
#             ],
#             'Cabin': {
#                 'Door': {
#                     'Row1': {
#                         'Left': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         },
#                         'Right': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         }
#                     },
#                     'Row2': {
#                         'Left': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         },
#                         'Right': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         }
#                     },
#                     'Row3': {
#                         'Left': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         },
#                         'Right': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         }
#                     },
#                     'Row4': {
#                         'Left': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         },
#                         'Right': {
#                             'IsOpen': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ],
#                             'IsLocked': [
#                                 {
#                                     'value': False,
#                                     'ts': ts
#                                 }
#                             ]
#                         }
#                     }
#                 }
#             },
#             'Speed': [
#                 {
#                     'value': random.randrange(0,80),
#                     'ts': ts
#                 }
#             ]
#         }
#     }
#     return data

def read(url_path, vehicle_data):
    path_list = url_path.split("/")
    response_data = {}
    for path in path_list:
        vehicle_data = vehicle_data[path]
    temp_data = {
        "path":url_path,
        "dp":{
            "value":vehicle_data[0]['value'],
            "ts":vehicle_data[0]['ts']
        } 
    }
    response_data['data'] = temp_data

    return response_data

def search_read(url_path, vehicle_data, op_value):
    url_path = url_path + "/" + op_value
    path_list = url_path.split("/")
    data_path = []
    if check_wildcard(op_value):
        response_data = {
            'data': []
        }
        search_read_type = 'wildcard'
        recursive_read(vehicle_data, path_list, data_path, response_data, search_read_type)
    else:
        search_read_type = 'no_wildcard'
        response_data = {}
        recursive_read(vehicle_data, path_list, data_path, response_data, search_read_type)
    return response_data

def check_wildcard(op_value):
    for path in op_value.split("/"):
        if path == "*":
            return True
    return False

def recursive_read(vehicle_data, path_list, data_path, response_data, search_read_type):
    path_list_copy = copy.deepcopy(path_list)
    if len(path_list_copy) != 1:
        if path_list_copy[0] != "*":
            data_path_copy = copy.deepcopy(data_path)
            data_path_copy.append(path_list_copy[0])
            path_list_copy.pop(0)
            recursive_read(vehicle_data[path_list[0]], path_list_copy, data_path_copy, response_data, search_read_type)
        else:
            path_list_copy.pop(0)
            for path in vehicle_data:
                data_path_copy = copy.deepcopy(data_path)
                data_path_copy.append(path)
                recursive_read(vehicle_data[path], path_list_copy, data_path_copy, response_data, search_read_type)
    else:
        if path_list[0] in vehicle_data:
            #if 'value' in vehicle_data[path_list[0]]:
            if type(vehicle_data[path_list[0]]) == list:
                last_path = path_list[0]
                data_path = "/".join(data_path)
                data_path = data_path + "/" + last_path
                temp_data = {
                    "path":data_path,
                    "dp":{
                        "value":vehicle_data[last_path][0]['value'],
                        "ts":vehicle_data[last_path][0]['ts']
                    } 
                }
                if search_read_type == 'wildcard':
                    response_data['data'].append(temp_data)
                elif search_read_type == 'no_wildcard':
                     response_data['data'] = temp_data
            else:
                data_path.append(path_list[0])
                if search_read_type == 'wildcard':
                    branch_data = response_data
                elif search_read_type == 'no_wildcard':
                    branch_data = response_data
                    branch_data['data'] = []
                recursive_branch_read(vehicle_data[path_list[0]], data_path, branch_data)

def recursive_branch_read(vehicle_data, data_path, branch_data):
    for path in vehicle_data:
        data_path_copy = copy.deepcopy(data_path)
        data_path_copy.append(path)
        #if 'value' in vehicle_data[path]:
        if type(vehicle_data[path]) == list:
            data_path_copy = "/".join(data_path_copy)
            temp_data = {
                "path":data_path_copy,
                "dp":{
                    "value":vehicle_data[path][0]['value'],
                    "ts":vehicle_data[path][0]['ts']
                } 
            }
            branch_data['data'].append(temp_data)
        else:
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
        vehicle_data = vehicle_data[path]

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

    return response_data

def get_time_for_op_value(op_value):
    period = {}
    op_value = op_value.split("P")[1]

    if len(op_value.split("D")) != 1:
        period['days_ago'] = int(op_value.split("D")[0])
        op_value = op_value.split("D")[1]
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
    if op_value == 'static':
        path_list = url_path.split("/")
        for path in path_list:
            if 'children' in vss_json_file:
                vss_json_file = vss_json_file['children']
            vss_json_file = vss_json_file[path]
    
    print(vss_json_file)

    response_data = {
        'metadata': vss_json_file,
        'ts': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    return response_data


def update(url_path, vehicle_data, request_data):
    path_list = url_path.split("/")
    response_data = {}
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    temp_vehicle_data = vehicle_data
    for path in path_list:
        temp_vehicle_data = temp_vehicle_data[path]
    temp_vehicle_data[0]['value'] = request_data['value']
    temp_vehicle_data[0]['ts'] = ts

    with open('viss/vss_final.json', 'w') as file_final:
        file_final.write(json.dumps(vehicle_data))

    response_data['ts'] = ts

    return response_data