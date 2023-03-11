#!/usr/bin/env python3
import json
from flask import Flask, render_template
from flask_sock import Sock
from datetime import datetime
from seismic import Seismograph
from tcpdump import TCP


app  = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
sock = Sock(app)
sis  = Seismograph()
tcp  = TCP(sis)


@app.route('/')
def index():
  return render_template('index.html')

@sock.route('/ws')
def seismicValues(sock):
  while True:
    value = sis.getData()
    date  = datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")
    try:
      sock.send(json.dumps({'value': value, "date": date}))
    except:
      break


if __name__ == '__main__':
  sis.start()
  tcp.start()

  app.run(host="0.0.0.0", port=5000)
