import telegram, logging, os
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def start(update, context):
    custom_keyboard = [[KeyboardButton("Option A"), KeyboardButton("Option B")], [KeyboardButton("Option C")], [KeyboardButton("Kirim Pesan")]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    update.message.reply_text("Hi there! What would you like to do today?",
                             reply_markup=reply_markup)
    return CHOOSING
    
# Retrieve chat ID, hidden command
def get_chat_id(update, context):
    chat_id = update.message.chat_id
    logger.info(f"Chat ID: {chat_id}")

def regular_choice(update, context):
    message = update.message.text
    context.user_data['choice'] = message
    if message == 'Option A':
        update.message.reply_text("You selected option A.")
    elif message == 'Option B':
        update.message.reply_text("You selected option B.")
    elif message == 'Option C':
        update.message.reply_text("You selected option C.")
    elif message == 'Kirim Pesan':
        update.message.reply_text("Kirim pesan ke bot. Pesan yang kamu kirim akan disampaikan kepada pengelola bot. Jika diperlukan pengelola akan menghubungimu. Tulis pesanmu.")
        return TYPING_REPLY
    
def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Good thing, I will forward it to the team.")
    context.bot.forward_message(chat_id=os.environ.get('FWCHATID'), from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    return CHOOSING

def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("Terima kasih telah menggunakan Bot ini. Mulai lagi dengan /start")
    user_data.clear()
    return ConversationHandler.END
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
def main():
    updater = Updater(token=os.environ.get('TOKEN'), use_context=True)

    dp = updater.dispatcher
    
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Option A|Option B|Option C|Kirim Pesan)$'),
                                      regular_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('getchatid', get_chat_id))

    # log all errors
    dp.add_error_handler(error)
    
    # Start app
    updater.start_polling()
    # Stay until CTRL+C
    updater.idle()

if __name__ == '__main__':
    main()