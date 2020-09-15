import json
import telegram
import os
import logging
import secret


# Logging is cool!
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
        chat_id = update.message.chat.id
        text = update.message.text
        user = update.message.from_user
        callback = update.callback_query

        if callback:
          bot.sendMessage(chat_id=chat_id, text=callback.data)

        elif text == '/start':
            text = start()
            bot.sendMessage(chat_id=chat_id, text=text)

        elif text == '/takeTemp':
          reply_markup = takeTemp()
          bot.sendMessage(chat_id=chat_id, text="Write your temperature here:", reply_markup=reply_markup)

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
  buttons = []
  temperatures = ['36.0','36,5', '37.0', '37.5']
  for element in temperatures:
    buttons.append(telegram.InlineKeyboardButton(text=element, callback_data=element))
  reply_markup = telegram.InlineKeyboardMarkup(buttons)
  return(reply_markup)
