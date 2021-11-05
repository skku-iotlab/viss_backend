import json
import random
import time

# GENERATOR : make random dataset based on next conditions; (datatype, min, max, enum)
def recursive_json_generator(json):
    #json_copy = copy.deepcopy(json)
    json_copy = json
    temp = dict()
    for parent in json_copy:
        child = json_copy[parent]
        if 'children' in parent:
            return recursive_json_generator(child)
        elif isinstance(child, dict):
            #child.append({"availability": 'availability'})
            temp[parent] = recursive_json_generator(child)
            temp['samplerate'] = random.uniform(0, 100)
            temp['availability'] = random.choice(['available', 'unavailable', 'error'])
            temp['validate'] = random.choice(['read-only', 'read-write'])
        elif 'datatype' in parent:
            dynamic_metadata = {}
            dynamic_metadata['samplerate'] = random.uniform(0, 100)
            dynamic_metadata['availability'] = random.choice(['available', 'unavailable', 'error'])
            dynamic_metadata['validate'] = random.choice(['read-only', 'read-write'])
            return dynamic_metadata
        else:
            continue
    return temp

def genVehicleMetadata():
    while(True):
        time.sleep(1)
        with open('viss/vss_release_2.1.json') as file_origin:
            json_file = json.loads(file_origin.read())
            result = recursive_json_generator(json_file)
            with open('viss/vss_metadata.json', 'w') as file_final:
                file_final.write(json.dumps(result))