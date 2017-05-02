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




LOG_FILENAME = 'retailstore.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Retailstore:
    def __init__(self,rpcuser,rpcpasswd,rpchost,rpcport,chainname):
        print "Retailstore"
        self.rpcuser = rpcuser
        self.rpcpasswd = rpcpasswd
        self.rpchost = rpchost
        self.rpcport = rpcport
        self.chainname = chainname
        self.mchain = Multichainpython(self.rpcuser,self.rpcpasswd,self.rpchost,self.rpcport,self.chainname)

    def connectTochain(self):       
        return self.mchain.multichainConnect()
    def retailstoreAddress(self):
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
    
    
    def issueRSasset(self): 
        try:
            assetaddress = self.mchain.accountAddress()
            assetname = "retailmoney" 
            assetdetails = {"name":assetname,"open":True} # along withthat a unique timestamp will be added
            assetquantity = 100 
            assetunit = 1 
            assetnativeamount =0 
            assetcustomfield = {'currency':'dollars','owner':'Peter-Retailer'}# will be generated based on sensor data, fields will be decided$
            issueRSasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)
            assetdescription = {"assetname":assetname,"assetquantity":assetquantity,"assetmetrics":"dollars"}
            
            message = {"op-return":issueRSasset_return,"assetdescription":assetdescription}
            
            self.assetsubscribe(assetname)
            publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})


        except Exception as e:
            print e,"error in issueHWasset"
            message = {"op-return":"error","message":e}
            publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})

    
    # def createExchange(self,ownasset,otherasset):
    #     try:
    #         # Here asset will be a dictionary ex: {"asset1":1}
    #         ownasset = {"warehouse-crop":20}
    #         otherasset = {"retailmoney":20}
    #         prepare_return = self.mchain.preparelockunspentexchange(ownasset)
    #         if prepare_return != False:
    #             createex_return = self.mchain.createExchange(prepare_return["txid"],prepare_return["vout"],otherasset)
    #             print createex_return
    #             message = {"op-return":str(createex_return),"hexblob":str(createex_return)}
    #             publish_handler({"messagecode":"createexchange","messagetype":"resp","message":message})
    #         else:
    #             publish_handler({"messagecode":"createexchange","messagetype":"resp","message":""})   
    #     except Exception as e:
    #         print e,"error in createExchange"
    #         publish_handler({"messagecode":"createexchange","messagetype":"resp","message":""})       


    def decodeExchange(self,hexBlob):
        # The following will give the details regarding the exchange
        
        ownasset = {"retailmoney":20}
        otherasset = {"warehouse-crop":20}
        
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
                    RS.issueRSasset()
            # if message["messagecode"] == "createexchange":
            #         RS.issueRSasset()
            if message["messagecode"] == "decodeexchange":
                    RS.decodeExchange(message["hexblob"],message["ownasset"],message["otherasset"]) 
            
            # if message["messagecode"] == "assettranx":
            #         RS.queryassettranx(message["asset"])
            # if message["messagecode"] == "assetdetails":
            #         RS.queryasstdetails(message["asset"])
            if message["messagecode"] == "assetbalance":
                    RS.assetbalances()

    except Exception as e:
        print e,"callback error"
        #logging.error("The callback exception is %s,%s"%(e,type(e)))           
        #logging.info(message)


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

    RS = Retailstore(rpcuser,rpcpasswd,rpchost,rpcport,chainname)
    RS.connectTochain()
    pub_Init()