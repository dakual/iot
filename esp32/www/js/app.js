$(document).ready(function () {
  const ctx = document.getElementById("myChart").getContext("2d");
  var sensorValue = 0

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Sensor 1", pointRadius: 0, }],
    },
    options: {
      animation: false,
      borderWidth: 1,
      borderColor: ['rgba(255, 99, 132, 1)',],
      scales: {
        xAxis: {
          display: false,
        },
        yAxis: {
          display: true,
          max: (scale) => (
            scale.chart.data.datasets.reduce((acc, curr) => {
              var max = 0
              if (Array.isArray(curr.data)) {
                max = Math.max(...curr.data) + 20000;
              }
              return max;
            }, Number.MIN_SAFE_INTEGER)),
          min: (scale) => (
            scale.chart.data.datasets.reduce((acc, curr) => {
              var min = 0
              if (Array.isArray(curr.data)) {
                min = Math.min(...curr.data) - 20000;
              }
              return min;
            }, Number.MIN_SAFE_INTEGER))
      }
      }
    },
  });

  function addData(label, data) {
    myChart.data.labels.push(label);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart.update();
  }

  function removeFirstData() {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }

  
  const MAX_DATA_COUNT = 600;
  const socket = new WebSocket('ws://' + location.host);
  socket.addEventListener('message', msg => {
    const data  = JSON.parse(msg.data);
    sensorValue = data.value;
    console.log("Received sensorData :: " + data.value);

    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    addData(data.date, data.value);
  });

});