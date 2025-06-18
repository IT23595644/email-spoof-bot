from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load .env values
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

# Define conversation states
FROM, TO, SUBJECT, BODY = range(4)
user_data = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to the *ShadowByte Email Spoof Bot*!\n\n"
        "🚀 You can send spoofed emails (for educational purposes only).\n\n"
        "👉 Use /send to begin spoofing\n"
        "ℹ️ Use /help to learn more"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Help command
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*How to Use the Bot:*\n"
        "`/send` - Start sending spoofed email\n"
        "`/cancel` - Cancel the spoofing process\n\n"
        "*Example Flow:*\n"
        "- From Email\n"
        "- To Email\n"
        "- Subject\n"
        "- Message\n"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Send command - starts conversation
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💌 Enter the *spoofed FROM email address*:", parse_mode='Markdown')
    return FROM

async def get_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['from'] = update.message.text
    await update.message.reply_text("📬 Now enter the *TO email address*:", parse_mode='Markdown')
    return TO

async def get_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['to'] = update.message.text
    await update.message.reply_text("📝 What's the *email subject*?", parse_mode='Markdown')
    return SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['subject'] = update.message.text
    await update.message.reply_text("✉️ Type the *message body*:", parse_mode='Markdown')
    return BODY

async def get_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['body'] = update.message.text

    from_email = context.user_data['from']
    to_email = context.user_data['to']
    subject = context.user_data['subject']
    message = context.user_data['body']

    # Try sending email
    status = send_email(from_email, to_email, subject, message)
    await update.message.reply_text(status)

    return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Spoofing canceled.")
    return ConversationHandler.END

# Email sender function
def send_email(spoofed_from, to_email, subject, message):
    msg = EmailMessage()
    msg["From"] = spoofed_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(message)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        return "✅ Email sent successfully via Gmail SMTP!"
    except Exception as e:
        return f"❌ Error: {e}"

# Main app
def main():
    print("🚀 Bot is running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send)],
        states={
            FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_from)],
            TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_to)],
            SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_subject)],
            BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_body)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
