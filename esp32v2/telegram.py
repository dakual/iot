import urequests

async def telegram_send(text, cnf):
  url  = 'https://api.telegram.org/bot' + cnf.TELEGRAM["token"]
  data = {'chat_id': cnf.TELEGRAM["chatid"] , 'text': text}
  try:
    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = urequests.get(url + '/sendMessage', json=data, headers=headers)
    response.close()

    print("Telegram notification has been sent!")
  except Exception as ex:
    raise ex