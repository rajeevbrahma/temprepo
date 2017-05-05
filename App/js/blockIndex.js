var farm_warehouse_shop_hexblob = '';
var warehouse_shop_hexblob = '';

pubnub = new PubNub({
    publishKey : 'pub-c-abde89c6-da51-4c04-8c2b-9c3984e1182d',
    subscribeKey : 'sub-c-d17a927c-e171-11e6-802a-02ee2ddab7fe'
})
       
    function publishMessage(channel,msg) {
        console.log(channel,msg)
        pubnub.publish(
        {
            message: msg,
            channel: channel,
            storeInHistory: true //override default storage options
        });
    }  
    pubnub.addListener({
        message: function(m) {
            console.log("Received Message!!", m.message);
            messageOnReceive(m.message)
        }
    })      
        
    pubnub.subscribe({
        channels: ['UI'] 
    });

    function messageOnReceive(m){
        console.log(m)
        if(m.messagecode == "decodeexchange" && m.messagetype == "resp" && m.node == "warehouse"){
            if(m.message.exchange_details != false && m.message.exchange_addedtochain != false){
                $('#arrow1').css({fill:"#7CFC00"});
                $('#Farm-Warehouse-Offered-Name').text(m.message.exchange_details.offer.assets[0].name);
                $('#Farm-Warehouse-Offered-Quantity').text(m.message.exchange_details.offer.assets[0].qty);
                $('#Farm-Warehouse-Asked-Name').text(m.message.exchange_details.ask.assets[0].name);
                $('#Farm-Warehouse-Asked-Quantity').text(m.message.exchange_details.ask.assets[0].qty);
                var publishMsg = { "messagecode":"updateassetbalance","messagetype":"req"}
                var channel = "farmland"
                publishMessage(channel,publishMsg)
                var publishMsg = { "messagecode":"updateassetbalance","messagetype":"req"}
                var channel = "warehouse"
                publishMessage(channel,publishMsg)
            }else
            {
                $('input:radio[name=createExchange]:nth(1)').attr('checked',false);
                alert("error")
            }
        }else if(m.messagecode == "decodeexchange" && m.messagetype == "resp" && m.node == "retailstore"){
            if(m.message.exchange_details != false && m.message.exchange_addedtochain != false){
                $('#arrow2').css({fill:"#7CFC00"});
                $('#Warehouse-Retailshop-Offered-Name').text(m.message.exchange_details.offer.assets[0].name);
                $('#Warehouse-Retailshop-Offered-Quantity').text(m.message.exchange_details.offer.assets[0].qty);
                $('#Warehouse-Retailshop-Asked-Name').text(m.message.exchange_details.ask.assets[0].name);
                $('#Warehouse-Retailshop-Asked-Quantity').text(m.message.exchange_details.ask.assets[0].qty);
                var publishMsg = { "messagecode":"updateassetbalance","messagetype":"req"}
                var channel = "warehouse"
                publishMessage(channel,publishMsg)
                var publishMsg = { "messagecode":"updateassetbalance","messagetype":"req"}
                var channel = "retailstore"
                publishMessage(channel,publishMsg)
            }else
            {
                $('input:radio[name=createExchange]:nth(3)').attr('checked',false);
                alert("error")
            }
        }else if(m.messagecode == "createexchange" && m.messagetype == "resp" && m.node == "farmland"){
            // create exchange top level error handling
            if(m.message == " "){
                console.log(m.message.error)
                $('input:radio[name=createExchange]:nth(0)').attr('checked',false);
                alert(m.message.error)
            }
            // create exchange API level error handling
            else if(m.message.hexblob == " "){
                $('input:radio[name=createExchange]:nth(0)').attr('checked',false);
                alert("API error")
            }else{
                console.log("reached")
                farm_warehouse_shop_hexblob = m.message.hexblob;
                $('#arrow1').css({fill:"#FF4500"});
            }
        }else if(m.messagecode == "createexchange" && m.messagetype == "resp" && m.node == "warehouse"){
            // create exchange top level error handling
            if(m.message == ""){
                console.log(m.message.error)
                $('input:radio[name=createExchange]:nth(2)').attr('checked',false);
                alert(m.message.error)
            }
            // create exchange API level error handling
            else if(m.message.hexblob == ""){
                $('input:radio[name=createExchange]:nth(2)').attr('checked',false);
                alert("API error")
            }else{
                farm_warehouse_shop_hexblob = m.message.hexblob;
                $('#arrow2').css({fill:"#FF4500"});
            }
        }
        else if(m.messagecode == "issueasset" && m.messagetype == "resp" && m.node == "farmland"){
            if(m.message["op_return"]["error"] != undefined || m.message["op_return"] == "error"){
                $('input:radio[name=IssueAssert]:nth(0)').attr('checked',false);
                alert("error")
            }else
            {
                $('#step_1_circle').css({fill:"#7CFC00"});
                $('#FarmLand-Name').text(m.message.assetdescription.assetname);
                $('#FarmLand-Quantity').text(m.message.assetdescription.assetquantity);
                $('#FarmLand-Metrics').text(m.message.assetdescription.assetmetrics);
                $('#FarmLand-Owner').text(m.message.assetdescription.assetowner);
            }
        }else if(m.messagecode == "issueasset" && m.messagetype == "resp" && m.node == "warehouse"){
            if(m.message["op_return"]["error"] != undefined || m.message["op_return"] == "error"){
                $('input:radio[name=IssueAssert]:nth(1)').attr('checked',false);
                alert("error")
            }else
            {
                $('#step_2_circle').css({fill:"#7CFC00"});
                $('#Warehouse-Name').text(m.message.assetdescription.assetname);
                $('#Warehouse-Quantity').text(m.message.assetdescription.assetquantity);
                $('#Warehouse-Metrics').text(m.message.assetdescription.assetmetrics);
                $('#Warehouse-Owner').text(m.message.assetdescription.assetowner);
            }
        }else if(m.messagecode == "issueasset" && m.messagetype == "resp" && m.node == "retailstore"){
            if(m.message["op_return"]["error"] != undefined || m.message["op_return"] == "error"){
                $('input:radio[name=IssueAssert]:nth(2)').attr('checked',false);
                alert("error")
            }else
            {
                $('#step_3_circle').css({fill:"#7CFC00"});
                $('#RetailShop-Name').text(m.message.assetdescription.assetname);
                $('#RetailShop-Quantity').text(m.message.assetdescription.assetquantity);
                $('#RetailShop-Metrics').text(m.message.assetdescription.assetmetrics);
                $('#RetailShop-Owner').text(m.message.assetdescription.assetowner);
            }
        }else if(m.messagecode == "updateassetbalance" && m.messagetype == "resp" && m.node == "farmland"){
            if(m.message["op_return"]["error"] != undefined || m.message["op_return"] == "error"){
                alert("error")
            }else
            {
                $('#FarmLand-Table').empty();

                $('#RetailShop-Name').text(m.message.assetdescription.assetname);
                $('#RetailShop-Quantity').text(m.message.assetdescription.assetquantity);
                $('#RetailShop-Metrics').text(m.message.assetdescription.assetmetrics);
                $('#RetailShop-Owner').text(m.message.assetdescription.assetowner);
            }
        }
        else if(m.messagecode == "updateassetbalance" && m.messagetype == "resp" && m.node == "warehouse"){
            if(m.message["op_return"]["error"] != undefined || m.message["op_return"] == "error"){
                alert("error")
            }else
            {
                $('#Warehouse-Table').empty();
                $('#RetailShop-Name').text(m.message.assetdescription.assetname);
                $('#RetailShop-Quantity').text(m.message.assetdescription.assetquantity);
                $('#RetailShop-Metrics').text(m.message.assetdescription.assetmetrics);
                $('#RetailShop-Owner').text(m.message.assetdescription.assetowner);
            }
        }
        else if(m.messagecode == "updateassetbalance" && m.messagetype == "resp" && m.node == "retailstore"){
            if(m.message["op_return"]["error"] != undefined || m.message["op_return"] == "error"){
                alert("error")
            }else
            {
                $('#Retailshop-Table').empty();
                $('#RetailShop-Name').text(m.message.assetdescription.assetname);
                $('#RetailShop-Quantity').text(m.message.assetdescription.assetquantity);
                $('#RetailShop-Metrics').text(m.message.assetdescription.assetmetrics);
                $('#RetailShop-Owner').text(m.message.assetdescription.assetowner);
            }
        }
    }


