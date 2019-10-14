import os
import json

class ServerConfigManager():
    
    def __init__(self):
        pass
    
    def getGatewayURL(self):        
        filePath = '../ServerConfig/serverConfig.json'
        record = open(filePath,'r')
        recordString = ''
        for line in record:
            recordString += line
        record.close()
        
        reading_jsonobject = json.loads(recordString)
        return reading_jsonobject['gateway_url']