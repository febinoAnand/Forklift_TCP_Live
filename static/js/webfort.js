// pie chart start//
document.addEventListener('DOMContentLoaded', async () => {
  const ctx = document.getElementById('myPieChart').getContext('2d');
  let myPieChart;

  const updatePieChart = async () => {
    try {
      const todayMorningTimestamp = new Date();
      todayMorningTimestamp.setHours(0, 0, 0, 0);
      const currentTimestamp = Math.floor(Date.now() / 1000);

      const response = await fetch(`/get_today_gps_data/?start=${todayMorningTimestamp.getTime() / 1000}&end=${currentTimestamp}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const data = await response.json();
      let activeMinutes = 0, inactiveMinutes = 0, idleMinutes = 0;

      if (data.length === 0) {
        inactiveMinutes = 24 * 60;
      } else {
        data.forEach(entry => {
          switch (entry.state) {
            case 1:
              activeMinutes += entry.duration / 60;
              break;
            case 2:
              inactiveMinutes += entry.duration / 60;
              break;
            case 3:
              idleMinutes += entry.duration / 60;
              break;
          }
        });
      }

      myPieChart.data.datasets[0].data = [activeMinutes, inactiveMinutes, idleMinutes];
      myPieChart.update();
    } catch (error) {
      console.error('Error fetching or parsing data:', error);
      myPieChart.data.datasets[0].data = [0, 24 * 60, 0];
      myPieChart.update();
    }
  };

  myPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Active Minutes', 'Inactive Minutes', 'Idle Minutes'],
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
function updateGraphWithData(data) {
  const bars = document.querySelectorAll('.graph tbody tr');

  bars.forEach((bar, barIndex) => {
    const percentSpans = bar.querySelectorAll('span.percent');
    const utilizationPercentages = data[barIndex]?.percentages || [0];
    const totalPercentage = utilizationPercentages.reduce((acc, curr) => acc + curr, 0);

    percentSpans.forEach((span, spanIndex) => {
      const percentage = utilizationPercentages[spanIndex] || 0;
      span.textContent = percentage + '%';
    });

    const barHeight = totalPercentage / 3;
    bar.style.height = barHeight + '%';
  });
}

function fetchDataAndUpdateGraph() {
  const apiUrl = '/get_utilization_hours/';

  fetch(apiUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      updateGraphWithData(data);
    })
    .catch(error => console.error('Error fetching data:', error));
}

fetchDataAndUpdateGraph();
setInterval(fetchDataAndUpdateGraph, 5000);
// bar chart ens //