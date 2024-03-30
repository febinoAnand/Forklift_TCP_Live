// pie chart start//
document.addEventListener('DOMContentLoaded', async () =>  {
    const ctx = document.getElementById('myPieChart').getContext('2d');
    let myPieChart;
    var deviceID = document.getElementById("currentdeviceID").innerText;

    const updatePieChart = async () => {
        try {
            const todayMorningTimestamp = new Date();
            todayMorningTimestamp.setHours(0, 0, 0, 0);
            const currentTimestamp = Math.floor(Date.now() / 1000);

            const response = await fetch(`/get_today_gps_data/?deviceID=`+deviceID);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
        
            const data = await response.json();
            let activeHours = 0, inactiveHours = 0, idleHours = 0;

            if (data.length === 0) {
                inactiveHours = 24;
            } else {
              //   data.forEach(entry => {
              //       switch (entry.state) {
              //           case 1:
              //               activeHours += entry.duration / 3600;
              //               break;
              //           case 2:
              //               inactiveHours += entry.duration / 3600;
              //               break;
              //           case 3:
              //               idleHours += entry.duration / 3600;
              //               break;
              //       }
              //   });
              
              data.forEach(entry => {
                switch (entry.state) {
                    case "Active":
                        activeHours = entry.duration;
                        break;
                    case "Inactive":
                        inactiveHours = entry.duration ;
                        break;
                    case "Idle":
                        idleHours = entry.duration;
                        break;
                    case "Alert":
                        inactiveHours += entry.duration;
                        break;
                }
            });
        }

        myPieChart.data.datasets[0].data = [activeHours, inactiveHours, idleHours];
        myPieChart.update();
    } catch (error) {
        console.error('Error fetching or parsing data:', error);
        myPieChart.data.datasets[0].data = [0, 24, 0];
        myPieChart.update();
    }
};

myPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['Active Hours', 'Inactive Hours', 'Idle Hours'],
        datasets: [{
            label: 'Today',
            data: [0, 0, 0],
            backgroundColor: [
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 206, 86, 0.8)'
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true
    }
});

updatePieChart();
setInterval(updatePieChart, 5000);
});
  // pie chart end//
  
  // line chart start //
  document.addEventListener('DOMContentLoaded', function() {
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart;
    var deviceID = document.getElementById("currentdeviceID").innerText;
    function updateChart() {
        $.ajax({
            url: '/api/get_last_data/?deviceID='+deviceID,
            success: function(data) {
                var gpsData = data.gps_data.map(item => item.speed);
                var extData = data.ext_data.map(item => item.speed);
                var labels = data.gps_data.map(item => item.time);

                myChart.data.labels = labels;
                myChart.data.datasets[0].data = gpsData;
                myChart.data.datasets[1].data = extData;

                myChart.update();
            }
        });
    }

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                    label: 'GPS-Speed',
                    data: [],
                    borderColor: 'red',
                    borderWidth: 1
                },
                {
                    label: 'EXT-Speed',
                    data: [],
                    borderColor: 'blue',
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    updateChart("device_id");
    setInterval(() => updateChart("device_id"), 5000);
});
  //line chart end //
  
  // bar chart start //
  var deviceID = document.getElementById("currentdeviceID").innerText;
 function updateBarChart(data) {
    Object.keys(data).forEach(day => {
        var utilizationData = data[day];
        var row = document.querySelector(`.bar-${day.toLowerCase()}`);
        if (row) {
            var bar = row.querySelector('.bar');
            if (bar) {
                var totalActive = parseFloat(utilizationData['Active']);
                var totalIdle = parseFloat(utilizationData['Idle']);
                var totalInactive = 24 - (totalActive + totalIdle);
                
                var activeElement = bar.querySelector('.active');
                var activeHours = totalActive > 0 ? totalActive : 0; // If totalActive is 0, set activeHours to 0
                
                var activePixel = (activeHours / 24) * 332; // Assuming 332 is the maximum height of the bar
                activeElement.style.height = `${activePixel}px`;
                activeElement.textContent = activeHours.toFixed(1);
                activeElement.style.backgroundColor = '#6EC7FA';
                activeElement.style.display = activePixel > 0 ? 'block' : 'none'; // Show or hide text content based on the height
                
                var idleElement = bar.querySelector('.idle');
                var idleHours = parseFloat(utilizationData['Idle']);
                var idlePixel = (idleHours / 24) * 332; // Assuming 332 is the maximum height of the bar
                idleElement.style.height = `${idlePixel}px`;
                idleElement.textContent = idleHours.toFixed(1);
                idleElement.style.backgroundColor = '#FAFA6E';
                idleElement.style.display = idlePixel > 0 ? 'block' : 'none'; // Show or hide text content based on the height
                
                var inactiveElement = bar.querySelector('.inactive');
                var inactivePixel = (totalInactive / 24) * 332; // Assuming 332 is the maximum height of the bar
                inactiveElement.style.height = `${inactivePixel}px`;
                inactiveElement.textContent = totalInactive.toFixed(1);
                inactiveElement.style.backgroundColor = '#FA766E';
                inactiveElement.style.display = inactivePixel > 0 ? 'block' : 'none'; // Show or hide text content based on the height
            } else {
                console.error(`Bar not found for ${day}.`);
            }
        } else {
            console.error(`Row for ${day} not found.`);
        }
    });
}




  function fetchDataAndUpdate() {
      fetch('/get_utilization_hours/?deviceID='+deviceID)
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(data => updateBarChart(data))
          .catch(error => console.error('Error fetching data:', error));
  }
  
  fetchDataAndUpdate();
  setInterval(fetchDataAndUpdate, 5000);
  // bar chart ens //