import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Function to retrieve and display the channel ID
async def get_channel_id(update: Update, context: CallbackContext) -> None:
    channel_username = "@rickbot12"  # Replace with your channel's username

    try:
        chat = await context.bot.get_chat(channel_username)
        channel_id = chat.id
        await update.message.reply_text(f"The channel ID for {channel_username} is: {channel_id}")
    except Exception as e:
        logger.error(f"Failed to retrieve channel ID: {e}")
        await update.message.reply_text("Failed to retrieve channel ID. Please check the channel username and try again.")

def main():
    # Use environment variable for bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables.")
        return

    application = Application.builder().token(token).build()

    # Handler to trigger channel ID retrieval
    application.add_handler(CommandHandler("getchannelid", get_channel_id))

    logger.info("Starting bot...")

    # Start the bot and run until stopped
    application.run_polling()

if __name__ == '__main__':
    main()
