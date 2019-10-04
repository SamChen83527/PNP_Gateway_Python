import os

class LookupTableManager():
    reading = ''
    
    def __init__(self):
        pass
    
    def isExist(self, deviceID):
        filePath = '../lookupTable/'+deviceID+'.txt'
        return os.path.isfile(filePath)
    
    def queryLookupTable(self, deviceID):        
        filePath = '../lookupTable/'+deviceID+'.txt'
        record = open(filePath,'r')
        recordString = ''
        for line in record:
            recordString += line
        #print (recordString)        
        record.close()
        return recordString
        
    def updateLookupTable(self, deviceID, data):
        filePath = '../lookupTable/'+deviceID+'.txt'
        record = open(filePath,'w')
        record.write(data)
        
        
        
        
        
        
        
        
        
        
        