import threading, socket

class TCP(threading.Thread):

  def __init__(self, seismograph):
    threading.Thread.__init__(self)

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind(('', 1025))
    self.sock.listen(5)

    self.seis = seismograph

  def run(self):
    while True:
      newSocket, address = self.sock.accept()      
      while True:
        try:
          data = self.seis.getData()

          newSocket.send(str(data).encode())
          newSocket.send(b'\r\n')
        except Exception as e:
          newSocket.close()
          break
