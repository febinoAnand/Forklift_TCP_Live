$(document).ready(function(){
  $("#loginForm").submit(function(e){
      e.preventDefault();
      var password = $("#password").val();
      if(password !== "123456"){
          alert("Incorrect password! Please try again.");
      } else {
    window.location.href="MAP.html";
          alert("Login successful!");
      }
  });
});


// pie chart start//
var ctx = document.getElementById('myPieChart').getContext('2d');
var data = {
  labels: ['Active Vehicles', 'Inactive Vehicles', 'Idle Vehicles'],
  datasets: [{
      label: 'Pie Chart',
      data: [30, 30, 40],
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
};

var myPieChart = new Chart(ctx, {
  type: 'pie',
  data: data,
  options: {
      responsive: true
  }
});

function updatePieChart() {
  var start_date = '2024-01-19';
  var end_date = '2024-02-27';

  $.ajax({
      url: '/get_gps_data/',
      data: {
          start_date: start_date,
          end_date: end_date
      },
      dataType: 'json',
      success: function(data) {
          myPieChart.data.datasets[0].data = [data.active, data.inactive, data.idle];
          myPieChart.update();
      }
  });
}

setInterval(updatePieChart, 5000);
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
function generateRandomData() {
  var data = [];
  for (var i = 0; i < 6; i++) {
    data.push(Math.floor(Math.random() * 100));
  }
  return data;
}

function updateTable() {
  var daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  var reorderedDays = daysOfWeek.slice(1).concat(daysOfWeek.slice(0, 1)); 
  var newData = generateRandomData();

  for (var i = 0; i < 6; i++) {
    var day = reorderedDays[i];
    var percent = newData[i] + '%';
    var row = document.querySelectorAll('.graph tbody tr')[i];
    row.style.height = percent;
    row.querySelector('th').textContent = day;
    row.querySelector('span').textContent = percent;
  }
}

function fetchDataAndUpdate() {
  updateTable();
}
setInterval(fetchDataAndUpdate, 5000);
// bar chart ens //