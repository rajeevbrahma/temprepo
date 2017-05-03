import os
import sys
import Savoir
import logging
import simplejson as json
from pubnub import Pubnub

parentpath = os.path.dirname(os.getcwd())
sys.path.insert(0,parentpath)
from MultichainPython import Multichainpython
from fileparser import ConfigFileParser


LOG_FILENAME = 'warehouse.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Warehouse:
    def __init__(self,rpcuser,rpcpasswd,rpchost,rpcport,chainname):
        print "Warehouse"
        self.rpcuser = rpcuser
        self.rpcpasswd = rpcpasswd
        self.rpchost = rpchost
        self.rpcport = rpcport
        self.chainname = chainname
        self.mchain = Multichainpython(self.rpcuser,self.rpcpasswd,self.rpchost,self.rpcport,self.chainname)

    def connectTochain(self):       
        return self.mchain.multichainConnect()
    def warehouseAddress(self):
        return self.mchain.accountAddress()
    def assetsubscribe(self,asset):
        self.mchain.subscribeToasset(asset)
    def assetbalances(self):
        assetbalances = self.mchain.gettotalbalances()
        return assetbalances
    def queryassetdetails(self,assetname):
        assetdetails = self.mchain.queryassetsdetails(assetname)
        return assetdetails
    def getburnaddress(self):
        return self.mchain.getburnaddress()     
    def burnasset(self,address,asset_name,asset_qty):
        return self.mchain.sendAsset(address,asset_name,asset_qty)

    def issueWHasset(self): 
        try:
            assetaddress = self.mchain.accountAddress()
            
            self.assetname = "warehousemoney" 
            assetdetails = {"name":self.assetname,"open":True}
            assetquantity = 1000  
            assetunit = 1  
            assetnativeamount =0 
            assetcustomfield = {'assetmetrics':'dollars','owner':'John-Distributor'}
            
            issueWHasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)
            assetdescription = {"assetname":self.assetname,"assetquantity":assetquantity,"assetmetrics":"dollars","assetowner":"John-Distributor"}
            
            message = {"op_return":issueWHasset_return,"assetdescription":assetdescription}
            
            self.assetsubscribe(self.assetname)
            publish_handler({"node":"warehouse","messagecode":"issueasset","messagetype":"resp","message":message})


        except Exception as e:
            print e,"error in issueHWasset"
            message = {"op_return":"error","message":e}
            publish_handler({"node":"warehouse","messagecode":"issueasset","messagetype":"resp","message":message})


    def createExchange(self):
        try:
            # Here asset will be a dictionary ex: {"asset1":1}
            ownasset = {"warehouse-crop":4}
            otherasset = {"retailmoney":50}
            prepare_return = self.mchain.preparelockunspentexchange(ownasset)
            print prepare_return
            if prepare_return != False or prepare_return.has_key("txid"):
                createex_return = self.mchain.createrawExchange(prepare_return["txid"],prepare_return["vout"],otherasset)
                print createex_return
                if type(createex_return) != dict:               

                    message = {"op_return":str(createex_return),"hexblob":str(createex_return)}
                    publish_handler({"node":"warehouse","messagecode":"createexchange","messagetype":"resp","message":message})
                else:
                    message = {"op_return":createex_return,"hexblob":""}
                    publish_handler({"node":"warehouse","messagecode":"createexchange","messagetype":"resp","message":message})                   
            else:
                publish_handler({"node":"warehouse","messagecode":"createexchange","messagetype":"resp","message":""})   
        except Exception as e:
            print e,"error in createExchange"
            publish_handler({"node":"warehouse","messagecode":"createexchange","messagetype":"resp","message":""})       


    def decodeExchange(self,hexBlob):
        # The following will give the details regarding the exchange
        try:    
            ownasset = {"warehousemoney":20}
            otherasset = {"crop":20}

            # --step1 decode the hexblob you got in the createexchange procedure
            decodedtranx =  self.mchain.decoderawExchange(hexBlob)
            if type(decodedtranx) == dict:
                if decodedtranx.has_key("offer") and decodedtranx.has_key("ask"):
                    # --step2
                    # We are locking the asset(ownasset)
                    prepare_return = self.mchain.preparelockunspentexchange(ownasset)
                    print prepare_return
                    if prepare_return != False:                
                        # --step3 
                        # Now we to do the appenexchange operation by giving hexblob and txid and otherasset 
                        append_return = self.mchain.appendrawExchange(hexBlob,prepare_return["txid"],prepare_return["vout"],otherasset)
                        print append_return
                        # -- step 4 
                        # This step is for sending the transaction details to the chain
                        if append_return["complete"] == True:
                            send_return = self.mchain.sendrawTransaction(append_return["hex"])
                            message = {"exchange_details":decodedtranx,"exchange_addedtochain":send_return} 
                    else:
                        message = {"exchange_details":False,"exchange_addedtochain":False} 
                else:
                    message = {"exchange_details":False,"exchange_addedtochain":False} 
            else:
                message = {"exchange_details":False,"exchange_addedtochain":False} 
                
            publish_handler({"node":"warehouse","messagecode":"decodeexchange","messagetype":"resp","message":message})         

        except Exception as e:
            message = {"exchange_details":False,"exchange_addedtochain":False} 
            publish_handler({"node":"warehouse","messagecode":"decodeexchange","messagetype":"resp","message":message})                            

    def convertasset(self):
        try:
            # step 1 get totalbalances
            assetbalances = self.assetbalances()
            assetname = "warehousemoney"
            for i in range(0,len(assetbalances)):
                if assetbalances[i]["name"] != assetname:
                    # if assetbalances[i]["name"] == "crop":
                    self.convertasset_name = assetbalances[i]["name"]
                    self.convertasset_qty = assetbalances[i]["qty"]
                else:
                    message = {"op_return":False,"assetdescription":False,"burnasset_op_return":False}
            # step 2 get details of the asset
            convertasset_details = self.queryassetdetails(self.convertasset_name)
            print convertasset_details
            
            if len(convertasset_details) != 0:
                if convertasset_details[0].has_key("details"):
                    convertedasset_name = "warehouse-crop"
                    assetdetails = {"name":convertedasset_name,"open":True} 
                    assetquantity = 4 
                    assetunit = 1 
                    assetnativeamount = 0
                    assetaddress = self.mchain.accountAddress()
                    assetcustomfield = {"origin":"farmland","owner":"John-Distributor","asset-arrivaldate":'2017-05-07',"asset-departuredate":'2017-05-10',"assetstorageconditions":"Good"}# will be generated based on sensor data, fields will be decided$
                    assetcustomfield.update(convertasset_details[0]["details"]) 
                    issueWHasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)
                    assetdescription = {"assetname":convertedasset_name,"assetquantity":assetquantity,"assetmetrics":"dollars","assetowner":"John-Distributor"}

                    message = {"op_return":issueWHasset_return,"assetdescription":assetdescription}
                    print message
                    self.assetsubscribe(convertedasset_name)
                    # publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})
                else:
                    message = {"op_return":False,"assetdescription":False,"burnasset_op_return":False}

            else:
                message = {"op_return":False,"assetdescription":False,"burnasset_op_return":False}

            if message["op_return"] !=False:    
                # step 3 send the asset to the burn address
                burnaddress = self.getburnaddress()
                if burnaddress != False:
                    burnasset_return = self.burnasset(burnaddress,self.convertasset_name,self.convertasset_qty)
                    message.update({"burnasset_op_return":burnasset_return})
                else:
                    message.update({"burnasset_op_return":burnasset_return})            

            else:
                message = {"op_return":False,"assetdescription":False,"burnasset_op_return":False}
            publish_handler({"node":"warehouse","messagecode":"issueasset","messagetype":"resp","message":message})	    
        except Exception as e:
            print e,"convertassetname" 
            message.update({"error":e})
            publish_handler({"node":"warehouse","messagecode":"convertasset","messagetype":"resp","message":message})            


    def updateassetbalance(self):
        try:
            updateassetbalances_list = []
            assetdescription = {}
            temp_dict = {}
            assetbalances = self.assetbalances()
            assetdetails = []
            print assetbalances
            if assetbalances !=False:    
                for i in range(0,len(assetbalances)):
                    temp_dict.update({assetbalances[i]["name"]:assetbalances[i]["qty"]})
                    assetdetails.append(self.queryassetdetails(assetbalances[i]["name"])[0])
                    
                for j in range(0,len(assetdetails)):
                    assetdescription = {"assetquantity":temp_dict[assetdetails[j]["name"]],
                                "assetname":assetdetails[j]["name"],
                                "assetowner":assetdetails[j]["details"]["owner"],
                                "assetmetrics":assetdetails[j]["details"]["assetmetrics"]}

                    updateassetbalances_list.append(assetdescription)
                print updateassetbalances_list
                message = {"op_return":updateassetbalances_list}
            else:                
                message = {"op_return":"error","message":e}
            
            publish_handler({"node":"warehouse","messagecode":"updateassetbalance","messagetype":"resp","message":message})                        
        except Exception as e:
            message = {"op_return":"error","message":e}
            publish_handler({"node":"warehouse","messagecode":"updateassetbalance","messagetype":"resp","message":message})
                

