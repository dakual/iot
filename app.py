from MPU6050 import MPU6050
import time
import socket
import logging
import sys
import threading
import select, queue
from logging.handlers import RotatingFileHandler


sensor_logger  = logging.getLogger("sensor")
# file_handler   = logging.FileHandler('logs.log', mode="a")
file_handler   = RotatingFileHandler(
  filename = 'logs.log', 
  mode = 'a',
  maxBytes = 5*1024*1024,
  backupCount = 10,
  encoding = None,
  delay = False
)

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
sensor_logger.addHandler(file_handler)
sensor_logger.setLevel(logging.INFO)


logger  = logging.getLogger("stdout")
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(stdout_handler)
logger.setLevel(logging.INFO)




class Seismograph():
  samples = 1000
  avarage = 0
  sensorValue = 0

  def __init__(self):
    logger.info("Sensor starting...")

    self.mpu = MPU6050(0x68)
    self.mpu.reset()
    self.mpu.power_manage()
    self.mpu.accel_config()

    for num in range(0, 10):
      self.mpu.read_accelerometer(gravity=True)

  def start(self):
    alarm_threshold = 25
    avg_percentage  = 2
    sample_size     = 350
    
    self.calibrate()
    
    logger.info("Sensor started.")

    samples = []
    counter = 0
    while True:
      Seismograph.sensorValue = self.getData()
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
    return Seismograph.sensorValue

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

    return total
  


class Server(threading.Thread):
  inputs  = []
  outputs = []
  message_queues = {}

  def __init__(self, host, port, sis):
    threading.Thread.__init__(self)

    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server.setblocking(0)
    self.server.bind((host, port))
    self.server.listen(5)
    self.inputs.append(self.server)
    self.seismograph = sis

  def run(self):
    logger.info("Client server started.")

    while self.inputs:
        readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
        for s in readable:
            if s is self.server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                self.inputs.append(connection)
                self.message_queues[connection] = queue.Queue()

                logger.info("New client connected: %s:%s" % (connection.getpeername()))

                # while True:
                #   self.message_queues[connection].put(str(self.seismograph.getValue()).encode())
                #   self.message_queues[connection].put(b'\r\n')
                #   self.outputs.append(connection)
            else:                     
                data = s.recv(1024)
                if data:
                    self.message_queues[s].put(data)
                    if s not in self.outputs:
                        self.outputs.append(s)
                else:
                    if s in self.outputs:
                        self.outputs.remove(s)
                    self.inputs.remove(s)
                    logger.info("Client disconnected: %s:%s" % (s.getpeername()))
                    s.close()
                    del self.message_queues[s]
                    

        for s in writable:
            try:
                next_msg = self.message_queues[s].get_nowait()
            except queue.Empty:
                self.outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            self.inputs.remove(s)
            if s in self.outputs:
                self.outputs.remove(s)
            s.close()
            del self.message_queues[s]



if __name__ == '__main__':
  logger.info("Application started.")

  sis    = Seismograph()
  server = Server("", 1025, sis)
  try:
    server.start()    
    sis.start()
  except KeyboardInterrupt:
    print("Keyboard interrupt")
    sys.exit(1)



  # alarm_threshold = 25
  # avg_percentage  = 2
  # sample_size     = 350

  # logger.info("Sensor starting...")
  # sis = seismograph()
  # logger.info("Sensor calibrating...")
  # sis.calibrate()
  # logger.info("Sensor started.")

  # samples = []
  # counter = 0
  # while True:
  #   data = sis.getData()
  #   samples.append(data)

  #   sisAvg = sis.getAvg()
  #   minVal = sisAvg - round((sisAvg * avg_percentage) / 100)
  #   maxVal = sisAvg + round((sisAvg * avg_percentage) / 100)
  #   counter += 1 if data < minVal or data > maxVal else 0

  #   if len(samples) >= sample_size:
  #     if(counter >= alarm_threshold):
  #       logger.warning("Sensor Alarm!!!")

  #     samples = []
  #     counter = 0

    

  # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  # sock.bind(('', 1025))
  # sock.listen(5)

  # try:
  #   seis = seismograph()
  #   seis.calibrate()

  #   while True:
  #     newSocket, address = sock.accept()
  #     stdout_logger.info("Connected from: %s"  % (address,))
      
  #     while 1:
  #       try:
  #         tot = seis.getData()
          
  #         newSocket.send(str(tot).encode())
  #         newSocket.send(b'\r\n')

  #         sensor_logger.info(tot)

  #         time.sleep(0.05)
  #       except Exception as e:
  #         break

  #     newSocket.close()
  #     stdout_logger.info("Disconnected from: %s"  % (address,))
  # finally:
  #   sock.close()
