// pie chart start//
document.addEventListener('DOMContentLoaded', function() {
  var ctx = document.getElementById('myPieChart').getContext('2d');
  var myPieChart;

  function updatePieChart() {
      var todayMorningTimestamp = new Date();
      todayMorningTimestamp.setHours(0, 0, 0, 0);
      var currentTimestamp = Math.floor(Date.now() / 1000);
      fetch('/get_today_gps_data/?start=' + todayMorningTimestamp.getTime() / 1000 + '&end=' + currentTimestamp)
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(data => {
              var activeHours = 0;
              var inactiveHours = 0;
              var idleHours = 0;

              if (data.length === 0) {
                  inactiveHours = 24;
              } else {
                  data.forEach(entry => {
                      if (entry.state === 'active') {
                          activeHours += entry.duration / 3600;
                      } else if (entry.state === 'inactive') {
                          inactiveHours += entry.duration / 3600;
                      } else if (entry.state === 'idle') {
                          idleHours += entry.duration / 3600;
                      }
                  });
              }

              myPieChart.data.datasets[0].data = [activeHours, inactiveHours, idleHours];
              myPieChart.update();
          })
          .catch(error => {
              console.error('Error fetching or parsing data:', error);
              myPieChart.data.datasets[0].data = [0, 24, 0];
              myPieChart.update();
          });
  }

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
  var daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    for (var i = 0; i < 6; i++) {
      var day = daysOfWeek[i];
      var utilizationHours = data[day] || 0;
      var percent = (utilizationHours / MAX_HOURS) * 100;

      var row = document.querySelectorAll('.graph tbody tr')[i];
      var bar = row.querySelector('td');
      bar.style.height = percent + '%';
      row.querySelector('th').textContent = day;
      row.querySelector('span').textContent = percent.toFixed(2) + '%';

      if (percent >= 0 && percent <= 33.33) {
        bar.style.backgroundColor = '#F37265';
      } else if (percent > 33.33 && percent <= 66.66) {
        bar.style.backgroundColor = '#5BADFF';
      } else if (percent > 66.66 && percent <= 100) {
        bar.style.backgroundColor = '#FF6E26';
      }
    }
}
function fetchDataAndUpdate() {
    fetch('/utilization-hours/')
        .then(response => response.json())
        .then(data => updateBarChart(data))
        .catch(error => console.error('Error fetching data:', error));
}

const MAX_HOURS = 24 * 6;
setInterval(fetchDataAndUpdate, 5000);
// bar chart ens //