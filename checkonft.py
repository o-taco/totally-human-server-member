import os
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

job_id = os.getenv("FINE_TUNING_JOB_ID")

# while True:
#     job = client.fine_tuning.jobs.retrieve(job_id)
#     print(job.status)
#     if job.status in ("succeeded", "failed", "cancelled"):
#         print(job)
#         break
#     time.sleep(5)

job = client.fine_tuning.jobs.retrieve(job_id)
print(job)