$(document).ready(function(){ 

    $("#myBtn").click(function(){
        var publishMsg = { "messagecode":"convertasset","messagetype":"req"}
        var channel = "warehouse"
        publishMessage(channel,publishMsg)
        console.log("im here")
        // $('#myModal').modal('show');
    });
    $('#farmland').click(function(){
        var publishMsg = { "messagecode":"issueasset","messagetype":"req"}
        var channel = "farmland"
        publishMessage(channel,publishMsg)
    })
    $('#warehouse').click(function(){
        var publishMsg = { "messagecode":"issueasset","messagetype":"req"}
        var channel = "warehouse"
        publishMessage(channel,publishMsg)
    })
    $('#retailstore').click(function(){
        var publishMsg = { "messagecode":"issueasset","messagetype":"req"}
        var channel = "retailstore"
        publishMessage(channel,publishMsg)
    })

// RadioButton select - Issue Assert

    $('#IssueAssert-farm').click(function(){
        $('input:radio[name=IssueAssert]:nth(0)').attr('checked',true);
        var publishMsg = { "messagecode":"issueasset","messagetype":"req","IssueAssert":"farmland"}
        var channel = "farmland"
        publishMessage(channel,publishMsg)
    })
    $('#IssueAssert-warehouse').click(function(){
        $('input:radio[name=IssueAssert]:nth(1)').attr('checked',true);
        var publishMsg = { "messagecode":"issueasset","messagetype":"req","IssueAssert":"warehouse"}
        var channel = "warehouse"
        publishMessage(channel,publishMsg)
    })
    $('#IssueAssert-retailshop').click(function(){
        $('input:radio[name=IssueAssert]:nth(2)').attr('checked',true);
        var publishMsg = { "messagecode":"issueasset","messagetype":"req","IssueAssert":"retailshop"}
        var channel = "retailstore"
        publishMessage(channel,publishMsg)
    })

// RadioButton select - Exchange Assert

    $('#createExchange-farm-warehouse').click(function(){
        $('input:radio[name=createExchange]:nth(0)').attr('checked',true);
        var publishMsg =  {"messagetype":"req","messagecode":"createexchange"}
        var channel = "farmland"
        publishMessage(channel,publishMsg)
    })
    $('#Decode-Exchange-farm-warehouse').click(function(){
        $('input:radio[name=createExchange]:nth(1)').attr('checked',true);
        var publishMsg =  {"messagetype":"req","messagecode":"decodeexchange","hexblob":farm_warehouse_shop_hexblob}
        var channel = "warehouse"
        publishMessage(channel,publishMsg)
    })
    $('#createExchange-warehouse-shop').click(function(){
        $('input:radio[name=createExchange]:nth(2)').attr('checked',true);
        $('#arrow2').css({fill:"#FF4500"});
        var publishMsg =  {"messagetype":"req","messagecode":"createexchange"}
        var channel = "warehouse"
        publishMessage(channel,publishMsg)
    })
    $('#Decode-Exchange-warehouse-shop').click(function(){
        $('input:radio[name=createExchange]:nth(3)').attr('checked',true);
        var publishMsg =  {"messagetype":"req","messagecode":"decodeexchange","hexblob":farm_warehouse_shop_hexblob}
        var channel = "retailstore"
        publishMessage(channel,publishMsg)
    })

});