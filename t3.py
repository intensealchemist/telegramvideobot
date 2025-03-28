import logging
import sqlite3
import random
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Channel Username (replace with your actual channel username)
CHANNEL_USERNAME = "@Teraboxjoinfirst"
VIDEO_CHANNEL_USERNAME = "@terabox1212"
ACTIVITY_CHANNEL_USERNAME = "@teraboxuseractivity"

# Initialize database and ensure tables exist
def init_db():
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            plan TEXT NOT NULL,
            daily_count INTEGER NOT NULL,
            last_access TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


async def log_user_activity(context, message: str) -> None:
    try:
        # Send a message to the channel using the username
        await context.bot.send_message(chat_id=ACTIVITY_CHANNEL_USERNAME, text=message)
        logger.info(f"User activity logged: {message}")
    except Exception as e:
        logger.error(f"Failed to log user activity: {e}")

async def handle_video(update: Update, context) -> None:
    message = update.channel_post

    if message and message.chat.username == VIDEO_CHANNEL_USERNAME.lstrip('@'):
        file_id = None
        file_type = "Video"  # Assuming you're only handling video files

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
            try:
                # Insert file_id and file_type into the database
                conn = sqlite3.connect('videos.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO videos (file_id, file_type) VALUES (?, ?)", (file_id, file_type))
                conn.commit()
                conn.close()

                logger.info(f"Stored {file_type} with file_id: {file_id} in the database.")
            except sqlite3.Error as e:
                logger.error(f"SQLite error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            logger.info("Received a message without a valid file to store.")
    else:
        logger.warning("Received an update that is not from the specified channel or does not contain a video.")

async def start(update: Update, context) -> None:
    user_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "there"

    logger.info(f"User {user_id} ({user_name}) started the bot.")
    await log_user_activity(context, f"{user_name} (ID: {user_id}) started the bot.")

    with sqlite3.connect('videos.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (user_id, plan, daily_count, last_access) VALUES (?, ?, ?, ?)",
                (user_id, 'free', 0, datetime.datetime.utcnow())
            )
            conn.commit()

    # Create buttons
    keyboard = [
        [KeyboardButton("Plan Status 📝"), KeyboardButton("Get Video 🍒")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    # Send welcome message with the "Get Video" button
    await update.message.reply_text(f'Heya {user_name}🔥\nReady for some fun?\nClick on the "Get Video 🍒" button to begin.', reply_markup=reply_markup)
    await update.message.reply_text(f'Hello!\nYou can contact us using this bot.', reply_markup=reply_markup)

async def buy(update: Update, context) -> None:
    user_name = update.effective_chat.first_name or "there"
    user_id = update.effective_chat.id

    logger.info(f"User {user_id} ({user_name}) initiated the buy command.")
    await log_user_activity(context, f"{user_name} (ID: {user_id}) initiated the buy command.")


    # Define the list of plans as inline buttons
    keyboard = [
        [InlineKeyboardButton("₹199", callback_data='plan_199')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message along with the inline keyboard
    await update.message.reply_text(
        f'Want to unlock more videos per day?\n\n'
        f'Try our paid plan, bet you won\'t regret buying it.',
        reply_markup=reply_markup
    )

async def get_video(update: Update, context) -> None:
    user_id = update.effective_chat.id
    chat_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "User"

    logger.debug(f"User {user_id} triggered Get Video")

    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        logger.debug(f"Membership status for user {user_id}: {member.status}")
        if member.status in ['left', 'kicked']:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Please join our channel first: {CHANNEL_USERNAME}")
            return
    except Exception as e:
        logger.error(f"Error checking channel membership: {e}")
        await context.bot.send_message(chat_id=chat_id, text="An error occurred while checking your channel subscription.")
        return
    
    await log_user_activity(context, f"{user_name} (ID: {user_id}) requested a video.")

    # Database operations
    with sqlite3.connect('videos.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT plan, daily_count, last_access FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            await context.bot.send_message(chat_id=chat_id, text="User not found in the database.")
            return

        # Reset daily count if it's a new day
        last_access = datetime.datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S.%f')
        if (datetime.datetime.utcnow() - last_access).days >= 1:
            cursor.execute("UPDATE users SET daily_count = 0 WHERE user_id = ?", (user_id,))
            conn.commit()

        # Check for free plan limits
        if user[0] == 'free' and user[1] >= 3:
            keyboard = [
                [InlineKeyboardButton("₹199", callback_data='plan_199')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id,
                                           text="You can only access 3 free videos daily. To unlock more daily videos, try the plan below.",
                                           reply_markup=reply_markup)
            return

        # Get a random video from the database
        cursor.execute("SELECT file_id FROM videos ORDER BY RANDOM() LIMIT 1")
        video = cursor.fetchone()

        if video is None:
            await context.bot.send_message(chat_id=chat_id, text="No videos available.")
            return

        # Send video
        try:
            await context.bot.send_video(chat_id=chat_id, video=video[0], protect_content=True)

            # Update daily count and last access time
            cursor.execute(
                "UPDATE users SET daily_count = daily_count + 1, last_access = ? WHERE user_id = ?",
                (datetime.datetime.utcnow(), user_id)
            )
            conn.commit()

            await log_user_activity(context, f"{user_name} (ID: {user_id}) received a video.")

        except Exception as e:
            logger.error(f"Failed to send video: {e}")
            await context.bot.send_message(chat_id=chat_id, text="An error occurred while sending the video.")

async def handle_reply_keyboard(update: Update, context) -> None:
    user_message = update.message.text
    user_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "User"

    logger.info(f"User {user_id} ({user_name}) clicked on '{user_message}'.")
    await log_user_activity(context, f"{user_name} (ID: {user_id}) clicked on '{user_message}'.")

    logger.debug(f"Received message: {user_message}")

    # Dictionary to map button text to the corresponding function
    actions = {
        "Plan Status 📝": plan_status,
        "Get Video 🍒": get_video,
    }

    # Call the appropriate function based on the message text
    if user_message in actions:
        logger.debug(f"Executing action for message: {user_message}")
        await actions[user_message](update, context)
    else:
        logger.warning(f"No action mapped for message: {user_message}")

async def plan_selected(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    user_name = query.from_user.first_name or "User"

    logger.debug(f"User {query.from_user.id} selected a plan.")
    logger.info(f"User {user_id} ({user_name}) selected a plan.")
    await log_user_activity(context, f"{user_name} (ID: {user_id}) selected a plan.")

    # Image to be sent (replace with actual image file_id)
    image_file_id = "AgACAgUAAxkBAAICD2a7Cgiki5B-L_J2uIHMyrwSRNRTAALMvTEbV_LYVYvsuzkP26NLAQADAgADeAADNQQ"

    try:
        # Send the photo first
        await context.bot.send_photo(chat_id=chat_id, photo=image_file_id)
        logger.debug("Photo sent successfully.")

        # UPI payment link
        upi_payment_url = "https://example.com/valid-upi-link"
        keyboard = [
            [InlineKeyboardButton("Pay via UPI", url=upi_payment_url)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send payment instruction message
        await context.bot.send_message(chat_id=chat_id,
                                       text=("You are purchasing 6000 videos, allowing you to get 200 videos every day for 30 days.\n\n"
                                             "Click the button below to pay via UPI."),
                                       reply_markup=reply_markup)
        logger.debug(f"Sent UPI payment button to user {query.from_user.id}.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await context.bot.send_message(chat_id=chat_id,
                                       text="An error occurred while processing your request. Please try again later.")

async def plan_status(update: Update, context) -> None:
    user_id = update.effective_chat.id
    chat_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "User"

    logger.info(f"User {user_id} ({user_name}) checked their plan status.")
    await log_user_activity(context, f"{user_name} (ID: {user_id}) checked their plan status.")


    # Database operations
    with sqlite3.connect('videos.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT plan, daily_count, last_access FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            await context.bot.send_message(chat_id=chat_id, text="User not found in the database.")
            return

        plan = user[0]
        daily_count = user[1]
        last_access = datetime.datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S.%f')

        # Check if it's a new day to reset daily count
        if (datetime.datetime.utcnow() - last_access).days >= 1:
            remaining_videos = 3 if plan == 'free' else 200
        else:
            remaining_videos = (3 if plan == 'free' else 200) - daily_count

        # Prepare the status message
        status_message = (
            f"**Daily Free Videos Consumed:** {daily_count}**/**{remaining_videos}\n\n"
            "You don't have any active plan."
        )

        logger.debug(f"Sending plan status to user {user_id}: {status_message}")
        await context.bot.send_message(chat_id=chat_id, text=status_message, parse_mode='Markdown')
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # Send the upgrade plan message as a separate message
        upgrade_message = "👉 To upgrade your plan, use the /buy command."
        await context.bot.send_message(chat_id=chat_id, text=upgrade_message)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    init_db()
    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(MessageHandler(filters.Regex('^(Plan Status 📝|Get Video 🍒)$'), handle_reply_keyboard))
    application.add_handler(CallbackQueryHandler(plan_selected))
    application.add_handler(MessageHandler(filters.VIDEO & filters.Chat(username=VIDEO_CHANNEL_USERNAME), handle_video))

    application.run_polling()

if __name__ == '__main__':
    main()
