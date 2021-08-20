import datetime
from viss.websocket_lib import *

async def accept_unsecured(websocket, path):
    sessionId = str(uuid.uuid1()) #mac addr and time based
    clientIp = websocket.remote_address[0]
    print("WS_unsecured: client connected", sessionId, clientIp) #testcode

    while True:
        try:
            data = await websocket.recv(); #wait for client
            dl = json.loads(data)
            response_json = {}
            vehicle_data = read_vehicle_data()

            #spam check start
            try:
                uns_req_hist[clientIp]
            except:
                uns_req_hist[clientIp] = []

            if len(uns_req_hist[clientIp]) >= 1: 
                if ((time.time() - uns_req_hist[clientIp][0]) <= SPAM_TIME) and len(uns_req_hist[clientIp]) == SPAM_COUNT:
                    response_json = get_error_code("too_many_attempts", True) #WEEK POINT: possible hazard
                    final_json = default_response_maker(dl)
                    for key in response_json:
                        final_json[key] = response_json[key]
                    await websocket.send(json.dumps(final_json))
                    continue
                
            uns_req_hist[clientIp].append(time.time()) 
            if len(uns_req_hist[clientIp]) > SPAM_COUNT:
                del uns_req_hist[clientIp][0]

            print(len(uns_req_hist[clientIp]))
            #spam check end

            response_json = get_response_based_on_request(dl, vehicle_data, websocket, sessionId)

            if "Error Code" in response_json:
                response_json = get_error_code(response_json["Error Reason"], True) #WEEK POINT: possible hazard

            final_json = default_response_maker(dl)
            for key in response_json:
                final_json[key] = response_json[key]

            print("WS_unsecured:", sessionId) #testcode
            print(json.dumps(final_json)) #testcode

            await websocket.send(json.dumps(final_json))
        except:
            print("WS_unsecured: client disconnected", sessionId)

            keys = list(working_subscriptionIds.keys())
            print("Subscription terminated:",keys)
            for i in range(len(working_subscriptionIds)):
                key = keys[i]
                if working_subscriptionIds[key] == sessionId:
                    del working_subscriptionIds[key]
            break
