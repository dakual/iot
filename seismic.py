import logging, threading, sys
from MPU6050 import MPU6050
from logging.handlers import RotatingFileHandler
from time import sleep

### Seismic sensor file logger
handler = RotatingFileHandler(
  filename = 'logs.log', 
  mode = 'a',
  maxBytes = 5*1024*1024,
  backupCount = 10,
  encoding = None,
  delay = False
)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

sensorLogger = logging.getLogger("sensor")
sensorLogger.addHandler(handler)
sensorLogger.setLevel(logging.INFO)

### Module stdout logger
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger = logging.getLogger("stdout")
logger.addHandler(stdout_handler)
logger.setLevel(logging.INFO)


class Seismograph(threading.Thread):
  samples = 1000
  avarage = 0
  sensorValue = 0

  def __init__(self):
    threading.Thread.__init__(self)

    logger.info("Sensor starting...")
    self.mpu = MPU6050(0x68)
    self.mpu.reset()
    self.mpu.power_manage()
    self.mpu.accel_config()
    self.calibrate()


  def run(self):
    alarm_threshold = 30
    avg_percentage  = 1
    sample_size     = 100
    
    logger.info("Sensor started.")

    samples = []
    counter = 0
    while True:
      self.sensorValue = self.getData()
      sensorLogger.info(self.sensorValue)
      samples.append(self.sensorValue)

      minVal = self.avarage - round((self.avarage * avg_percentage) / 100)
      maxVal = self.avarage + round((self.avarage * avg_percentage) / 100)
      counter += 1 if self.sensorValue < minVal or self.sensorValue > maxVal else 0

      if len(samples) >= sample_size:
        if(counter >= alarm_threshold):
          logger.warning("Sensor Alarm!!!")

        samples = []
        counter = 0

  def getValue(self):
    return self.sensorValue

  def calibrate(self):
    logger.info("Sensor calibrating...")

    for num in range(0, self.samples):
      self.avarage += self.getData()
    self.avarage /= self.samples

    return self.avarage

  def getData(self):
    acc = self.mpu.read_accelerometer(gravity=True)
    xValue = acc["x"] + 2
    yValue = acc["y"] + 2
    zValue = acc["z"] + 2

    total  = xValue * yValue * zValue
    total  = round(total * 10000)

    sleep(0.01)

    return total