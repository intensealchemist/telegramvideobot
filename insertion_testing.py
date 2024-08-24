import sqlite3
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to set up the database
def setup_database():
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to handle /get_file_id command or incoming messages from the specified channel
async def get_file_id(update: Update, context: CallbackContext) -> None:
    message = update.message or update.channel_post

    if message:
        # Specify your channel username
        channel_username = '@rickbot12'  # Replace with your channel's username

        # Check if the message is from the specified channel
        if message.chat.username == channel_username.lstrip('@'):
            # Check for various file types and store the file_id
            file_id = None

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

            if file_id:
                # Insert file_id and file_type into the database
                conn = sqlite3.connect('videos.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO videos (file_id) VALUES (?)", (file_id,))
                conn.commit()
                conn.close()

                await message.reply_text(f"{file_type} file_id: {file_id} has been stored in the database.")
                logger.info(f"Stored {file_type} with file_id: {file_id} in the database.")
            else:
                await message.reply_text("Please send a supported file type to get its file_id.")
        else:
            logger.info(f"Ignored a message from another chat: {message.chat.username}")
    else:
        logger.warning("Received an update that is not a message or channel post.")

# Adding the command handler to your bot in the main function
def main():
    # Set up the database
    setup_database()

    application = Application.builder().token("7262552574:AAEjZCYAa-3PGgpl0X_o6lh4457X0pfqPAE").build()

    # Handle /get_file_id command
    application.add_handler(CommandHandler("get_file_id", get_file_id))
    
    # Handle messages from the channel
    application.add_handler(MessageHandler(filters.ALL, get_file_id))

    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
