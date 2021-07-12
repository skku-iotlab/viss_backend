import random
import json
import copy
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from viss.lib import *
from viss.data_generator import *

# Create your views here.


# VISSv2 & VSSv2.1
@api_view(['GET', 'POST'])
def Vehicle(request):
    #print(vehicle_data)
    with open('viss/vss_final.json') as generated_data:
        vehicle_data = json.loads(generated_data.read())
    query_params = request.query_params.dict()
    url_path = request.path[1:len(request.path)]
    if request.method == 'GET':
        if url_path[len(url_path)-1] == "/":
            url_path = url_path[0:len(url_path)-1]
        if "filter" not in query_params:
            response_data = read(url_path, vehicle_data)
        else:
            query_params = json.loads(query_params["filter"])
            op_type = query_params["op-type"]
            op_value = query_params["op-value"]
            if op_type == 'paths':
                response_data = search_read(url_path, vehicle_data, op_value)
            elif op_type == 'history':
                response_data = history_read(url_path, vehicle_data, op_value)
            elif op_type == 'metadata':
                with open('viss/vss_release_2.1.json') as file_origin:
                    vss_json_file = json.loads(file_origin.read())
                response_data = service_discovery_read(url_path, vss_json_file, op_value)
        print(response_data)
    elif request.method == 'POST':
        if url_path[len(url_path)-1] == "/":
            url_path = url_path[0:len(url_path)-1]
        if "filter" not in query_params:
            response_data = update(url_path, vehicle_data, request.data)
        print(response_data)
    return JsonResponse(response_data)

# VISSv2 & VSSv2.1
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def Vehicle_AverageSpeed(request):
    #print(vehicle_data)
    with open('viss/vss_final.json') as generated_data:
        vehicle_data = json.loads(generated_data.read())
    query_params = request.query_params.dict()
    url_path = request.path[1:len(request.path)]
    if request.method == 'GET':
        if url_path[len(url_path)-1] == "/":
            url_path = url_path[0:len(url_path)-1]
        if "filter" not in query_params:
            response_data = read(url_path, vehicle_data)
        else:
            query_params = json.loads(query_params["filter"])
            op_type = query_params["op-type"]
            op_value = query_params["op-value"]
            if op_type == 'paths':
                response_data = search_read(url_path, vehicle_data, op_value)
            elif op_type == 'history':
                response_data = history_read(url_path, vehicle_data, op_value)
            elif op_type == 'metadata':
                with open('viss/vss_release_2.1.json') as file_origin:
                    vss_json_file = json.loads(file_origin.read())
                response_data = service_discovery_read(url_path, vss_json_file, op_value)
        print(response_data)
    elif request.method == 'POST':
        if url_path[len(url_path)-1] == "/":
            url_path = url_path[0:len(url_path)-1]
        if "filter" not in query_params:
            response_data = update(url_path, vehicle_data, request.data)
        print(response_data)
    return JsonResponse(response_data)
