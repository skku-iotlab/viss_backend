from viss.websocket_lib import *


async def accept(websocket, path):
    sessionId = str(uuid.uuid1())  # mac addr and time based
    clientIp = websocket.remote_address[0]  # 현재 연결된 client의 ip address get
    print("WS_secured: client connected", sessionId, clientIp)  # testcode

    while True:
        try:
            data = await websocket.recv()  # wait for client
            dl = json.loads(data)
            response_json = {}
            vehicle_data = read_vehicle_data()
            vehicle_metadata = read_vehicle_metadata()
            #spam check start
            try:
                # 특정 clientIp 마다 request history를 time으로 저장
                s_req_hist[clientIp]
            except:
                # 해당 clientIp가 처음 request를 보내서 list가 선언이 안되어있는 경우
                s_req_hist[clientIp] = []

            if len(s_req_hist[clientIp]) >= 1:
                if ((time.time() - s_req_hist[clientIp][0]) <= SPAM_TIME) and len(s_req_hist[clientIp]) == SPAM_COUNT:
                    # 가장 오래된 request의 시간과 현재 시간의 차이가 SPAM_TIME보다 작고,
                    # 요청의 개수가 SPAM_COUNT와 같다면, too_many_request error 발생
                    # WEEK POINT: possible hazard
                    response_json = get_error_code("too_many_requests", True)
                    final_json = default_response_maker(dl)
                    for key in response_json:
                        final_json[key] = response_json[key]
                    await websocket.send(json.dumps(final_json))
                    continue

            # SPAM_TIME동안 SPAM_COUNT 개수만큼 request를 보내지 않았다면 append
            s_req_hist[clientIp].append(time.time())
            if len(s_req_hist[clientIp]) > SPAM_COUNT:
                # 만약 SPAM_COUNT 개수 이상 들어왔는데, SPAM_TIME 제한에 걸리지 않은 경우, 가장 오래된 data를 삭제함
                del s_req_hist[clientIp][0]

            print(len(s_req_hist[clientIp]))
            #spam check end

            if is_request_authorized(dl):
                # request에 올바른 token이 들어오면, 들어온 request 처리해줌
                try:
                    body = jwt.decode(
                        dl["authorization"], SIMPLE_JWT['SIGNING_KEY'], SIMPLE_JWT['ALGORITHM'])
                    print(body)
                    response_json = get_response_based_on_request(
                        dl, vehicle_data, vehicle_metadata, websocket, sessionId)
                except jwt.ExpiredSignatureError:
                    response_json = get_error_code("token_expired", True)
                except jwt.InvalidTokenError:
                    #jwt spam check start
                    #위의 too_many_request와 동일하게 SPAM_TIME과 SPAM_COUNT로 판단
                    try:
                        jwt_req_hist[clientIp]
                    except:
                        jwt_req_hist[clientIp] = []

                    if len(jwt_req_hist[clientIp]) >= 1:
                        if ((time.time() - jwt_req_hist[clientIp][0]) <= JWT_SPAM_TIME) and len(jwt_req_hist[clientIp]) == JWT_SPAM_COUNT:
                            # WEEK POINT: possible hazard
                            response_json = get_error_code(
                                "too_many_attempts", True)
                            final_json = default_response_maker(dl)
                            for key in response_json:
                                final_json[key] = response_json[key]
                            await websocket.send(json.dumps(final_json))
                            continue

                    jwt_req_hist[clientIp].append(time.time())
                    if len(jwt_req_hist[clientIp]) > JWT_SPAM_COUNT:
                        del jwt_req_hist[clientIp][0]

                    print(len(jwt_req_hist[clientIp]))
                    #jwt spam check end

                    response_json = get_error_code("token_invalid", True)
                else:
                    #too_many_attempts
                    pass
            else:
                response_json = get_error_code("token_missing")

            if "Error Code" in response_json:
                # WEEK POINT: possible hazard
                response_json = get_error_code(
                    response_json["Error Reason"], True)

            final_json = default_response_maker(dl)
            for key in response_json:
                final_json[key] = response_json[key]

            print("WS_secured:", sessionId)  # testcode
            print(json.dumps(final_json))  # testcode

            await websocket.send(json.dumps(final_json))
        except:
            print("WS_secured: client disconnected", sessionId)

            keys = list(working_subscriptionIds.keys())
            print(keys)
            for i in range(len(working_subscriptionIds)):
                key = keys[i]
                if working_subscriptionIds[key] == sessionId:
                    del working_subscriptionIds[key]
            break
