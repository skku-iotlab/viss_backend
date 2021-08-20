from viss.websocket_lib import *

async def accept_unsecured(websocket, path):
    sessionId = str(uuid.uuid1()) #mac addr and time based
    print("WS_unsecured: client connected", sessionId) #testcode

    while True:
        # try:
        data = await websocket.recv(); #wait for client

        dl = json.loads(data)
        response_json = {}
        vehicle_data = read_vehicle_data()

        print('A') #testcode

        response_json = get_response_based_on_request(dl, vehicle_data, websocket, sessionId)

        if "Error Code" in response_json:
            response_json = get_error_code(response_json["Error Reason"], True) #WEEK POINT: possible hazard

        final_json = default_response_maker(dl)
        for key in response_json:
            final_json[key] = response_json[key]

        print("WS_unsecured:", sessionId) #testcode
        print(json.dumps(final_json)) #testcode

        await websocket.send(json.dumps(final_json))
        # except:
        #     print("WS_unsecured: client disconnected", sessionId)

        #     keys = list(working_subscriptionIds.keys())
        #     print(keys)
        #     for i in range(len(working_subscriptionIds)):
        #         key = keys[i]
        #         if working_subscriptionIds[key] == sessionId:
        #             del working_subscriptionIds[key]
        #     break
