from flask import Flask, request
from LookupTableManager_module import LookupTableManager
from SerialPortManager_module import SerialPortManager
import json

app = Flask(__name__)
@app.route("/task", methods = ["POST"])
def task():
    if request.method == 'POST':
        # Task request:
        # {
        #     "device_ID": "TaskingDevice001",
        #     "TaskingCapability_name": "buzzer",
        #     "buzz_time": 10,
        #     "<para_name>": ...
        # }
        
        # Parse task from STA
        gateway_task = request.get_json()
        device_ID = gateway_task['device_ID']        
        TaskingCapability_name = gateway_task['TaskingCapability_name']

        # Query lookup table
        queryer = LookupTableManager()
        if queryer.isExist(device_ID):
            record = json.loads(queryer.queryLookupTable(device_ID))
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
            
            service_URL = record["service_URL"]
            taskingcapability_parameter_list = record['TaskingCapability_parameter_list']
            
            device_task = ''
            # Translate gateway task to device task
            for taskingcapability_name in taskingcapability_parameter_list:
                if 'zigbeeProtocol' in taskingcapability_parameter_list[taskingcapability_name]:
                    protocol = taskingcapability_parameter_list[taskingcapability_name]['zigbeeProtocol']
                    device_task_template = protocol['messageBody']
                    
                
                parameters = taskingcapability_parameter_list[taskingcapability_name]['taskingParameters']['field']
                for para in parameters:
                    parameter_name = para['name']
                    tasking_value = gateway_task[parameter_name]
                    place_holder = '{' + parameter_name + '}'
                    device_task = device_task_template.replace(place_holder, str(tasking_value))
            
            # Send device task
            serialportmanager = SerialPortManager()
            serialportmanager.sendRequ_withoutResponse(device_task)
            app.logger.info(device_task)
            
            return 'OK'
        
        elif not queryer.isExist(device_ID):
            return 'Device does not exist.'
    
if __name__ == "__main__":
    app.run(host = "192.168.1.200", port = 8484, debug = True)