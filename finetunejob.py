import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

job = client.fine_tuning.jobs.create(
    training_file=os.getenv("TRAINING_DATA_FILE"),
    model="gpt-4.1-mini-2025-04-14"
)

print(job.id)