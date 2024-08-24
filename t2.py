import asyncio
import logging
import aiosqlite
import random
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from telegram.error import BadRequest, TelegramError
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Telegram channel username
CHANNEL_USERNAME = "RickBot"

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Start command received")

    user_id = update.effective_chat.id
    username = update.effective_chat.first_name

    async with aiosqlite.connect('videos.db') as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()

        if not user:
            await db.execute(
                "INSERT INTO users (user_id, plan, daily_count, last_access) VALUES (?, ?, ?, ?)",
                (user_id, 'free', 0, datetime.datetime.utcnow())
            )
            await db.commit()
            logger.info(f"Inserted new user with ID: {user_id}")

    keyboard = [[InlineKeyboardButton("Get Video", callback_data='get_video')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Hey {username}, Ready for some fun?\nClick on the 'Get Video' button to begin.", reply_markup=reply_markup)

# Function to check if the user is subscribed to the channel
async def check_subscription(user_id: int, context: CallbackContext) -> bool:
    member_status = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member_status.status in ['member', 'administrator', 'creator']

def send_video(bot: Bot, chat_id, video_path):
    try:
        logger.debug(f"Attempting to send video with file_id: {video_path}")
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id=chat_id, video=video)
    except BadRequest as e:
        logging.error(f"BadRequest error while sending video: {e}")
    except TelegramError as e:
        logging.error(f"General TelegramError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Function to handle the Get Video button
async def get_video(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"User {query.from_user.id} requested a video")

    user_id = query.from_user.id

    try:
        async with aiosqlite.connect('videos.db') as db:
            async with db.execute("SELECT plan, daily_count, last_access FROM users WHERE user_id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()

            if not user:
                await query.edit_message_text(text="User not found in the database.")
                return

            if not await check_subscription(user_id, context):
                keyboard = [[InlineKeyboardButton("Subscribe to Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="You are not subscribed to the channel. Please subscribe and try again!", reply_markup=reply_markup)
                return

            # Reset daily count if it's a new day
            if user[0] == 'free' and (datetime.datetime.utcnow() - datetime.datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S.%f')).days >= 1:
                await db.execute("UPDATE users SET daily_count = 0 WHERE user_id = ?", (user_id,))
                await db.commit()

            # Handle video sending logic for both free and paid users
            if user[0] == 'free' and user[1] >= 3:
                await query.edit_message_text(text="You can only access 3 free videos daily. To unlock more daily videos, consider upgrading to a paid plan.")
            else:
                async with db.execute("SELECT file_id FROM videos ORDER BY RANDOM() LIMIT 1") as cursor:
                    video = await cursor.fetchone()
                    if video is None:
                        await query.edit_message_text(text="No videos available.")
                        return

                    logger.info(f"Sending video with file_id: {video[0]}")
                    await context.bot.send_video(chat_id=query.message.chat_id, video=video[0], protect_content=True)

                    # Update daily count and last access time for free users
                    if user[0] == 'free':
                        await db.execute("UPDATE users SET daily_count = daily_count + 1, last_access = ? WHERE user_id = ?",
                                         (datetime.datetime.utcnow(), user_id))
                        await db.commit()

    except Exception as e:
        logger.error(f"Failed to send video: {e}")
        await query.edit_message_text(text="An error occurred while sending the video.")

# Function to handle purchasing a plan (Removed UPI link for testing)
async def buy_plan(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"User {query.from_user.id} clicked to buy a plan")

    # For testing purposes, we just inform the user about the plan without requiring payment.
    await query.edit_message_text(text="You are now in a testing environment. Normally, you would purchase a plan here.")

async def channel_post(update: Update, context: CallbackContext):
    logger.info(f"New post in the channel: {update.channel_post}")

    if update.channel_post.video:
        video_file_id = update.channel_post.video.file_id
        logger.info(f"Video file ID: {video_file_id}")

        # Store video ID in the database
        try:
            async with aiosqlite.connect('videos.db') as db:
                await db.execute("INSERT INTO videos (file_id) VALUES (?)", (video_file_id,))
                await db.commit()
                logger.info(f"Video ID {video_file_id} inserted into the database.")
        except Exception as e:
            logger.error(f"Failed to insert video ID: {e}")

# Main function to start the bot
def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables.")
        return

    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(get_video, pattern='get_video'))
    application.add_handler(CallbackQueryHandler(buy_plan, pattern='buy_plan'))
    application.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.CHANNEL, channel_post))

    logger.info("Starting bot...")

    # Run the bot indefinitely
    application.run_polling()

if __name__ == '__main__':
    main()
