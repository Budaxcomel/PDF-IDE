```python
#!/usr/bin/python
import os
import telebot
from telebot import types
from PIL import Image
import shutil
from time import sleep
from pathlib import Path
import logging

# Define the API token and ConvertAPI key here
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")  # Make sure to set this environment variable
CONVERT_API_KEY = os.getenv("CONVERT_API_KEY")  # Make sure to set this environment variable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the bot instance
bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# In-memory storage
PDF = {}

def get_user_dir(user_id):
    user_dir = Path(f"./{user_id}")
    user_dir.mkdir(exist_ok=True)
    return user_dir

@bot.message_handler(commands=["start"])
def start(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        strtMsg = f"""
ʜᴇʏ [{message.from_user.first_name}](tg://user?id={message.chat.id}) ɪᴀᴍ ᴘᴅғ ɪᴅᴇ..
sᴇɴᴅ ᴍᴇ ᴛʜᴇ ғɪʟᴇs ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ..

➪ Project Name : ᴘᴅғ ɪᴅᴇ
➪ Author : [Budaxcomel](https://telegram.me/ownerimmanvpn)
➪ Library : Pyrogram
➪ Language : Python
➪ License Type : GNU General public License (GPL)

sᴏᴍᴇ ᴏғ ᴛʜᴇ ᴍᴀɪɴ ғᴇᴀᴛᴜʀᴇs ᴀʀᴇ:
◍ `ᴄᴏɴᴠᴇʀᴛ ɪᴍᴀɢᴇs ᴛᴏ ᴘᴅғ`
◍ `ᴄᴏɴᴠᴇʀᴛ ᴘᴅғ ᴛᴏ ɪᴍᴀɢᴇs`
◍ `ᴄᴏɴᴠᴇʀᴛ ғɪʟᴇs ᴛᴏ ᴘᴅғ`
"""
        key = types.InlineKeyboardMarkup()
        key.add(
            types.InlineKeyboardButton('Developer', url='https://telegram.me/ownerimmanvpn'),
            types.InlineKeyboardButton("More", callback_data="imgsToPdfEdit"),
        )
        bot.send_message(
            message.chat.id, strtMsg, disable_web_page_preview=True, reply_markup=key
        )
    except Exception as e:
        logger.error(f"Error in /start handler: {e}")

@bot.message_handler(commands=["id"])
def usr_id(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, f"Your ID - `{message.chat.id}`")
    except Exception as e:
        logger.error(f"Error in /id handler: {e}")

@bot.message_handler(commands=["feedback"])
def feedback(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        feedbackMsg = f"Feedback [immanvpn](https://telegram.me/ownerimmanvpn) 🤍"
        bot.send_message(message.chat.id, feedbackMsg, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in /feedback handler: {e}")

def handle_image(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        picMsgId = bot.reply_to(message, "`Downloading your Image..`")
        
        user_dir = get_user_dir(message.chat.id)
        img_path = user_dir / "imgs" / f"{message.chat.id}.jpg"
        img_path.parent.mkdir(exist_ok=True)
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(img_path, "wb") as new_file:
            new_file.write(downloaded_file)
        
        img = Image.open(img_path).convert("RGB")
        PDF.setdefault(message.chat.id, []).append(img)
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            text=f"`Added {len(PDF[message.chat.id])} page/'s to your pdf..`\n\n/generate to generate PDF",
            message_id=picMsgId.message_id,
        )
    except Exception as e:
        logger.error(f"Error handling image: {e}")

@bot.message_handler(content_types=["photo"])
def pic(message):
    handle_image(message)

def handle_document(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        file_info = message.document
        file_name = file_info.file_name
        file_size = file_info.file_size
        
        if file_size >= 10_000_000:
            bot.send_message(
                message.chat.id,
                "Due to Overload, bot supports only 10MB files. Please send a file less than 10MB.",
            )
            sleep(15)
            bot.delete_message(message.chat.id, message.message_id)
            return

        file_ext = Path(file_name).suffix.lower()
        user_dir = get_user_dir(message.chat.id)
        
        if file_ext in [".jpg", ".jpeg", ".png"]:
            picMsgId = bot.reply_to(message, "`Downloading your Image..`")
            img_path = user_dir / "imgs" / f"{message.chat.id}{file_ext}"
            
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            with open(img_path, "wb") as new_file:
                new_file.write(downloaded_file)
            
            img = Image.open(img_path).convert("RGB")
            PDF.setdefault(message.chat.id, []).append(img)
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                text=f"`Added {len(PDF[message.chat.id])} page/'s to your pdf..`\n\n/generate to generate PDF",
                message_id=picMsgId.message_id,
            )
        
        elif file_ext == ".pdf":
            # Handle PDF to images conversion
            pass
        
        else:
            bot.send_message(
                message.chat.id,
                "Unsupported file type. Please send an image or a PDF.",
            )
    
    except Exception as e:
        logger.error(f"Error handling document: {e}")

@bot.message_handler(content_types=["document"])
def fls(message):
    handle_document(message)

@bot.message_handler(commands=["cancel"])
def cancel(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        user_dir = get_user_dir(message.chat.id)
        shutil.rmtree(user_dir)
        bot.reply_to(message, "`Queue deleted Successfully..`")
        PDF.pop(message.chat.id, None)
    except FileNotFoundError:
        bot.reply_to(message, "`No Queue found`")
    except Exception as e:
        bot.reply_to(message, "`An error occurred while deleting the queue.`")
        logger.error(f"Error in /cancel handler: {e}")

@bot.message_handler(commands=["generate"])
def generate(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        new_name = message.text.replace("/generate", "").strip()
        images = PDF.pop(message.chat.id, [])
        
        if not images:
            ntFnded = bot.reply_to(message, "`No images found.`")
            sleep(5)
            bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, ntFnded.message_id)
            return
        
        file_name = f"{new_name or message.from_user.first_name}.pdf"
        file_path = get_user_dir(message.chat.id) / file_name
        images[0].save(file_path, save_all=True, append_images=images[1:])
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            text="`Uploading pdf..`",
            message_id=message.message_id,
        )
        bot.send_chat_action(message.chat.id, "upload_document")
        
        with open(file_path, "rb") as sendfile:
            bot.send_document(message.chat.id, sendfile)
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            text="`PDF generated and sent successfully!`",
            message_id=message.message_id,
        )
        
    except Exception as e:
        logger.error(f"Error in /generate handler: {e}")
        bot.reply_to(message, "`An error occurred while generating the PDF.`")

# Polling
bot.polling()
```
