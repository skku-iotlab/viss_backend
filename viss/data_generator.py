import json
#import copy
import string
import random
import numpy as np
from datetime import datetime, timedelta
import pprint

def recursive_get_all_datatype(json):
    #json_copy = copy.deepcopy(json)
    json_copy = json
    temp = set()
    for parent in json_copy:
        child = json_copy[parent]
        if isinstance(child, dict):
            temp = temp | recursive_get_all_datatype(child)
        elif parent in ["datatype"]:
            return set([child])
        else:
            continue
    return temp

def recursive_json_formatter(json, ts):
    #json_copy = copy.deepcopy(json)
    json_copy = json
    temp = dict()
    for parent in json_copy:
        child = json_copy[parent]
        if parent in ["children"]:
            return recursive_json_formatter(child, ts)
        elif isinstance(child, dict):
            temp[parent] = recursive_json_formatter(child, ts)
        elif parent in ["datatype"]:
            return [{"value": child, "ts": ts}]
        else:
            continue
    return temp    

def recursive_json_generator(json, ts, granpa):
    #json_copy = copy.deepcopy(json)
    json_copy = json
    temp = dict()
    for parent in json_copy:
        parent = parent
        child = json_copy[parent]
        if parent in ["children"]:
            return recursive_json_generator(child, ts, granpa)
        elif isinstance(child, dict):
            temp[parent] = recursive_json_generator(child, ts, parent)
        elif parent in ["datatype"]:
            value_list = []
            for days_ago in range(0, 8):
                if child ==  "boolean":
                    random_data_point = random.choice([True, False])
                elif child == "double":
                    random_data_point = str(np.float64(random.random()))
                elif child == "float":
                    random_data_point = str(np.float32(random.random()))
                elif child == "int8":
                    random_data_point = random.randrange(-128, 127)
                elif child == "int16":
                    random_data_point = random.randrange(-32768,32767)
                elif child == "int32":
                    random_data_point = random.randrange(-2147483648, 2147483647)         
                elif child == "uint8":
                    random_data_point = random.randrange(0, 255)
                elif child == "uint16":
                    random_data_point = random.randrange(0, 65535)  
                elif child == "uint32":
                    random_data_point = random.randrange(0, 4294967295)
                elif child == "string":
                    random_data_point = granpa + "_data_random_string_"
                    for i in range(6):
                        random_data_point += random.choice(string.ascii_uppercase)
                #special_case_A: List of currently active DTCs formatted according OBD II (SAE-J2012DA_201812) standard ([P|C|B|U]XXXXX )
                elif child == "string[]":
                    random_data_point = random.choice(['P', 'C', 'B', 'U'])
                    for i in range(5):
                        random_data_point += random.choice(string.ascii_uppercase)
                #special_case_B: Number of seats across each row from the front to the rear
                elif child == "uint8[]": 
                    random_data_point = []
                    for i in range(random.randrange(1, 7)):
                        random_data_point.append(random.randrange(1, 5))
                    random_data_point = str(random_data_point)
                else:
                    pass
                temp_ts = (datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
                value_list.append({"value": random_data_point, "ts": temp_ts})
            return value_list
        else:
            continue
    return temp

def getVehicleData():
    with open('viss/vss_release_2.1.json') as file_origin:
        json_file = json.loads(file_origin.read())

        #print(sorted(recursive_get_all_datatype(json_file)))

        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        json_file = recursive_json_generator(json_file, ts, '')
        #pprint.pprint(json_file)
        #print(json_file)
        with open('viss/vss_final.json', 'w') as file_final:
            file_final.write(json.dumps(json_file))