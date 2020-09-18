import json
import telegram
import os
import logging
import secret
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin
import datetime
from pytz import timezone

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
    date = datetime.datetime.now(timezone('Asia/Singapore')).date().strftime("%d:%m:%Y")
    time = datetime.datetime.now(timezone('Asia/Singapore')).time().strftime("%H:%M:%S")

    if event.get('httpMethod') == 'POST' and event.get('body'):
        logger.info('Message received')
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
        
        # Checks if message is a callback query
        if update.callback_query:
          callback = update.callback_query
          text = callback.data
          query_id = callback.id
          user = callback.from_user
          name = user.first_name + " " + user.last_name
          inline_id = callback.inline_message_id
          message = callback.message
          chat_id = message.chat.id

          count_ref = db.reference(date).child(name).child("count").get()
          count = count_ref["count"]
          ref = db.reference(date).child(name)
          
          # Callback after selecting temperature
          if "temp" in text:
            ref.update({
              count : {
                "temp: " + time : text.split(": ")[1]
              }
            })
            bot.editMessageText(chat_id=chat_id, message_id=message.message_id, text="You submitted your temperature as " + text.split(": ")[1], reply_markup = InlineKeyboardMarkup([]))
            bot.answerCallbackQuery(callback_query_id=query_id)
            reply_markup = reportingSick()
            bot.sendMessage(chat_id=chat_id, text="Will you be reporting sick outside today?:", reply_markup=reply_markup)

          # Callback after submitting MC query
          elif "sick" in text:
            ref.child(str(count)).update({
              "sick " + time : text.split(": ")[1]
            })
            bot.editMessageText(chat_id=chat_id, message_id=message.message_id, text="You are: " + text.split(": ")[1], reply_markup = InlineKeyboardMarkup([]))
            bot.answerCallbackQuery(callback_query_id=query_id)
            reply_markup = symptoms()
            bot.sendMessage(chat_id=chat_id, text="Please select any symptoms you might have (click again to deselect) and click the submit button when you are done. Click submit if you have no symptoms: \nSymptoms:", reply_markup=reply_markup)

          # Callback after selecting symptoms without submitting
          elif "continue" in text:
            symptom = text.split(": ")[1]
            if symptom in message.text:
              updated_text = message.text.replace("\n" + symptom, "")
            else:
              updated_text = message.text + "\n" + symptom
            reply_markup = symptoms()
            bot.editMessageText(chat_id=chat_id, message_id=message.message_id, text=updated_text, reply_markup = reply_markup)

          # Callback after submitting symptoms
          elif "submit" in text:
            final_text = str(message.text.split("\nSymptoms:")[-1])
            if final_text != '':
              final_text = final_text.replace("\n", "", 1)
              final_text = final_text.replace("\n", ", ")
            else:
              final_text = "None"
            ref.child(str(count)).update({
              "symptoms " + time : final_text
            })
            bot.editMessageText(chat_id=chat_id, message_id=message.message_id, text="You have the following symptoms: " + final_text, reply_markup = InlineKeyboardMarkup([]))


        # Checks if message is initiated by user
        else:
          message = update.message
          text = message.text
          chat_id = message.chat.id
          user = message.from_user
          name = user.first_name + " " + user.last_name

          if text == '/start':
              text = start()
              bot.sendMessage(chat_id=chat_id, text=text)

          elif text == '/takeTemp':
            reply_markup = takeTemp()
            ref = db.reference(date).child(name).child("count")
            count_dict = ref.get()
            if count_dict:
              ref.update({
                "count" : count_dict["count"] + 1
              })
            else:
              ref.update({
                "count" : 1
              })
            bot.sendMessage(chat_id=chat_id, text="Temperature Reading:", reply_markup=reply_markup)

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
        InlineKeyboardButton(36.0, callback_data="temp: 36.0"),
        InlineKeyboardButton(36.1, callback_data="temp: 36.1"),
        InlineKeyboardButton(36.2, callback_data="temp: 36.2"),
        InlineKeyboardButton(36.3, callback_data="temp: 36.3"),
        InlineKeyboardButton(36.4, callback_data="temp: 36.4"),
      ],
      [
        InlineKeyboardButton(36.5, callback_data="temp: 36.5"),
        InlineKeyboardButton(36.6, callback_data="temp: 36.6"),
        InlineKeyboardButton(36.7, callback_data="temp: 36.7"),
        InlineKeyboardButton(36.8, callback_data="temp: 36.8"),
        InlineKeyboardButton(36.9, callback_data="temp: 36.9"),
      ],
      [
        InlineKeyboardButton(37.0, callback_data="temp: 37.0"),
        InlineKeyboardButton(37.1, callback_data="temp: 37.1"),
        InlineKeyboardButton(37.2, callback_data="temp: 37.2"),
        InlineKeyboardButton(37.3, callback_data="temp: 37.3"),
        InlineKeyboardButton(37.4, callback_data="temp: 37.4"),
      ],
      [
        InlineKeyboardButton(37.5, callback_data="temp: 37.5"),
        InlineKeyboardButton(37.6, callback_data="temp: 37.6"),
        InlineKeyboardButton(37.7, callback_data="temp: 37.7"),
        InlineKeyboardButton(37.8, callback_data="temp: 37.8"),
        InlineKeyboardButton(37.9, callback_data="temp: 37.9"),
      ]
    ]
  )
  return IKM

def reportingSick():
  IKM = InlineKeyboardMarkup(
    inline_keyboard = [
      [
        InlineKeyboardButton("Yes", callback_data="sick: Reporting sick outside today"),
        InlineKeyboardButton("No", callback_data="sick: Not reporting sick"),
      ],
      [
        InlineKeyboardButton("Currently on MC", callback_data="sick: Currently on MC"),
      ]
    ]
  )
  return IKM



def symptoms():
  IKM = InlineKeyboardMarkup(
    inline_keyboard = [
      [
        InlineKeyboardButton("Fever", callback_data="continue: Fever"),
        InlineKeyboardButton("Runny Nose", callback_data="continue: Runny Nose"),
        InlineKeyboardButton("Cough", callback_data="continue: Cough"),
      ],
      [
        InlineKeyboardButton("Breathlessness", callback_data="continue: Breathlessness"),
        InlineKeyboardButton("Sore Throat", callback_data="continue: Sore Throat"),
      ],
      [
        InlineKeyboardButton("Submit", callback_data="submit"),
      ]
    ]
  )
  return IKM

