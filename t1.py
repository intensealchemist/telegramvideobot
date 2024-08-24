import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.ext import Updater, CallbackContext
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
block_level = 0
mess_deleted = False
bad_words = ["bad word", "badword"]
very_bad_words = ["very bad word", "verybadword"]

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(f"Hello! I'm your Bot, {user.first_name}!")

async def handle_message(update: Update, context: CallbackContext):
    global block_level, mess_deleted
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()
    user = update.message.from_user
    first_name = user.first_name
    last_name = user.last_name

    # Time of the message
    year, month, day = update.message.date.year, update.message.date.month, update.message.date.day
    hour, minute, second = update.message.date.hour, update.message.date.minute, update.message.date.second

    # Display message info
    logger.info(f"Received a '{message_text}' message in chat {chat_id} from {first_name} {last_name} at {hour}:{minute}:{second} on {year}/{month}/{day}")

    # Check if the user is a member of the group/channel
    chat_member = await context.bot.get_chat_member(chat_id="@zetalvx", user_id=user.id)
    chat_member2 = await context.bot.get_chat_member(chat_id="@tutorialbotprogramming", user_id=user.id)

    if chat_member.status in ['left', 'kicked'] or chat_member2.status in ['left', 'kicked']:
        # Ask the user to join the channel
        keyboard = [[
            InlineKeyboardButton("Channel 1", url="https://t.me/zetalvx"),
            InlineKeyboardButton("Channel 2", url="https://t.me/tutorialbotprogramming")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Before using the bot, please follow these channels. Click /home to continue.", reply_markup=reply_markup)
        return

    # Handle vulgarity filter
    if message_text == "/vulgarity":
        block_level = (block_level + 1) % 3
        block_states = ["Block disabled", "Medium block", "Hard block"]
        await update.message.reply_text(f"Vulgarity: \"{block_states[block_level]}\".")
        return

    # Check bad words
    if block_level >= 2:
        for bad_word in bad_words:
            if bad_word in message_text:
                mess_deleted = True
                await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
                await update.message.reply_text(f"{first_name} {last_name}, you can't say that!")
                return

    # Check very bad words
    if block_level >= 1:
        for very_bad_word in very_bad_words:
            if very_bad_word in message_text:
                mess_deleted = True
                await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
                await update.message.reply_text(f"{first_name} {last_name}, you can't say that!")
                return

    # Specific commands or messages
    if message_text == "hello":
        await update.message.reply_text(f"Hello {first_name} {last_name}!")

    elif message_text == "meme":
        await context.bot.send_photo(chat_id=chat_id, photo="https://i.redd.it/uhkj4abc96r61.jpg", caption="<b>MEME</b>", parse_mode="HTML")

    elif message_text == "sound":
        await context.bot.send_audio(chat_id=chat_id, audio="https://github.com/TelegramBots/book/raw/master/src/docs/audio-guitar.mp3")

    elif message_text == "countdown":
        await context.bot.send_video(chat_id=chat_id, video="https://raw.githubusercontent.com/TelegramBots/book/master/src/docs/video-countdown.mp4", supports_streaming=True)

    elif message_text == "album":
        await context.bot.send_media_group(chat_id=chat_id, media=[
            {"type": "photo", "media": "https://cdn.pixabay.com/photo/2017/06/20/19/22/fuchs-2424369_640.jpg"},
            {"type": "photo", "media": "https://cdn.pixabay.com/photo/2017/04/11/21/34/giraffe-2222908_640.jpg"},
        ])

    elif message_text == "doc":
        await context.bot.send_document(chat_id=chat_id, document="https://github.com/TelegramBots/book/raw/master/src/docs/photo-ara.jpg", caption="<b>Ara bird</b>. <i>Source</i>: <a href=\"https://pixabay.com\">Pixabay</a>", parse_mode="HTML")

    elif message_text == "gif":
        await context.bot.send_animation(chat_id=chat_id, animation="https://raw.githubusercontent.com/TelegramBots/book/master/src/docs/video-waves.mp4", caption="Waves")

    elif message_text == "poll":
        poll_message = await context.bot.send_poll(chat_id=chat_id, question="How are you?", options=["Good!", "I could be better.."])
        context.user_data['poll_id'] = poll_message.message_id

    elif message_text == "close poll" and 'poll_id' in context.user_data:
        poll_id = context.user_data['poll_id']
        await context.bot.stop_poll(chat_id=chat_id, message_id=poll_id)

    elif message_text == "send me the phone number of anna":
        await context.bot.send_contact(chat_id=chat_id, phone_number="+1234567890", first_name="Anna", last_name="Rossi")

    elif message_text == "roma location":
        await context.bot.send_venue(chat_id=chat_id, latitude=41.9027835, longitude=12.4963655, title="Rome", address="Rome, via Daqua 8, 08089")

    elif message_text == "send me a location":
        await context.bot.send_location(chat_id=chat_id, latitude=41.9027835, longitude=12.4963655)

async def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    application = Application.builder().token("7262552574:AAEjZCYAa-3PGgpl0X_o6lh4457X0pfqPAE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
