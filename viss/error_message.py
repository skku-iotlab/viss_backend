def get_error_code(reason):
    if reason == "not_modified":
        return {"error":{
        "Error Code":"304 (Not Modified)",
        "Error Reason" : "not_modified",
        "Error Message": "No changes have been made by the server."
        }}

    if reason == "bad_request":
        return {"error":{
        "Error Code":"400 (Bad Request)",
        "Error Reason" : "bad_request",
        "Error Message": "The server is unable to fulfil the client request because the request is malformed."
        }}

    if reason == "filter_invalid":
        return {"error":{
        "Error Code":"400 (Bad Request)",
        "Error Reason" : "filter_invalid",
        "Error Message": "Filter requested on non-primitive type."
        }}

    if reason == "token_expired":
        return {"error":{
        "Error Code":"401 (Unauthorized)",
        "Error Reason" : "token_expired",
        "Error Message": "Access token has expired."
        }}        

    if reason == "token_invalid":
        return {"error":{
        "Error Code":"401 (Unauthorized)",
        "Error Reason" : "token_invalid",
        "Error Message": "Access token is invalid."
        }}

    if reason == "token_missing":
        return {"error":{
        "Error Code":"401 (Unauthorized)",
        "Error Reason" : "token_missing",
        "Error Message": "Access token is missing."
        }}

    if reason == "too_many_attempts":
        return {"error":{
        "Error Code":"401 (Unauthorized)",
        "Error Reason" : "too_many_attempts",
        "Error Message": "The client has failed to authenticate too many times."
        }}

    if reason == "read_only":
        return {"error":{
        "Error Code":"401 (Unauthorized)",
        "Error Reason" : "read_only",
        "Error Message": "The desired signal cannot be set since it is a read only signal."
        }}

    if reason == "user_forbidden":
        return {"error":{
        "Error Code":"403 (Forbidden)",
        "Error Reason" : "user_forbidden",
        "Error Message": "The user is not permitted to access the requested resource. Retrying does not help."
        }}

    if reason == "user_unknown":
        return {"error":{
        "Error Code":"403 (Forbidden)",
        "Error Reason" : "user_unknown",
        "Error Message": "The user is unknown. Retrying does not help."
        }}

    if reason == "device_forbidden":
        return {"error":{
        "Error Code":"403 (Forbidden)",
        "Error Reason" : "device_forbidden",
        "Error Message": "The device is not permitted to access the requested resource. Retrying does not help."
        }}

    if reason == "device_unknown":
        return {"error":{
        "Error Code":"403 (Forbidden)",
        "Error Reason" : "device_unknown",
        "Error Message": "The device is unknown. Retrying does not help."
        }}

    if reason == "invalid_path":
        return {"error":{
        "Error Code":"404 (Not Found)",
        "Error Reason" : "invalid_path",
        "Error Message": "The specified data path does not exist."
        }}

    if reason == "private_path":
        return {"error":{
        "Error Code":"404 (Not Found)",
        "Error Reason" : "private_path",
        "Error Message": "The specified data path is private and the request is not authorized to access signals on this path."
        }}

    if reason == "invalid_subscriptionId":
        return {"error":{
        "Error Code":"404 (Not Found)",
        "Error Reason" : "invalid_subscriptionId",
        "Error Message": "The specified subscription was not found."
        }}

    if reason == "insufficient_priviledges":
        return {"error":{
        "Error Code":"406 (Not Acceptable)",
        "Error Reason" : "insufficient_priviledges",
        "Error Message": "The priviledges represented by the access token are not sufficient."
        }}

    if reason == "not_acceptable":
        return {"error":{
        "Error Code":"406 (Not Acceptable)",
        "Error Reason" : "not_acceptable",
        "Error Message": "The server is unable to generate content that is acceptable to the client."
        }}

    if reason == "too_many_requests":
        return {"error":{
        "Error Code":"429 (Too Many Requests)",
        "Error Reason" : "too_many_requests",
        "Error Message": "The client has sent the server too many requests in a given amount of time."
        }}

    if reason == "bad_gateway":
        return {"error":{
        "Error Code":"502 (Bad Gateway)",
        "Error Reason" : "bad_gateway",
        "Error Message": "The server was acting as a gateway or proxy and received an invalid response from an upstream server."
        }}

    if reason == "service_unavailable":
        return {"error":{
        "Error Code":"503 (Service Unavailable)",
        "Error Reason" : "service_unavailable",
        "Error Message": "The server is currently unable to handle the request due to a temporary overload or scheduled maintenance (which may be alleviated after some delay)."
        }}

    if reason == "gateway_timeout":
        return {"error":{
        "Error Code":"504 (Gateway Timeout)",
        "Error Reason" : "gateway_timeout",
        "Error Message": "The server did not receive a timely response from an upstream server it needed to access in order to complete the request."
        }}        

#print(get_error_code("user_unknown"))