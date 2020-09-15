import json
import telegram
import os
import logging
import secret
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin

cred = credentials.Certificate('serviceAccountKey.json')
config = {
  "apiKey": secret.firebaseAPIKey,
  "authDomain": secret.authDomain,
  "databaseURL": secret.databaseURL,
  "projectId": "temptaking-b16aa",
  "storageBucket": secret.storageBucket,
  "messagingSenderId": "518980129989",
  "appId": "1:518980129989:web:bda2018de7d490ff24ccac",
  "measurementId": "G-RS3CCBFC32"
}
firebase = firebase_admin.initialize_app(cred, config)
ref = db.reference('/')

logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}


def configure_telegram():
    """
    Configures the bot with a Telegram Token.
    Returns a bot instance.
    """

    TELEGRAM_TOKEN = secret.botToken
    if not TELEGRAM_TOKEN:
        logger.error('The TELEGRAM_TOKEN must be set')
        raise NotImplementedError

    return telegram.Bot(TELEGRAM_TOKEN)


def webhook(event, context):
    """
    Runs the Telegram webhook.
    """

    bot = configure_telegram()
    logger.info('Event: {}'.format(event))

    if event.get('httpMethod') == 'POST' and event.get('body'): 
        logger.info('Message received')
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
          
        if update.callback_query:
          callback = update.callback_query
          text = callback.data
          query_id = callback.id

          bot.answerCallbackQuery(callback_query_id=query_id, text=text)
        else:
          text = update.message.text
          chat_id = update.message.chat.id

          if text == '/start':
              text = start()
              bot.sendMessage(chat_id=chat_id, text=text)

          elif text == '/takeTemp':
            reply_markup = takeTemp()
            bot.sendMessage(chat_id=chat_id, text="Write your temperature here:", reply_markup=reply_markup)
          
          elif text == '/db':
            ref.push({
              'color': 'purple',
              'width': 7,
              'height': 8,
              'length': 6
          })
            bot.sendMessage(chat_id=chat_id, text="Updated db")

        logger.info('Message sent')

        return OK_RESPONSE

    return ERROR_RESPONSE


def set_webhook(event, context):
    """
    Sets the Telegram bot webhook.
    """

    logger.info('Event: {}'.format(event))
    bot = configure_telegram()
    url = 'https://{}/{}/'.format(
        event.get('headers').get('Host'),
        event.get('requestContext').get('stage'),
    )
    webhook = bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE


def start():
  return("""Hello, use this bot to record your temperature!""")

def takeTemp():
  IKM = InlineKeyboardMarkup(
    inline_keyboard = [
      [
        InlineKeyboardButton(36.0, callback_data="36.0"),
        InlineKeyboardButton(36.5, callback_data="36.5"),
        InlineKeyboardButton(37.0, callback_data="37.0")
      ],
      [
        InlineKeyboardButton(37.5, callback_data="37.5"),
        InlineKeyboardButton(5, callback_data="5"),
        InlineKeyboardButton(6, callback_data="6")
      ],
      [
        InlineKeyboardButton(7, callback_data="7"),
        InlineKeyboardButton(8, callback_data="8"),
        InlineKeyboardButton(9, callback_data="9")
      ],
      [
        InlineKeyboardButton(".", callback_data="."),
        InlineKeyboardButton(0, callback_data="0"),
        InlineKeyboardButton("#", callback_data="#")
      ]
    ]
  )
  return(IKM)