import json
from LookupTableManager_module import LookupTableManager
from HTTPManager_module import HTTPManager
# from .SerialPortManager_module import SerialPortManager

class PNPRequest():
    def __init__(self, request):
        self.request = json.loads(request)
        self.operation = self.request["operation"]
        self.device_ID = self.request["device_ID"]
        self.msg_body = self.request["msg_body"]
        self.observations = None
        self.service_url = None
        self.doRequest()

    def doRequest(self):
        if self.operation == "UploadObs":
            self.observations = self.request["msg_body"]
            self.doUploadObs()

        # elif self.operation == "UpdateStatus":
        #     self.doUpdateStatus()
        #
        # elif self.operation == "SendServURL":
        #     self.doSendServURL)
        #
        # elif self.operation == "SendDesc":
        #     self.doSendDesc()
        #
        # elif self.operation == "SendServURLandDesc":
        #     self.doSendServURLandDesc()

    def doUploadObs(self):
        #   UploadObs request:
        #
        #   {
        #       "operation":"UploadObs",
        #       "device_ID":"MY_DEVICE00023",
        #       "msg_body":[
        #           {
        #               "name":"sensor1",
        #               "observation":"25.10"
        #           },
        #           {
        #               "name":"sensor2",
        #               "observation":"46.20"
        #           }
        #       ]
        #   }

        # Query lookup table
        queryer = LookupTableManager()
        if queryer.isExist(self.device_ID):
            print ("Device exists:")

            # Upload observations
            record = json.loads(queryer.queryLookupTable(self.device_ID))
            print (record)
            print ('\n')
            #   Lookup table record:
            #
            #   {
            #       "device_ID":"MY_DEVICE00023",
            #       "Thing_ID":"6",
            #       "Datastream_id_list":
            #       {
            #           "sensor1": 6,
            #           "sensor2": 7
            #       },
            #       "service_URL": "140.115.110.69:8080/SensorThingsAPIPart2/v1.0"
            #   }
            self.service_url = record["service_URL"]

            for observation in self.observations:
                # from request observations
                datastream_name = observation["name"]
                result = observation["observation"]
                # from lookup table record
                datastream_id = record["Datastream_id_list"][datastream_name]

                # POST message body
                target = "Datastreams(" + str(datastream_id) + ")/Observations"
                messageBody = "{\"result\":" + result + "}"

                httpmanager = HTTPManager(self.service_url)
                httpmanager.sendPOST(target, messageBody)

            # TO-DO: Send Confirm
        else:
            print ("Device doesn't exist.")
            self.doSendServURL()



    def doSendServURL(self):
        getservurl = '''
            {
                "operation": "GetServURL",
                "device_ID": "''' + self.device_ID + '''"
            }<CR>
        '''

        # To-Do
        # # ask service url from device
        # serialportmanager = SerialPortManager()
        # sendservurl = serialportmanager.sendRequ(GetServURL)

        # TO-DO: varify reponse in SerialPortManager or doSendServURL?

        # Simulated response
        sendservurl = '''
            {
                "operation": "SendServURL",
                "device_ID": "MY_DEVICE00023",
                "service_URL": "http://140.115.110.69:8080/sta_taskingservice/STA/v1.0"
            }
        '''

        # Parse response
        sendservurl_jsonobject = json.loads(sendservurl)
        self.service_url = sendservurl_jsonobject["service_URL"]

        # Send HTTP GET to query device from SensorThings API
        get_thing = self.service_url + "/Things?$filter=properties/UID%20eq%20%27" + self.device_ID + "%27&$select=id&$expand=Datastreams($select=id,name;$count=true)&$count=true"

        httpmanager = HTTPManager(self.service_url)
        get_response = httpmanager.sendGET(get_thing)

        # parse get response
        get_thing_from_sta_jsonbject = json.loads(get_response)

        #   {
        #       "@iot.count": 1,
        #       "value": [
        #           {
        #               "Datastreams": [
        #                   {
        #                       "name": "Relative humidity measurement",
        #                       "@iot.id": 7
        #                   },
        #                   {
        #                       "name": "Temperature measurement",
        #                       "@iot.id": 6
        #                   }
        #               ],
        #               "Datastreams@iot.count": 2,
        #               "@iot.id": 6
        #           }
        #       ]
        #   }

        thing_number = get_thing_from_sta_jsonbject["@iot.count"];
        if thing_number == 0:
            print('Device ' + self.device_ID + " doesn't exist in service")
        else:
            print('Device ' + self.device_ID + " exists in service")

            # NOTE:
            # JSON in Python -
            #   json string -> loads() -> dict
            #   dict -> dumps() -> json string

            # thing dict
            thing_from_sta = get_thing_from_sta_jsonbject["value"][0]
            thing_id_from_sta = thing_from_sta["@iot.id"]
            # datastreams dict
            datastreams_from_sta = thing_from_sta["Datastreams"]
            datastreams_number = thing_from_sta["Datastreams@iot.count"]

            # Update lookup table
            lookuptable_dict = {}
            lookuptable_dict['device_ID'] = self.device_ID
            lookuptable_dict['Thing_ID'] = thing_id_from_sta
            lookuptable_dict['service_URL'] = self.service_url

            datastream_id_list = {}
            for datstream_count in range(datastreams_number):
                datastream_name = datastreams_from_sta[datstream_count]["name"]
                datastream_id = datastreams_from_sta[datstream_count]["@iot.id"]
                datastream_id_list[datastream_name] = datastream_id

            lookuptable_dict["Datastream_id_list"] = datastream_id_list
            lookuptable_jsonstring = json.dumps(lookuptable_dict)

            print(lookuptable_jsonstring)
            LookupTableManager().updateLookupTable(self.device_ID, lookuptable_jsonstring)

            # Upload observations
            for observation in self.observations:
                #   from request observations:
                #   [
                #       {
                #           "name":"sensor1",
                #           "observation":"25.10"
                #       },
                #       {
                #           "name":"sensor2",
                #           "observation":"46.20"
                #       }
                #   ]
                datastream_name_from_request = observation["name"]
                result = observation["observation"]

                #   from Datastream_id_list:
                #   {
                #       "sensor1": 6,
                #       "sensor2": 7
                #   }
                datastream_id = datastream_id_list[datastream_name_from_request]

                # POST message body
                target = "Datastreams(" + str(datastream_id) + ")/Observations"
                messageBody = "{\"result\":" + result + "}"

                httpmanager = HTTPManager(self.service_url)
                httpmanager.sendPOST(target, messageBody)





































#    def doUpdateStatus(self):
#             
#             
#             
#    def doSendServURL(self):
#        
#    
#    
#    def doSendDesc(self):
#             
#             
#             
#    def doSendServURLandDesc(self):