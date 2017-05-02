import ConfigParser

class ConfigFileParser:
	def __init__(self):
		self.Config = ConfigParser.ConfigParser()

	def ConfigSectionMap(self,section):
	    dict1 = {}
	    options = self.Config.options(section)
	    for option in options:
	        try:
	            dict1[option] = self.Config.get(section, option)
	            if dict1[option] == -1:
	                DebugPrint("skip: %s" % option)
	        except:
	            print("exception on %s!" % option)
	            dict1[option] = None
	    return dict1
	
	def parseConfig(self,Filename):
		self.parseDict = {}	
		self.Config.read(Filename)

		field = self.Config.sections()[0]
		self.parseDict = self.ConfigSectionMap(field)
		
		# return self.parseDict.keys()
				# or
		return self.parseDict

	def getConfig(self,fieldname):
		if self.parseDict.has_key(fieldname):
			return self.parseDict[fieldname]
		else:
			return None


# if __name__ == '__main__':
# 	cf = ConfigFileParser()
# 	retrn  = cf.parseConfig("config.ini")
# 	print retrn
	# retrn = cf.getConfig("databaseurl")
	# print retrn
# NO_OF_WORKFLOWS = ConfigSectionMap("Details")['no_of_workflows']
# SELF_RID  = ConfigSectionMap("Details")['self_rid']
# REGISTRATION_FUNCTION_RID  = ConfigSectionMap("Details")['registration_function_rid']

# print NO_OF_WORKFLOWS,SELF_RID,REGISTRATION_FUNCTION_RID

