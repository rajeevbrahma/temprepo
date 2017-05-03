from pubnub import Pubnub

import logging
LOG_FILENAME = 'UI.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def error(message):
        logging.error("ERROR on Pubnub: " + str(message))

def connect(message):
        logging.info("CONNECTED")

def reconnect(message):
    logging.info("RECONNECTED")

def disconnect(message):
     logging.info("DISCONNECTED")
                
                
def pub_Init(): 
        global pubnub
        try:
                pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
                pubnub.subscribe(channels='UI', callback=callback,error=error,
                connect=connect, reconnect=reconnect, disconnect=disconnect)    
                return True
        except Exception as pubException:
                logging.error("The pubException is %s %s"%(pubException,type(pubException)))
                return False    

                        

def callback(message,channel):
	global hexblob
        try:
                if message["messagetype"] == "resp":
                	print message
                  	if message["messagecode"] == "createexchange":
                  		hexblob = message["message"]["hexblob"]
                  	
                
        except Exception as e:
                logging.error("The callback exception is %s,%s"%(e,type(e)))            
                logging.info(message)


def publish_handler(channel,message):
	try:
	    pbreturn = pubnub.publish(channel = channel ,message = message,error=error)
	    print pbreturn
	except Exception as error_pbhandler:
	    print error_pbhandler


def main():

	while(1):
		inpt = raw_input("CHOOSE ONE OPTION \t\t\t\n1 create farmasset,\n2 create wareasset,\n3 create retailasset , \n4 createexchange - from Farmland,\n5 decodeexchange - in warehouse,\n6 createexchange - from warehouse \n7 decodeexchange - in retailstore \n8 convertasset  \n0 totalbalances\n\n\n\t")
		if(inpt == "1"):
			publish_handler(farmchannel,{"messagecode":"issueasset","messagetype":"req"})
		elif(inpt == "2"):
			publish_handler(warechannel,{"messagecode":"issueasset","messagetype":"req"})

		elif(inpt == "3"):
			publish_handler(retailchannel,{"messagecode":"issueasset","messagetype":"req"})	
		elif(inpt == "4"):
			publish_handler(farmchannel,{"messagetype":"req","messagecode":"createexchange"})
		elif(inpt == "5"):	
			publish_handler(warechannel,{"messagetype":"req","messagecode":"decodeexchange","hexblob":hexblob})
		
		elif(inpt == "6"):
			publish_handler(warechannel,{"messagetype":"req","messagecode":"createexchange"})
		elif(inpt == "7"):	
			publish_handler(retailchannel,{"messagetype":"req","messagecode":"decodeexchange","hexblob":hexblob})
		
		elif(inpt == '8'):
			# publish_handler(warechannel,{"messagecode":"convertasset","messagetype":"req"})
			publish_handler(warechannel,{"messagecode":"issuemoreasset","messagetype":"req"})				
			

		elif(inpt == "0"):
			inpt3 = raw_input("1) farmland  2) warehouse 3) retailstore \n\n\t")
			if inpt3 == "1":
				publish_handler(farmchannel,{"messagetype":"req","messagecode":"assetbalance"})
			if inpt3 == "2":	
				publish_handler(warechannel,{"messagetype":"req","messagecode":"assetbalance"})
			if inpt3 == "3":	
				publish_handler(retailchannel,{"messagetype":"req","messagecode":"assetbalance"})		
		else: 
			pass






if __name__ == '__main__':
	hexblob = None
	farmchannel = "farmland"
	warechannel = "warehouse"
	retailchannel = "retailstore"
	pubnub = None
	# PUBNUB KEYS
	pub_key = 'pub-c-abde89c6-da51-4c04-8c2b-9c3984e1182d'
	sub_key = 'sub-c-d17a927c-e171-11e6-802a-02ee2ddab7fe'
	pub_Init()
	main()




# {"messagecode":"issueasset","messagetype":"req"}
# {"messagetype":"req","messagecode":"createexchange","ownasset":{"crop2":10},"otherasset":{"money1":10}}
# {"messagetype":"req","messagecode":"decodeexchange","hexblob":"01000000010a06695c1d3e06ea446e6d3a529ff331ef4276b7f8561e95c72b27ba4caebdb6000000006a473044022066f205cc98533144581439cdd2cd6caa1c9cfae42c2876afb1bad22080bf4003022025d83cf6c402f439e2fe05b6656b33105508c894ac5fb4353790a29a6794ccf1832102ba65ca166f6fe4a7f3e29ab82b6212b525e156c357614657919f6f5468d6f618ffffffff0100000000000000003776a9140561864a77ef56faa1742ed2c982ca3654b82e2488ac1c73706b71cb5a1f9f97c0982e24c1a82b0404b0ad0a000000000000007500000000","ownasset":{"money1":10},"otherasset":{"crop2":10}}

# {"messagecode":"assettranx","messagetype":"req","asset":"crop2"}
# {"messagecode":"assetdetails","messagetype":"req","asset":"crop2"}



# # {"messagecode":"issueasset","messagetype":"req"}
# # {"messagetype":"req","messagecode":"createexchange","asset":{"money1":50}}
# # {"messagetype":"req","messagecode":"decodeexchange","hexblob":,"asset":{"crop1":50}}

# {"messagecode":"assettranx","messagetype":"req","asset":"money1"}
# {"messagecode":"assetdetails","messagetype":"req","asset":"money1"}