def pub_Init(): 
    global pubnub
    try:
        pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
        pubnub.subscribe(channels=subchannel, callback=callback,error=error,
        connect=connect, reconnect=reconnect, disconnect=disconnect)    
        return True
    except Exception as pubException:
        logging.error("The pubException is %s %s"%(pubException,type(pubException)))
        return False    

                        

def callback(message,channel):
    try:
        print message
        if message["messagetype"] == "req":
            if message["messagecode"] == "issueasset":
                WH.issueWHasset()
            if message["messagecode"] == "createexchange":
                WH.createExchange()
            if message["messagecode"] == "decodeexchange":
                WH.decodeExchange(message["hexblob"])
            if message["messagecode"] == "convertasset":
                WH.convertasset()
            if message["messagecode"] == "updateassetbalance":
                WH.updateassetbalance()
    except Exception as e:
        logging.error("The callback exception is %s,%s"%(e,type(e)))           
    

def publish_handler(message):

    try:
        pbreturn = pubnub.publish(channel = pubchannel ,message = message,error=error)

    except Exception as error_pbhandler:
        print error_pbhandler

                
def error(message):
    logging.error("ERROR on Pubnub: " + str(message))

def connect(message):
    logging.info("CONNECTED")

def reconnect(message):
    logging.info("RECONNECTED")

