from LookupTableManager import*

print (LookupTableManager().isExist('device132'))

LookupTableManager().updateLookupTable('device132', "Damn you")
print (LookupTableManager().queryLookupTable('device132'))