function updateGPSTable(deviceID){
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        
        var data = JSON.parse(this.responseText);
        var gpsTemplateString = "";
        if (data.length <= 0){
            gpsTemplateString = "<tr> \
                                    <td colspan=10> No Data </td>\
                                </tr>";
        }
        
        for(let i =0;i<data.length;i++){
            var fieldData = data[i]["fields"];
            // console.log(fieldData);
            gpsTemplateString +="<tr> \
                                <td>"+(i+1)+"</td> \
                                <td>"+fieldData['date']+"</td> \
                                <td>"+fieldData['time']+"</td> \
                                <td>"+fieldData['distance']+"</td> \
                                <td>"+fieldData['speed']+"</td> \
                                <td>"+fieldData['latitude']+"</td> \
                                <td>"+fieldData['longitude']+"</td> \
                                </tr>";
        }
        document.getElementById("gps_data_table").innerHTML = gpsTemplateString;
        
    }
    xhttp.open("GET", "updategpstable?deviceID="+deviceID, true);
    xhttp.send();
    
}


function updateEXTTable(deviceID){
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        var data = JSON.parse(this.responseText);
        var extTemplateString = "";
        if (data.length <= 0){
            extTemplateString = "<tr> \
                                    <td colspan=10> No Data </td>\
                                </tr>";
        }
        
        for(let i =0;i<data.length;i++){
            var fieldData = data[i]["fields"];
            extTemplateString +="<tr> \
                                <td>"+(i+1)+"</td> \
                                <td>"+fieldData['date']+"</td> \
                                <td>"+fieldData['time']+"</td> \
                                <td>"+fieldData['distance']+"</td> \
                                <td>"+fieldData['speed']+"</td> \
                                <td>"+fieldData['watt_hr']+"</td> \
                                <td>"+fieldData['batt_voltage']+"</td> \
                                <td>"+fieldData['batt_amp']+"</td> \
                                <td>"+fieldData['batt_power']+"</td> \
                                <td>"+fieldData['batt_capacity']+"</td> \
                                </tr>"
        }
        document.getElementById("external_data_table").innerHTML = extTemplateString;
    }
    xhttp.open("GET", "updateexttable?deviceID="+deviceID, true);
    xhttp.send();
}

function startUpdateTable(imei_id){
    // console.log("IMEI ID:",imei_id);
    updateGPSTable(imei_id);
    updateEXTTable(imei_id);
    setInterval(updateGPSTable,5000,imei_id);
    setInterval(updateEXTTable,5000,imei_id);

}