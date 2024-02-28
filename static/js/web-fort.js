
var ctx = document.getElementById('myPieChart').getContext('2d');
var myPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['Active Vehicles', 'Inactive Vehicles', 'Idle Vehicles'],
        datasets: [{
            label: 'Pie Chart',
            data: [30, 30, 40],
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true
    }
});

document.addEventListener('DOMContentLoaded', function() {
    var ctx = document.getElementById('myChart').getContext('2d');

    // Function to generate random data
    function generateRandomData() {
      var labels = [];
      var data = [];

      // Generate random time labels
      for (var i = 0; i < 6; i++) {
        var hour = Math.floor(Math.random() * 12) + 1;
        var minute = Math.floor(Math.random() * 60);
        var time = hour + ':' + (minute < 10 ? '0' : '') + minute + (hour < 12 ? ' AM' : ' PM');
        labels.push(time);
      }

      // Generate random speed data
      for (var i = 0; i < 6; i++) {
        data.push(Math.floor(Math.random() * 12));
      }

      return {
        labels: labels,
        data: data
      };
    }

    // Generate random data
    var randomData = generateRandomData();

    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: randomData.labels,
        datasets: [{
          label: 'Speed',
          data: randomData.data,
          borderColor: 'red',
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
  });




