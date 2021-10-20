import json
#import copy
import string
import random
import numpy as np
from datetime import datetime, timedelta
import pprint
import time

# DEV FUNCTION NOT USE : grab all data types(string, uint8, int8, etc.) under given json
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

# DEV FUNCTION NOT USE : make simple version of given json
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

# GENERATOR : make random dataset based on next conditions; (datatype, min, max, enum)
def recursive_json_generator(json, ts, granpa, num):
    #json_copy = copy.deepcopy(json)
    json_copy = json
    temp = dict()
    for parent in json_copy:
        child = json_copy[parent]
        if parent in ["children"]:
            return recursive_json_generator(child, ts, granpa, num)
        elif isinstance(child, dict):
            temp[parent] = recursive_json_generator(child, ts, parent, num)
        elif parent in ["datatype"]:
            value_list = []
            min, max, enum = None, None, None 
            for rule in json_copy: # check if rule exist
                if rule in ["min"]:
                    min = json_copy[rule]
                elif rule in ["max"]:
                    max = json_copy[rule]
                elif rule in ["enum"]:
                    enum = json_copy[rule]
                else:
                    continue
            for days_ago in range(0, num):
                if enum is not None:
                    if(min is not None): raise Exception('Unhandled Case')
                    elif(max is not None): raise Exception('Unhandled Case')
                    else: random_data_point = random.choice(enum)
                else:                  
                    if (min is not None) and (max is None): #BRANCH 1: min_O max_X
                        if child == "float":
                            random_data_point = str(np.float32(random.uniform(min, 100)))
                        else:
                            raise Exception('Unhandled Case')
                    elif (min is None) and (max is not None): #BRANCH 2: min_X max_O
                        raise Exception('Unhandled Case')
                    elif (min is not None) and (max is not None): #BRANCH 3: min_O max_O
                        if child == "double":
                            random_data_point = str(np.float64(random.uniform(min, max)))
                        elif child == "float":
                            random_data_point = str(np.float32(random.uniform(min, max)))
                        elif child in ["int8", "int16", "int32", "uint8", "uint16", "uint32"]:
                            random_data_point = random.randrange(min, max)
                        else: raise Exception('Unhandled Case')             
                    else: #BRANCH 4: min_X max_X
                        if child == "boolean":
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
                        #SPECIAL CASE A: List of currently active DTCs formatted according OBD II (SAE-J2012DA_201812) standard ([P|C|B|U]XXXXX )
                        elif child == "string[]":
                            random_data_point = random.choice(['P', 'C', 'B', 'U'])
                            random_data_point += random.choice(['1', '2'])
                            random_data_point += random.choice(['1', '2', '3', '4', '5', '6', '7', '8'])
                            random_data_point += random.choice(string.digits)
                            random_data_point += random.choice(string.digits)
                        #SPECIAL CASE B: Number of seats across each row from the front to the rear
                        elif child == "uint8[]": 
                            random_data_point = []
                            for i in range(random.randrange(1, 7)):
                                random_data_point.append(random.randrange(1, 5))
                            random_data_point = str(random_data_point)
                        else: raise Exception('Unhandled Case')
                temp_ts = (datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
                #print(random_data_point)
                value_list.append({"value": random_data_point, "ts": temp_ts})
            return value_list
        else:
            continue
    return temp

def merge_datasets(json_new, json_old, max_length = 5):
    temp = dict()
    json_new_copy = json_new
    json_old_copy = json_old
    for a in json_new_copy:
        if isinstance(json_new_copy[a], dict):
            temp[a] = merge_datasets(json_new_copy[a], json_old_copy[a])
            #print(temp[a])
        elif isinstance(json_new_copy[a], list):
            temp[a] = []
            for j in json_new_copy[a]:
                temp[a].append(j)
            for k in json_old_copy[a]:
                temp[a].append(k)
            temp[a] = temp[a][:max_length]
        else:
            continue
    return temp

def genVehicleData():
    with open('viss/vss_release_2.1.json') as file_origin:
        json_file = json.loads(file_origin.read())
        #print(sorted(recursive_get_all_datatype(json_file)))
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        result = recursive_json_generator(json_file, ts, '', 1)
        #pprint.pprint(json_file)
        with open('viss/vss_final.json', 'w') as file_final:
            file_final.write(json.dumps(result))

        while(True):
            time.sleep(1)
            ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            with open('viss/vss_final.json') as generated_data:  # without children directory
                old = json.loads(generated_data.read())
                result = merge_datasets(recursive_json_generator(json_file, ts, '', 1), old, 20)
                with open('viss/vss_final.json', 'w') as file_final:
                    file_final.write(json.dumps(result))
                    # print('Vehicle Data Updated:', ts)
