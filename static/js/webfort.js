// pie chart start//
document.addEventListener('DOMContentLoaded', async () =>  {
  const ctx = document.getElementById('myPieChart').getContext('2d');
  let myPieChart;

  const updatePieChart = async () => {
      try {
          const todayMorningTimestamp = new Date();
          todayMorningTimestamp.setHours(0, 0, 0, 0);
          const currentTimestamp = Math.floor(Date.now() / 1000);

          const response = await fetch(`/get_today_gps_data/?start=${todayMorningTimestamp.getTime() / 1000}&end=${currentTimestamp}`);
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }

          const data = await response.json();
          let activeHours = 0, inactiveHours = 0, idleHours = 0;

          if (data.length === 0) {
              inactiveHours = 24;
          } else {
              data.forEach(entry => {
                  switch (entry.state) {
                      case 1:
                          activeHours += entry.duration / 3600;
                          break;
                      case 2:
                          inactiveHours += entry.duration / 3600;
                          break;
                      case 3:
                          idleHours += entry.duration / 3600;
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

  function updateChart() {
    $.ajax({
      url: '/api/get_last_data/',
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
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });

  updateChart();
  setInterval(updateChart, 5000);
});
//line chart end //

// bar chart start //
function updateBarChart(data) {
    Object.keys(data).forEach(day => {
        if (day.toLowerCase() !== 'sunday') {
            var utilizationData = data[day];
            var row = document.querySelector(`.bar-${day.toLowerCase()}`);
            if (row) {
                var bar = row.querySelector('.bar');
                if (bar) {
                    var totalHours = 0;
                    var stateHours = {};
                    var currentTime = new Date(); // Get current time
                    var totalPercentage = 0;
                    var maxHeight = 100; // Maximum height for the bar
                    for (const state in utilizationData) {
                        if (state !== 'Total') {
                            var hours = parseFloat(utilizationData[state]);
                            if (!isNaN(hours) && hours >= 0) {
                                stateHours[state] = hours;
                                totalHours += hours;
                            }
                        }
                    }
                    if (totalHours > 0) {
                        for (const state in stateHours) {
                            var percentage = (stateHours[state] / totalHours) * 100;
                            var element = bar.querySelector(`.${state.toLowerCase()}`);
                            if (element) {
                                element.textContent = `${percentage.toFixed(1)}%`;
                                element.style.height = `${(percentage * maxHeight) / 100}%`; 
                                if (state.toLowerCase() === 'active') {
                                    element.style.background = '#6ECBFA';
                                } else if (state.toLowerCase() === 'idle') {
                                    element.style.background = '#FCF46B';
                                } else if (state.toLowerCase() === 'inactive') {
                                    element.style.background = '#F78484';
                                }
                                totalPercentage += percentage;
                            }
                        }
                        if (totalPercentage > 0 && totalPercentage <= 100) {
                            bar.style.height = `${(totalPercentage * maxHeight) / 100}%`; 
                        } else {
                            console.error(`Total percentage exceeds 100% for ${day}.`);
                        }
                    }
                } else {
                    console.error(`Bar not found for ${day}.`);
                }
            }
        }
    });
}
function fetchDataAndUpdate() {
  fetch('/get_utilization_hours/')
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