def disconnect(message):
    logging.info("DISCONNECTED")
                
if __name__ == '__main__':
    pubnub = None   
    filename = "config.ini"
    cf = ConfigFileParser()     
    cf.parseConfig(filename)

    # PUBNUB KEYS
    pub_key = cf.getConfig("pubkey")
    sub_key = cf.getConfig("subkey")  

    pubchannel = cf.getConfig("pubchannel")
    subchannel = cf.getConfig("subchannel")

    # Multichain  Credentials
    rpcuser= cf.getConfig("rpcuser")
    rpcpasswd=cf.getConfig("rpcpasswd")
    rpchost = cf.getConfig("rpchost")
    rpcport = cf.getConfig("rpcport")
    chainname = cf.getConfig("chainname")

    WH = Warehouse(rpcuser,rpcpasswd,rpchost,rpcport,chainname)
    WH.connectTochain()
    pub_Init()


# def issuemoreasset(self):
    #     try:
    #         assetname = "crop"
    #         assetcustomfield = {"asset-arrivaldate":'2017-05-07',"asset-departuredate":'2017-05-10',"assetstorageconditions":"Good"} 
    #         assetaddress = self.mchain.accountAddress()
    #         issuemoreasset_return = self.mchain.issueMoreAsset(assetaddress,assetname,assetcustomfield)
            
    #         assetdescription = {"assetname":assetname,"assetcustomfield":assetcustomfield}
    #         message = {"op_return":issuemoreasset_return,"assetdescription":assetdescription}
    #         publish_handler({"messagecode":"issuemoreasset","messagetype":"resp","message":message})
        
    #     except Exception as e:
    #         print e,"issuemoreasset error"
    #         message = {"op_return":"error","message":e}
    #         publish_handler({"messagecode":"issuemoreasset","messagetype":"resp","message":message})


# message = {"op_return":assetbalances}   
        # publish_handler({"node":"warehouse","messagecode":"assetbalance","messagetype":"resp","message":message})
        

    # def queryassettranx(self,asset):
    #     assettranx = self.mchain.queryAssetTransactions(asset)
    #     message = {"op_return":assettranx}  
    #     publish_handler({"node":"warehouse","messagecode":"assettranx","messagetype":"resp","message":message})

# message = {"op_return":assetdetails}    
# publish_handler({"node":"warehouse","messagecode":"assetdetails","messagetype":"resp","message":message})
        