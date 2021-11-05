import datetime
from viss.websocket_lib import *


async def accept_unsecured(websocket, path):
    sessionId = str(uuid.uuid1())  # mac addr and time based
    clientIp = websocket.remote_address[0]  # 현재 연결된 client의 ip address get
    print("WS_unsecured: client connected", sessionId, clientIp)  # testcode

    while True:
        try:
            data = await websocket.recv()  # wait for client
            dl = json.loads(data)
            response_json = {}
            vehicle_data = read_vehicle_data()
            vehicle_metadata = read_vehicle_metadata()

            #spam check start
            try:
                uns_req_hist[clientIp]  # 해당 clientIp의 list가 생성되어있는지 확인
            except:
                # 해당 clientIp가 처음 request를 보내서 list가 선언이 안되어있는 경우
                uns_req_hist[clientIp] = []

            if len(uns_req_hist[clientIp]) >= 1:
                if ((time.time() - uns_req_hist[clientIp][0]) <= SPAM_TIME) and len(uns_req_hist[clientIp]) == SPAM_COUNT:
                    # 가장 오래된 request의 시간과 현재 시간의 차이가 SPAM_TIME보다 작고,
                    # 요청의 개수가 SPAM_COUNT와 같다면, too_many_request error 발생
                    # WEEK POINT: possible hazard
                    response_json = get_error_code("too_many_requests", True)
                    final_json = default_response_maker(dl)
                    for key in response_json:
                        final_json[key] = response_json[key]
                    await websocket.send(json.dumps(final_json))
                    continue

            uns_req_hist[clientIp].append(time.time())
            #특정 clientIp 마다 request history를 time으로 저장
            # SPAM_TIME동안 SPAM_COUNT 개수만큼 request를 보내지 않았다면 append
            if len(uns_req_hist[clientIp]) > SPAM_COUNT:
                # 만약 SPAM_COUNT 개수 이상 들어왔는데, SPAM_TIME 제한에 걸리지 않은 경우, 가장 오래된 data를 삭제함
                del uns_req_hist[clientIp][0]

            print(len(uns_req_hist[clientIp]))
            #spam check end

            response_json = get_response_based_on_request(
                dl, vehicle_data, vehicle_metadata, websocket, sessionId)
            # dl : data from client = request
            print(response_json)
            if "Error Code" in response_json:
                # WEEK POINT: possible hazard
                response_json = get_error_code(
                    response_json["Error Reason"], True)
            final_json = default_response_maker(dl)
            for key in response_json:
                final_json[key] = response_json[key]

            print("WS_unsecured:", sessionId)  # testcode
            print(json.dumps(final_json))  # testcode

            await websocket.send(json.dumps(final_json))
        except:
            print("WS_unsecured: client disconnected", sessionId)

            keys = list(working_subscriptionIds.keys())
            print("Subscription terminated:", keys)
            for i in range(len(working_subscriptionIds)):
                key = keys[i]
                if working_subscriptionIds[key] == sessionId:
                    del working_subscriptionIds[key]
            break
