import urequests

async def telegram_send(text, cnf):
  url  = 'https://api.telegram.org/bot' + cnf.TELEGRAM["token"]
  data = {'chat_id': cnf.TELEGRAM["chatid"] , 'text': text}
  try:
    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = urequests.post(url + '/sendMessage', json=data, headers=headers)
    response.close()
  except Exception as ex:
    raise ex