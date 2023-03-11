$(document).ready(function () {
  const ctx = document.getElementById("myChart").getContext("2d");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Sensor 1", pointRadius: 0, }],
    },
    options: {
      borderWidth: 1,
      borderColor: ['rgba(255, 99, 132, 1)',],
      scales: {
        xAxis: {
            display: false,
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
  const socket = new WebSocket('ws://' + location.host + '/ws');
  socket.addEventListener('message', msg => {
    const data = JSON.parse(msg.data);
    console.log("Received sensorData :: " + data.value);

    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    addData(data.date, data.value);
  });

});