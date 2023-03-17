import urequests
import secrets

async def telegram_send(text):
  url  = 'https://api.telegram.org/bot' + secrets.TELEGRAM_TOKEN
  data = {'chat_id': secrets.TELEGRAM_CHATID , 'text': text}
  try:
    headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = urequests.post(url + '/sendMessage', json=data, headers=headers)
    response.close()
    return True
  except:
    return False