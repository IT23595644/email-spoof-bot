from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv()

MAILTRAP_USERNAME = os.getenv("MAILTRAP_USERNAME")
MAILTRAP_PASSWORD = os.getenv("MAILTRAP_PASSWORD")
BOT_TOKEN = os.getenv("BOT_TOKEN")


# 📧 Function to send spoofed email
def send_email(spoofed_from, to_email, subject, message):
    msg = EmailMessage()
    msg["From"] = spoofed_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(message)

    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
            server.send_message(msg)
        return "✅ Spoofed email sent successfully to Mailtrap inbox."
    except Exception as e:
        return f"❌ Error sending email: {e}"

# 🤖 Telegram command handler
async def spoof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 4:
        await update.message.reply_text("Usage: /spoof <from_email> <to_email> <subject> <message>")
        return
    
    from_email = args[0]
    to_email = args[1]
    subject = args[2]
    message = ' '.join(args[3:])
    
    result = send_email(from_email, to_email, subject, message)
    await update.message.reply_text(result)

# 🚀 Start the Telegram bot
def main():
    print("🚀 Telegram bot started. Waiting for spoof commands...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("spoof", spoof))
    app.run_polling()

if __name__ == "__main__":
    main()
