import {botToken} from './secret.js'


const rp = require('request-promise');
async function getShortUrl(longUrl) {
  const options = {
    method: 'POST',
    uri: 'https://cleanuri.com/api/v1/shorten',
    form: {
      url: String(longUrl).trim()
    },
    json: true
  };

  return rp(options);
}

async function sendToUser(chat_id, text) {
  const options = {
    method: 'GET',
    uri: 'https://api.telegram.org/bot' + botToken + '/sendMessage',
    qs: {
      chat_id,
      text
    }
  };

  return rp(options);
}

module.exports.tufftimes = async event => {
  const body = JSON.parse(event.body);
  const {chat, text} = body.message;

  if (text) {
    let message = '';
    try {
      const result = await getShortUrl(text);
      message = 'Input: ' + text + ',\nShort: ' + result.result_url;
    } catch (error) {
      message = 'Input: ' + text + '\nError: ' + (error.message);
    }

    await sendToUser(chat.id, message);
  } else {
    await sendToUser(chat.id, 'Text message is expected.');
  }

  return { statusCode: 200 };
};



// help me