from PNP.Main.PNP_procedure import PNPRequest

# # Existed device
# UploadObs_req = '''
#     {
#         "operation":"UploadObs",
#         "device_ID":"MY_DEVICE00023",
#         "msg_body":[
#             {
#                 "name":"sensor1",
#                 "observation":"25.10"
#             },
#             {
#                 "name":"sensor2",
#                 "observation":"46.20"
#             }
#         ]
#     }
# '''
#
# PNPRequest(UploadObs_req)

# Non-existed device
UploadObs_req2 = '''
    {
        "operation":"UploadObs",
        "device_ID":"MY_DEVICE00023",
        "msg_body":[
            {
                "name":"Temperature measurement",
                "observation":"25.10"
            },
            {
                "name":"Relative humidity measurement",
                "observation":"46.20"
            }
        ]
    }
'''

PNPRequest(UploadObs_req2)