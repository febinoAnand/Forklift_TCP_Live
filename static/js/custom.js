function updateGPSTable(deviceID){
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        var responseData = JSON.parse(this.responseText);
        var gpsData = JSON.parse(responseData['gps_data']);

        var gpsTemplateString = "";
        if (!gpsData || gpsData.length <= 0){
            gpsTemplateString = "<tr> \
                                    <td colspan=10> No Data </td>\
                                </tr>";
        }
        else {
            for(let i = 0; i < gpsData.length; i++){
                var fieldData = gpsData[i].fields;
                gpsTemplateString += "<tr> \
                                        <td>"+(i+1)+"</td> \
                                        <td>"+fieldData.date+"</td> \
                                        <td>"+fieldData.time+"</td> \
                                        <td>"+fieldData.distance+"</td> \
                                        <td>"+fieldData.speed+"</td> \
                                        <td>"+fieldData.latitude+"</td> \
                                        <td>"+fieldData.longitude+"</td> \
                                    </tr>";
            }
        }
        document.getElementById("gps_data_table").innerHTML = gpsTemplateString;
        
    }
    xhttp.open("GET", "combined-data-view/?deviceID="+deviceID, true);
    xhttp.send();
}

function updateEXTTable(deviceID){
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        var responseData = JSON.parse(this.responseText);
        var extData = JSON.parse(responseData['ext_data']);

        var extTemplateString = "";
        if (!extData || extData.length <= 0){
            extTemplateString = "<tr> \
                                    <td colspan=10> No Data </td>\
                                </tr>";
        }
        else {
            for(let i = 0; i < extData.length; i++){
                var fieldData = extData[i].fields;
                extTemplateString += "<tr> \
                                        <td>"+(i+1)+"</td> \
                                        <td>"+fieldData.date+"</td> \
                                        <td>"+fieldData.time+"</td> \
                                        <td>"+fieldData.distance+"</td> \
                                        <td>"+fieldData.speed+"</td> \
                                        <td>"+fieldData.watt_hr+"</td> \
                                        <td>"+fieldData.batt_voltage+"</td> \
                                        <td>"+fieldData.batt_amp+"</td> \
                                        <td>"+fieldData.batt_power+"</td> \
                                        <td>"+fieldData.batt_capacity+"</td> \
                                    </tr>";
            }
        }
        document.getElementById("external_data_table").innerHTML = extTemplateString;
    }
    xhttp.open("GET", "combined-data-view/?deviceID="+deviceID, true);
    xhttp.send();
}


function startUpdateTable(imei_id){
    updateGPSTable(imei_id);
    updateEXTTable(imei_id);
    setInterval(updateGPSTable, 5000, imei_id);
    setInterval(updateEXTTable, 5000, imei_id);
}
