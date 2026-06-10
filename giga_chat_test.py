import requests
import os
from dotenv import load_dotenv
import logging

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

logging.basicConfig(level=logging.INFO)

load_dotenv()


# --------------------- получение Access token для возможности осуществлять запросы -------------------


def get_access_token_giga()-> str:
    """Возвращает access_token для giga_chat"""

    try:
        AUTH_KEY = os.getenv('AUTHORIZATION_KEY')
        print(f'{AUTH_KEY=}')


        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        payload={
        'scope': 'GIGACHAT_API_CORP'
        }
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '30848901-8002-45cd-ae07-81bb0049fa2a',
        'Authorization': f'Basic {AUTH_KEY}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        response_data = response.json()
        
        access_token = response_data.get('access_token')
        logging.info(f'{access_token=}')
        return access_token

        
    except Exception as e:
        logging.error(f'[ERROR][get_access_token_giga] При попытке получения access_token произошла ошибка: {e}')
        return None
        

# --------------------- вариант отправки запроса на получение списка моделей с использованием Access token -------------------

# '''
# access_token = get_access_token_giga()

# url = "https://gigachat.devices.sberbank.ru/api/v1/models"


# payload={}
# headers = {
#   'Accept': 'application/json',
#   'Authorization': f'Bearer {access_token}'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# print(f'Список моделей {response.text}')

# '''

# ----------------------- Получение ответов на запросы с использованием различных моделей ------------------------

AUTH_KEY = os.getenv('AUTHORIZATION_KEY')
print(f'{AUTH_KEY=}')


with GigaChat(credentials=AUTH_KEY, verify_ssl_certs=False, scope='GIGACHAT_API_CORP', model='GigaChat-2-Max') as giga:
  response=giga.chat(
      Chat(
        messages=[
              Messages(
                  role=MessagesRole.USER,
                  content="Как ты оцениваешь свои возможности по сравнению с Claude "
              )
          ]
      )
  )

print(response.choices[0].message.content)
