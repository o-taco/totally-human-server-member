import discord
import os
import random
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
from collections import defaultdict, deque

conversation_memory = defaultdict(lambda: deque(maxlen = 100))

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_ID = os.getenv("AI_CHANNEL_ID")
FINE_TUNED_MODEL_ID = os.getenv("FINE_TUNED_MODEL_ID")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

client = OpenAI(api_key=OPENAI_API_KEY)



# SYSTEM_PROMPT = """
# you are not an assistant. you are a regular in a private discord server.
#
# send YOUR OWN messages based off the conversation
# REQUIRED: do not start messages with [user]: [message], just SEND YOUR MESSAGE CONTENT LIKE [message]
# """

SYSTEM_PROMPT = """
be a nonchalant rizzler in a discord conversation
make your responses nonchalant and actually sound like a real person instead of chatgpt 
"""

EXAMPLES = [
    "bro ts cooked 😭",
    "erm what the sigma is ts diddy blud doing",
    "blud is albert einstein",
    "martisan",
    "pluh pluh pluh pluh pluh",
    "lowk ts pmo icl",
]


# @bot.event
# async def on_ready():
#     print(f"Logged in as {bot.user}")
#
#     channel = bot.get_channel(CHANNEL_ID)
#     if not channel:
#         print("Channel not found.")
#         await bot.close()
#         return
#
#
#     message = "pluh"
#     await channel.send(content=message)
#
#     await bot.close()


@bot.event
# async def on_message(message: discord.Message):
#     # if not should_reply(message):
#     #     return
#
#     try:
#         async with message.channel.typing():
#             response = client.chat.completions.create(
#                 model="gpt-4.1-mini",
#                 temperature=0.9,
#                 max_tokens=80,
#                 messages=[
#                     {"role": "system", "content": SYSTEM_PROMPT},
#
#                     # style examples
#                     *[
#                         {"role": "assistant", "content": e}
#                         for e in EXAMPLES
#                     ],
#
#                     # actual user message
#                     {
#                         "role": "user",
#                         "content": message.content.replace(
#                             f"<@{bot.user.id}>", ""
#                         ),
#                     },
#                 ],
#             )
#
#         reply = response.choices[0].message.content.strip()
#         if reply:
#             await message.reply(reply)
#
#     except Exception as e:
#         print("error:", e)
#
#     await bot.process_commands(message)

async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)



    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # examples as prior assistant messages
    for ex in EXAMPLES:
        messages.append({
            "role": "assistant",
            "content": ex
        })

    # minimal prompt
    messages.append({
        "role": "user",
        "content": "say something to kick off the roleplay"
    })

    response = client.chat.completions.create(
        model = FINE_TUNED_MODEL_ID,
        temperature=0.7,
        max_tokens=100,
        messages=messages,
    )

    msg = response.choices[0].message.content.strip()
    await channel.send(msg)

@bot.event
async def on_message(message: discord.Message):
    # ignore itself and other bots
    if message.author.bot:
        return

    # only respond in one channel
    if message.channel.id != CHANNEL_ID:
        return

    # store user message in memory
    author = message.author.display_name
    text = message.content

    conversation_memory[message.channel.id].append({
        "role": "user",
        "content": f"{author}: {text}"
    })

    # build msgs list
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # style grounding
    for ex in EXAMPLES:
        messages.append({
            "role": "assistant",
            "content": ex
        })

    # conversation memory
    messages.extend(conversation_memory[message.channel.id])

    # call openai
    async with message.channel.typing():
        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL_ID,
            temperature=0.7,
            max_tokens=100,
            messages=messages,
        )

    reply = response.choices[0].message.content.strip()

    colon_index = reply.find(":") # DUCT TAPING THE PROBLEM BY TRUNCATING USER 👍👍👍👍👍👍👍🤫🤫🤫🤫🤫🤫
    if 0 < colon_index < 40:
        reply = reply[colon_index + 1:].strip()

    if reply:
        await message.reply(reply)

        # store bot reply in memory
        conversation_memory[message.channel.id].append({
            "role": "assistant",
            "content": reply
        })

    # so commands still work
    await bot.process_commands(message)

@bot.command()
async def history(ctx):
    channel_id = ctx.channel.id

    if channel_id not in conversation_memory or not conversation_memory[channel_id]:
        await ctx.send("no history stored")
        return

    lines = []
    for msg in conversation_memory[channel_id]:
        role = msg["role"]
        content = msg["content"]
        lines.append(f"**{role}:** {content}")

    history_text = "\n".join(lines)

    # discord message limit
    if len(history_text) > 1900:
        history_text = history_text[-1900:]

    await ctx.send(history_text)

@bot.command()
async def clear(ctx):
    channel_id = ctx.channel.id

    if channel_id not in conversation_memory or not conversation_memory[channel_id]:
        await ctx.send("no memory to clear")
        return

    conversation_memory[channel_id].clear()
    await ctx.send("memory cleared")


bot.run(TOKEN)
