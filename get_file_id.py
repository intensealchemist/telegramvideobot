import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment variable
BOT_TOKEN = os.getenv("FILE_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to handle /get_file_id command or incoming messages
async def get_file_id(update: Update, context: CallbackContext) -> None:
    message = update.message or update.channel_post

    if message:
        logger.info(f"Received a message from chat {message.chat.id} (username: {message.chat.username})")

        # Check for various file types
        if message.video:
            file_id = message.video.file_id
            file_type = "Video"
        elif message.photo:
            file_id = message.photo[-1].file_id  # Get the highest resolution photo
            file_type = "Photo"
        elif message.document:
            file_id = message.document.file_id
            file_type = "Document"
        elif message.audio:
            file_id = message.audio.file_id
            file_type = "Audio"
        elif message.voice:
            file_id = message.voice.file_id
            file_type = "Voice Message"
        elif message.sticker:
            file_id = message.sticker.file_id
            file_type = "Sticker"
        else:
            await message.reply_text("Please send a supported file type to get its file_id.")
            return

        logger.info(f"Sending {file_type} file_id: {file_id}")
        await message.reply_text(f"{file_type} file_id: {file_id}")
    else:
        logger.warning("Received an update that is not a message or channel post.")

# Adding the command handler to your bot in the main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handle /get_file_id command
    application.add_handler(CommandHandler("get_file_id", get_file_id))
    
    # Handle all messages to get file IDs
    application.add_handler(MessageHandler(filters.ALL, get_file_id))

    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
