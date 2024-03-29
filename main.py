import os
import requests
import openai
import time
from dotenv import load_dotenv
import pymongo
import datetime
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
os.getenv("TELEGRAM_API_KEY")
os.getenv("MONGO_DB")

now = datetime.datetime.now()
current_month = now.month

PAI_TOKEN = "\n \n Any donations you can make are greatly appreciated and will help us keep our "
Telegram = "\n \n Kindly join our telegram group https://t.me/pencilAI"

# Connect to MongoDB to save userid
client = pymongo.MongoClient(format(os.getenv("MONGO_DB")))
db = client["abekeapo"]
collection = db["Cluster0"]

update_url = "https://api.telegram.org/bot{}/getUpdates".format(os.getenv("TELEGRAM_API_KEY"))
send_message_url = "https://api.telegram.org/bot{}/sendMessage".format(os.getenv("TELEGRAM_API_KEY"))
client = openai.OpenAI(
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url='https://api.together.xyz',
)

# Set to keep track of unique users
last_update_id = 0

# Function to handle incoming messages
def handle_message(update):
    if "message" in update:
        message = update["message"]
        if "text" in message:
            message_text = message["text"]
            chat_id = message["chat"]["id"]

            # Check if the message ends with the bot's username
            if not message_text.endswith("@TajiriBot"):
                return  # Ignore the message if it doesn't end with "@tajiri"

            # Remove the bot's username from the message text before processing
            message_text = message_text[:-7]  # Assuming '@tajiri' is 7 characters long

            model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": message_text,
                        }
                    ],
                    model=model
                )
                # send the response back to Telegram
                requests.post(send_message_url, json={
                    "chat_id": chat_id,
                    "text": chat_completion.choices[0].message.content.strip()
                })
            except:
                requests.post(send_message_url, json={
                    "chat_id": chat_id,
                    "text": "I'm sorry, there was an error processing your request from our third party service providers. Please try again later."
                })
            global last_update_id
            last_update_id = update["update_id"]
        else:
            print("No text in the message")
    else:
        print("No message in update")

while True:
    response = requests.get(update_url, params={"offset": last_update_id + 1})
    if "result" in response.json():
        updates = response.json()["result"]
        for update in updates:
            handle_message(update)
    time.sleep(5)