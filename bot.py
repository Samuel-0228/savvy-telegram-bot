import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Environment-based token
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7075011101
DATA_FILE = "messages.json"

# Load or initialize message store
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def save_message(user_id, username, message_text):
    with open(DATA_FILE, "r") as f:
        messages = json.load(f)
    messages.append({
        "user_id": user_id,
        "username": username,
        "message": message_text
    })
    with open(DATA_FILE, "w") as f:
        json.dump(messages, f, indent=2)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to SAVVY SOCIETY! Send me your questions anytime."
    )


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message_text = update.message.text
    user_id = user.id
    username = user.username or user.first_name

    # Save message to JSON
    save_message(user_id, username, message_text)

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Message from {username} (ID: {user_id}):\n\n{message_text}"
    )

    # Friendly response to user
    await update.message.reply_text(
        "Thanks for your message! 😊\nWe'll get back to you shortly.\nSAVVY SOCIETY – stay tuned at @savvy."
    )


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 You're not authorized to use this.")

    try:
        user_id = int(context.args[0])
        reply_text = ' '.join(context.args[1:])
        if not reply_text:
            raise ValueError("No reply message provided.")
        await context.bot.send_message(chat_id=user_id, text=f"💬 Admin:\n{reply_text}")
        await update.message.reply_text("✅ Message sent!")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /reply <user_id> <your message>")


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    app.add_handler(CommandHandler("reply", reply_command))

    print("🤖 Bot is running...")
    app.run_polling()
