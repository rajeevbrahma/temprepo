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
        message = {"op-return":assetbalances}   
        publish_handler({"messagecode":"assetbalance","messagetype":"resp","message":message})

    def queryassettranx(self,asset):
        assettranx = self.mchain.queryAssetTransactions(asset)
        message = {"op-return":assettranx}  
        publish_handler({"messagecode":"assettranx","messagetype":"resp","message":message})

    def queryasstdetails(self,asset):
        assetdetails = self.mchain.queryassetsdetails(asset)
        message = {"op-return":assetdetails}    
        publish_handler({"messagecode":"assetdetails","messagetype":"resp","message":message})

    def getburnaddress(self):
        return self.mchain.getburnaddress()     

    def burnasset(self,address,asset_name,asset_qty):
        return self.mchain.sendAsset(address,asset,asset_qty)

    def issueWHasset(self): 
        try:
            assetaddress = self.mchain.accountAddress()
            
            self.assetname = "warehousemoney" 
            assetdetails = {"name":self.assetname,"open":True}
            assetquantity = 100  
            assetunit = 1  
            assetnativeamount =0 
            assetcustomfield = {'currency':'dollars','owner':'John-Distributor'}
            
            issueWHasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)
            assetdescription = {"assetname":self.assetname,"assetquantity":assetquantity,"assetmetrics":"dollars"}
            
            message = {"op-return":issueWHasset_return,"assetdescription":assetdescription}
            
            self.assetsubscribe(self.assetname)
            publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})


        except Exception as e:
            print e,"error in issueHWasset"
            message = {"op-return":"error","message":e}
            publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})

    
    def createExchange(self):
        try:
            # Here asset will be a dictionary ex: {"asset1":1}
            ownasset = {"warehouse-crop":20}
            otherasset = {"retailmoney":20}
            prepare_return = self.mchain.preparelockunspentexchange(ownasset)
            if prepare_return != False:
                createex_return = self.mchain.createExchange(prepare_return["txid"],prepare_return["vout"],otherasset)
                print createex_return
                message = {"op-return":str(createex_return),"hexblob":str(createex_return)}
                publish_handler({"messagecode":"createexchange","messagetype":"resp","message":message})
            else:
                publish_handler({"messagecode":"createexchange","messagetype":"resp","message":""})   
        except Exception as e:
            print e,"error in createExchange"
            publish_handler({"messagecode":"createexchange","messagetype":"resp","message":""})       


    def decodeExchange(self,hexBlob):
        # The following will give the details regarding the exchange
        
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
                # -- step 6 
                # This step is for sending the transaction details to the chain
                if append_return["complete"] == True:
                        send_return = self.mchain.sendrawTransaction(append_return["hex"])
                        message = {"exchange-detials":decodedtranx,"exchange-addedtochain":send_return} 
                        publish_handler({"messagecode":"decodeexchange","messagetype":"resp","message":message})            
            else:
                message = {"exchange-detials":False,"exchange-addedtochain":False} 
                publish_handler({"messagecode":"decodeexchange","messagetype":"resp","message":message})         
                
        else:
            message = {"exchange-detials":False,"exchange-addedtochain":False} 
            publish_handler({"messagecode":"decodeexchange","messagetype":"resp","message":message})         
                            

    def convertasset(self)
        try:
            # step 1 get totalbalances
            assetbalances = self.mchain.assetbalances()
            for i in range(0,len(assetbalances)):
                if assetbalances[i]["name"] != self.assetname
                    self.convertasset_name = assetbalances[i]["name"]
                    self.convertasset_qty = assetbalances[i]["qty"]
                else:
                    
                    message = {"op-return":False,"assetdescription":False,"burnasset-op-return":False}
                    
            # step 2 get details of the asset
            convertasset_details = self.mchain.queryassetsdetails(self.convertasset_name)
            if len(convertasset_details) != 0:
                if convertasset_details[0].has_key("details"):
                    convertedasset_name = "warehouse-crop"
                    assetdetails = {"name":convertedasset_name,"open":True} 
                    assetquantity = int(self.convertasset_qty) 
                    assetunit = 1 
                    assetnativeamount = 0 
                    
                    assetcustomfield = {"asset-arrivaldate":'2017-05-07',"asset-departuredate":'2017-05-10',"assetstorageconditions":"Good"}# will be generated based on sensor data, fields will be decided$
                    assetcustomfield.update(convertasset_details[0]["details"]) 
                    issueWHasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)
                    assetdescription = {"assetname":convertedasset_name,"assetquantity":assetquantity,"assetmetrics":"dollars"}
                    
                    message = {"op-return":issueWHasset_return,"assetdescription":assetdescription}
                    
                    self.assetsubscribe(convertedasset_name)
                    # publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})
                else:
                    message = {"op-return":False,"assetdescription":False,"burnasset-op-return":False}
                    
            else:
                message = {"op-return":False,"assetdescription":False,"burnasset-op-return":False}
                    
            if message["op-return"] !=False:    
                # step 3 send the asset to the burn address
                burnaddress = self.mchain.burnaddress()
                if burnaddress != False:
                    burnasset_return = self.mchain.burnasset(burnaddress,self.convertasset_name,self.convertasset_qty)
                    message.update({"burnasset-op-return":burnasset_return})
                else:
                    message.update({"burnasset-op-return":burnasset_return})
            
            publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})

        except Exception as e:
            message.update({"error":e})
            publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})            


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
                    WH.issueWHasset()
            
            if message["messagecode"] == "decodeexchange":
                    WH.decodeExchange(message["hexblob"],message["ownasset"],message["otherasset"]) 
            
            if message["messagecode"] == "assetbalance":
                    WH.assetbalances()
            
            if message["messagecode"] == "convertasset":
                    WH.convertasset()
            
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
