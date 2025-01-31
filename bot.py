from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from database import users_collection, chat_history_collection, file_metadata_collection
from gemini import generate_response
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id

    # Check if user already exists
    if users_collection.find_one({"chat_id": chat_id}):
        await update.message.reply_text(f"Welcome back, {user.first_name}!")
    else:
        # Request contact details
        contact_button = KeyboardButton("Share Contact", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
        await update.message.reply_text("Please share your contact details.", reply_markup=reply_markup)

# Contact handler
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    contact = update.message.contact

    # Save user data
    user_data = {
        "chat_id": update.message.chat_id,
        "first_name": user.first_name,
        "username": user.username,
        "phone_number": contact.phone_number,
        "created_at": datetime.now()
    }
    users_collection.insert_one(user_data)
    await update.message.reply_text("Thank you for sharing your contact details!")

# Chat handler
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    bot_response = generate_response(user_input)
    await update.message.reply_text(bot_response)

    # Save chat history
    chat_history = {
        "chat_id": update.message.chat_id,
        "user_input": user_input,
        "bot_response": bot_response,
        "timestamp": datetime.now()
    }
    chat_history_collection.insert_one(chat_history)

# File handler
async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"downloads/{file.file_id}"
    await file.download_to_drive(file_path)

    # Analyze file content
    analysis = generate_response(f"Describe the content of this file: {file_path}")
    await update.message.reply_text(analysis)

    # Save file metadata
    file_metadata = {
        "chat_id": update.message.chat_id,
        "filename": file.file_name,
        "description": analysis,
        "timestamp": datetime.now()
    }
    file_metadata_collection.insert_one(file_metadata)

# Web search handler
async def web_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    summary = generate_response(f"Search the web for: {query}")
    await update.message.reply_text(summary)

# Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, file_handler))
    app.add_handler(CommandHandler("websearch", web_search_handler))

    # Start the bot
    app.run_polling()
    