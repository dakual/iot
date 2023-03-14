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
  calibrationSampleSize = 1000
  calibrationAvarage = 0
  
  alarmThreshold = 50
  alarmPercentage = 1
  alarmSampleSize = 200
  alarmState = 0

  def __init__(self):
    threading.Thread.__init__(self)

    logger.info("Sensor starting...")
    self.mpu = MPU6050(0x68)
    self.mpu.reset()
    self.mpu.power_manage(temp_sense_disable=True)
    self.calibrate()

  def run(self):
    logger.info("Sensor started.")

    samples = []
    counter = 0
    while True:
      sensorValue = self.getData()
      sensorLogger.info(sensorValue)

      minVal = self.calibrationAvarage - round((self.calibrationAvarage * self.alarmPercentage) / 100)
      maxVal = self.calibrationAvarage + round((self.calibrationAvarage * self.alarmPercentage) / 100)
      counter += 1 if sensorValue < minVal or sensorValue > maxVal else 0
      
      samples.append(sensorValue)
      if len(samples) >= self.alarmSampleSize:
        if(counter >= self.alarmThreshold):
          self.alarm(1)
        else:
          if self.alarmState == 1: self.alarm(0)

        samples = []
        counter = 0

  def calibrate(self):
    logger.info("Sensor calibrating...")

    for num in range(0, self.calibrationSampleSize):
      self.calibrationAvarage += self.getData()
    self.calibrationAvarage /= self.calibrationSampleSize

    return self.calibrationAvarage

  def getData(self):
    accVal = self.mpu.read_accelerometer(gravity=True)
    xValue = accVal["x"] + 2
    yValue = accVal["y"] + 2
    zValue = accVal["z"] + 2

    total  = xValue * yValue * zValue
    total  = round(total * 10000)

    sleep(0.01)

    return total
  
  def alarm(self, state):
    self.alarmState = state
    logState = "active" if state == 1 else "inactive"
    logger.warning(f"Alarm ({logState})")