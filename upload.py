import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

file = client.files.create(
    file=open("discord_finetune.jsonl", "rb"),
    purpose="fine-tune"
)
print(file)