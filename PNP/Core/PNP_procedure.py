import json
from LookupTableManager_module import LookupTableManager
from HTTPManager_module import HTTPManager
from SerialPortManager_module import SerialPortManager

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

        elif self.operation == "UpdateStatus":
            self.doUpdateStatus()

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
                messageBody = "{\"result\":" + str(result) + "}"

                httpmanager = HTTPManager(self.service_url)
                httpmanager.sendPOST(target, messageBody)

            # Send Confirm
            confirm = '''{"operation": "Confirm","device_ID": "''' + self.device_ID + '''"}'''
            print (confirm)
            serialportmanager = SerialPortManager()
            sendservurl = serialportmanager.sendRequ(confirm)
        else:
            print ("Device doesn't exist.")
            self.doSendServURL()



    def doSendServURL(self):
        getservurl = '''{"operation": "GetServURL","device_ID": "''' + self.device_ID + '''"}'''
        print (getservurl)
        
        # # ask service url from device
        serialportmanager = SerialPortManager()
        sendservurl = serialportmanager.sendRequ(getservurl)

        # TO-DO: varify reponse in SerialPortManager or doSendServURL?

        # Simulated response
        # sendservurl = '''
        #     {
        #         "operation": "SendServURL",
        #         "device_ID": "MY_DEVICE00023",
        #         "service_URL": "http://140.115.110.69:8080/sta_taskingservice/STA/v1.0"
        #     }
        # '''

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
            # TO-DO: doSendDesc()
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
                messageBody = "{\"result\":" + str(result) + "}"

                httpmanager = HTTPManager(self.service_url)
                httpmanager.sendPOST(target, messageBody)

            # Send Confirm
            confirm = '''{"operation": "Confirm","device_ID": "''' + self.device_ID + '''"}'''
            print (confirm)
            serialportmanager = SerialPortManager()
            sendservurl = serialportmanager.sendRequ(confirm)

    def doUpdateStatus(self):
        #   UpdateStatus request:
        #
        #   {
        #       "operation":"UpdateStatus",
        #       "device_ID":"MY_DEVICE00023"
        #   }

        # Query lookup table
        queryer = LookupTableManager()
        if queryer.isExist(self.device_ID):
            print ("Device exists:")
            
            record = json.loads(queryer.queryLookupTable(self.device_ID))
            print (record)
            print ('\n')
            #   Lookup table record:
            #
            #   {
            #       "device_ID":"MY_DEVICE00023",
            #       "Thing_ID":"6",
            #       "Datastream_id_list": {},
            #       "TaskingCapability_parameter_list": {
            #           
            #       },
            #       "service_URL": "140.115.110.69:8080/SensorThingsAPIPart2/v1.0"
            #   }
            self.service_url = record["service_URL"]
            
            
            if ('TaskingCapability_parameter_list' in record):
                # TO-DO
                pass
            else:
                # TO-DO
                pass
            
            
        else not queryer.isExist(self.device_ID):
            print ("Device doesn't exists:")
            
            getservurlanddesc = '''{"operation": "GetServURLandDesc","device_ID": "''' + self.device_ID + '''"}'''
            print (getservurlanddesc)
            
            # # ask service url from device
            serialportmanager = SerialPortManager()
            sendservurlanddesc = serialportmanager.sendRequ(getservurlanddesc)
            
            # Parse response
            sendservurlanddesc_jsonobject = json.loads(sendservurlanddesc)
            self.service_url = sendservurl_jsonobject["service_URL"]
            self.msg_body = sendservurl_jsonobject["msg_body"]

            # Send HTTP GET to query device from SensorThings API
            get_thing = self.service_url + "/Things?$filter=properties/UID%20eq%20%27" + self.device_ID + "%27&$select=id&$expand=Datastreams($select=id,name;$count=true),TaskingCapabilities($select=id,name;$count=true)&$count=true"
                        
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
            #               "TaskingCapabilities": [
            #                   {
            #                       "name": "Hue",
            #                       "@iot.id": 133
            #                   }
            #               ],
            #               "TaskingCapabilities@iot.count": 1,
            #               "@iot.id": 6
            #           }
            #       ]
            #   }
            
            thing_number = get_thing_from_sta_jsonbject["@iot.count"];
            if thing_number == 0:
                print('Device ' + self.device_ID + " doesn't exist in service")
                # TO-DO:
                # 1. Ceate Thing/Datastreams/TaskingCapabilities
                # 2. Update lookup table
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
                # taskingcapabilities dict
                taskingcapabilities_from_sta = thing_from_sta["TaskingCapabilities"]
                taskingcapabilities_number = thing_from_sta['TaskingCapabilities@iot.count']

                descriptionfile = json.loads(self.msg_body)
                
                # Lookup table record:
                #
                #   {
                #       "device_ID":"MY_DEVICE00023",
                #       "Thing_ID":"6",
                #       "service_URL": "140.115.110.69:8080/SensorThingsAPIPart2/v1.0",
                #       "Datastream_id_list": {},
                #       "TaskingCapability_parameter_list": {
                #             "buzzer": {
                #                 "taskingParameters": {
                #                     "field": [
                #                         {
                #                             "name": "buzz_time",
                #                             "use": "Mandatory",
                #                             "description": "ring buzzer several times",
                #                             "definition": {
                #                                 "unitOfMeasurement": "times",
                #                                 "allowedValues": [
                #                                     {
                #                                         "Min": 1,
                #                                         "Max": 10
                #                                     }
                #                                 ],
                #                                 "inputType": "Integer"
                #                             }
                #                         }
                #                     ]
                #                 },
                #                 "zigbeeProtocol": {
                #                     "messageBody": "TaskingDevice_1003003:buzzer:{buzz_time}",
                #                     "addressingSH": "",
                #                     "messageDataType": "application/text",
                #                     "addressingSL": ""
                #                  },
                #             "TCID": 174
                #         }
                #   }
                
                lookuptable_dict = {}
                lookuptable_dict['device_ID'] = self.device_ID
                lookuptable_dict['Thing_ID'] = thing_id_from_sta
                lookuptable_dict['service_URL'] = self.service_url
                
                datastream_id_list = {}
                for datstream_count in range(datastreams_number):
                    datastream_name = datastreams_from_sta[datstream_count]["name"]
                    datastream_id = datastreams_from_sta[datstream_count]["@iot.id"]
                    datastream_id_list[datastream_name] = datastream_id
                    
                taskingcapability_parameter_list = {}
                # for each taskingcapability from SensorThings API GET
                for taskingcapability_count in range(taskingcapabilities_number):
                    taskingcapability_name = taskingcapabilities_from_sta[taskingcapability_count]["name"]
                    taskingcapability_id = taskingcapabilities_from_sta[taskingcapability_count]["@iot.id"]
                    
                    # for each taskingcapability from description file
                    # match the parameter name
                    http_messagebody = ''
                    for taskingcapabilities_from_descriptionfile in descriptionfile["TaskingCapabilities"]:
                        # if match then PATCH
                        if taskingcapabilities_from_descriptionfile['name'] == taskingcapability_name:
                            taskingParameters = taskingcapabilities_from_descriptionfile['taskingParameters']
                            if 'zigbeeProtocol' in taskingcapabilities_from_descriptionfile:
                                protocol = taskingcapabilities_from_descriptionfile['zigbeeProtocol']
                            for parameter_count in range(len(taskingParameters['field'])):
                                parameter = taskingParameters['field'][parameter_count]
                                http_messagebody = http_messagebody + '"' + parameter['name'] + '":{' + parameter['name'] + '}'
                                if parameter_count<len(taskingParameters['field'])-1:
                                    http_messagebody = http_messagebody + ','
                            http_messagebody = '{' + http_messagebody + '"TaskingCapability_name":"' + taskingcapability_name + '","device_ID":"' + self.device_ID + '"}'
                            print ('http_messagebody: ' + http_messagebody)
                            
                            # PATCH
                            #     {
                            #         "httpProtocol":
                            #             {
                            #                 "httpMethod":"POST",
                            #                 "absoluteResourcePath": "<gatewayurl>",
                            #                 "contentType":"application/json",
                            #                 "messageBody":"<http_messagebody>"
                            #             }                            #         
                            #     }
                            
                            # TO-DO: gateway_url
                            patch_content = {'httpProtocol':'POST','absoluteResourcePath':gateway_url, 'contentType':'application/json', 'messageBody':http_messagebody}
                            
                            
                    taskingcapability_parameter_list[taskingcapability_name] = {'taskingParameters':taskingParameters, 'zigbeeProtocol':protocol, 'TCID':taskingcapability_id}
                    
                lookuptable_dict["Datastream_id_list"] = datastream_id_list
                lookuptable_dict["TaskingCapability_parameter_list"] = taskingcapability_parameter_list
                
                # Update lookup table                
                lookuptable_jsonstring = json.dumps(lookuptable_dict)
                print(lookuptable_jsonstring)
                LookupTableManager().updateLookupTable(self.device_ID, lookuptable_jsonstring)
                
                # Send Confirm
                confirm = '''{"operation": "Confirm","device_ID": "''' + self.device_ID + '''"}'''
                print (confirm)            
                serialportmanager = SerialPortManager()
                sendservurl = serialportmanager.sendRequ(confirm)
                
                
                
                
                    

    












#    def doSendDesc(self):
#             
#             
#             
#    def doSendServURLandDesc(self):