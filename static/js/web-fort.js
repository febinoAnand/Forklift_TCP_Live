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
};

var myPieChart = new Chart(ctx, {
  type: 'pie',
  data: data,
  options: {
      responsive: true
  }
});

function updatePieChart() {
  var active = Math.floor(Math.random() * 100);
  var inactive = Math.floor(Math.random() * (100 - active));
  var idle = 100 - active - inactive;

  myPieChart.data.datasets[0].data = [active, inactive, idle];

  myPieChart.update();
}
setInterval(updatePieChart, 5000);
// pie chart end//

// line chart start //
document.addEventListener('DOMContentLoaded', function() {
  var ctx = document.getElementById('myChart').getContext('2d');
  var myChart;

  function updateChartWithData(data) {
    var labels = data.gps_speed.map(entry => entry[0]); // Extract time from GPS speed data
    var gpsSpeedData = data.gps_speed.map(entry => entry[1]); // Extract GPS speed values
    var extSpeedData = data.ext_speed.map(entry => entry[1]); // Extract EXT speed values

    myChart.data.labels = labels;
    myChart.data.datasets[0].data = gpsSpeedData;
    myChart.data.datasets[1].data = extSpeedData;

    myChart.update();
  }

  function fetchDataAndUpdateChart() {
    fetch('/get_speed_data/') // URL to fetch data from
      .then(response => response.json())
      .then(data => updateChartWithData(data))
      .catch(error => console.error('Error fetching data:', error));
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

  setInterval(fetchDataAndUpdateChart, 5000);
});
//line chart end //

// bar chart start //
function generateRandomTime() {
  var hours = Math.floor(Math.random() * 12) + 1; 
  var minutes = Math.floor(Math.random() * 60); 
  var ampm = Math.random() < 0.5 ? 'AM' : 'PM'; 
  return hours + ':' + (minutes < 10 ? '0' : '') + minutes + ' ' + ampm;
}

function generateRandomData() {
  var data = [];
  for (var i = 0; i < 6; i++) {
    data.push(Math.floor(Math.random() * 100));
  }
  return data;
}

function updateTable() {
  var timeLabels = [];
  var newData = generateRandomData();

  for (var i = 0; i < 6; i++) {
    timeLabels.push(generateRandomTime());
  }

  var rows = document.querySelectorAll('.graph tbody tr');

  rows.forEach(function(row, index) {
    var span = row.querySelector('span');
    var percent = newData[index] + '%';
    row.style.height = percent;
    row.querySelector('th').textContent = timeLabels[index];
    span.textContent = percent;
  });
}

function fetchDataAndUpdate() {

  updateTable();
}
setInterval(fetchDataAndUpdate, 5000);
// bar chart ens //