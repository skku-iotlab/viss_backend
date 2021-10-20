import random
import json
import copy
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse, response

from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from viss.lib import *
from viss.data_generator import *


class UserThrottle(UserRateThrottle):
    rate = '10/m'
# rest API에서 SPAM(too_many_request and too_many_attempts) 처리하는 library
# 1분당 10회

# VISSv2 & VSSv2.1

# authorization이 아닌 경우 실행
@api_view(['GET', 'POST'])
@throttle_classes([UserThrottle]) #SPAM
def Vehicle(request):
    # print("IN VEHICLE")
    with open('viss/vss_final.json') as generated_data:  # without children directory
        vehicle_data = json.loads(generated_data.read())
        # data_generator로 만든 vehicle data -> 추후에 각 함수에 전달
    query_params = request.query_params.dict()

    url_path = request.path[1:len(request.path)]
    if request.method == 'GET':
        if url_path[len(url_path)-1] == "/":  # set url end without slash
            url_path = url_path[0:len(url_path)-1]

        # GET data
        if "filter" not in query_params:  # GET && no filter ex. GET /Vehicle/Speed HTTP/1.1
            # just return single data & no filter
            response_data = read(url_path, vehicle_data)
        else:  # GET && yes filter
            query_params = json.loads(query_params["filter"])
            op_type = query_params["type"]
            op_value = query_params["value"]
            print(op_value)
            print(type(op_value))
            # ###ADDED by JUNE###
            # if "," in op_value:
            #     op_value = op_value.split(',')
            #     print(op_value)
            # ###ADDED by JUNE###

            if op_type == 'paths':
                # paths -> sub directory search
                response_data = search_read(url_path, vehicle_data, op_value)
            elif op_type == 'history':
                # history -> 과거의 값들을 가져오기
                response_data = history_read(url_path, vehicle_data, op_value)
            elif op_type == 'static-metadata':
                # metadata 해당 경로의 metadata를 가져오기
                with open('viss/vss_release_2.1.json') as file_origin:
                    vss_json_file = json.loads(file_origin.read())
                response_data = service_discovery_read(
                    url_path, vss_json_file, op_value)
            else:
                # filter가 paths, history, metadata가 아닌 경우 filter_invalid 에러 
                response_data = get_error_code("filter_invalid")
    elif request.method == 'POST':
        if url_path[len(url_path)-1] == "/":
            url_path = url_path[0:len(url_path)-1]
        if "filter" not in query_params:
            response_data = update(url_path, vehicle_data, request.data)
            
            
    ########AFTER RETURN response_data#########        
    if "error" in response_data:
        # error 반환시, 404 status로 client에 응답
        return JsonResponse(response_data, status=404)
    else:
        # response data에 error없을시, 200 status로 client에 응답
        return JsonResponse(response_data, status=200)

# VISSv2 & VSSv2.1

# authorization이 필요한 경우 실행
@api_view(['GET', 'POST'])
@throttle_classes([UserThrottle]) #SPAM
@permission_classes((IsAuthenticated, ))
def Vehicle_AverageSpeed(request):
    # print("IN VEHICLE_AVRG_SPEED")
    with open('viss/vss_final.json') as generated_data:
        vehicle_data = json.loads(generated_data.read())
    query_params = request.query_params.dict()
    url_path = request.path[1:len(request.path)]
    if url_path[len(url_path)-1] == "/":
        url_path = url_path[0:len(url_path)-1]
    if "filter" not in query_params:
        response_data = read(url_path, vehicle_data)
    else:
        query_params = json.loads(query_params["filter"])
        op_type = query_params["type"]
        op_value = query_params["value"]
        if op_type == 'paths':
            response_data = search_read(url_path, vehicle_data, op_value)
        elif op_type == 'history':
            response_data = history_read(url_path, vehicle_data, op_value)
        elif op_type == 'metadata':
            with open('viss/vss_release_2.1.json') as file_origin:
                vss_json_file = json.loads(file_origin.read())
            response_data = service_discovery_read(
                url_path, vss_json_file, op_value)

    return JsonResponse(response_data)
