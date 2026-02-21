import json
from pathlib import Path

# === CONFIG ===

INPUT_JSON = "ASIANGANG_GENERAL_LOG.json"
OUTPUT_JSONL = "discord_finetune.jsonl"

SYSTEM_PROMPT = """
you are a regular in a private discord server.
messages are formatted like "name: message".
match the tone, length, and style of the server.
always respond as if you are just another friend in the chat.
""".strip()

# messages to use as context
CONTEXT_SIZE = 4


import json

def load_messages(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # trimming up to the last 20 lines until JSON parses
    for cut in range(0, 20):
        try_lines = lines[: len(lines) - cut]  # drop last cut lines
        text = "".join(try_lines).strip()
        if not text:
            break

        try:
            raw = json.loads(text)
            print(f"loaded JSON successfully after dropping {cut} trailing lines")
            break
        except json.JSONDecodeError:
            raw = None

    if raw is None:
        raise ValueError("could not recover valid JSON; re-export the file")

    # if the top level is an object with messages
    if isinstance(raw, list):
        raw_messages = raw
    else:
        raw_messages = raw.get("messages", raw.get("Messages", []))

    cleaned = []

    for msg in raw_messages:
        author = None
        content = None
        is_bot = False

        if "author" in msg:
            author_info = msg["author"]
            author = (
                author_info.get("name")
                or author_info.get("username")
                or "unknown"
            )
            is_bot = author_info.get("isBot", False) or author_info.get("is_bot", False)
        elif "Author" in msg:
            author_info = msg["Author"]
            author = author_info.get("Name") or "unknown"
            is_bot = author_info.get("IsBot", False)

        content = msg.get("content") or msg.get("Content") or ""
        if not content:
            continue
        content = content.strip()
        if not content:
            continue

        if is_bot:
            continue
        if content.startswith("!"):  # skip commands
            continue

        cleaned.append(f"{author}: {content}")

    return cleaned



def build_examples(cleaned_messages):
    examples = []

    if len(cleaned_messages) <= CONTEXT_SIZE:
        return examples

    for i in range(CONTEXT_SIZE, len(cleaned_messages)):
        context = cleaned_messages[i - CONTEXT_SIZE : i - 1]
        target = cleaned_messages[i - 1]

        messages = []

        # system message
        messages.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

        # context
        for c in context:
            messages.append({
                "role": "user",
                "content": c
            })

        # "assistant" reply
        messages.append({
            "role": "assistant",
            "content": target
        })

        examples.append({"messages": messages})

    return examples


def save_jsonl(examples, path: str):
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    in_path = Path(INPUT_JSON)
    if not in_path.exists():
        print(f"Input file not found: {in_path}")
        return

    print("loading messages...")
    cleaned_messages = load_messages(str(in_path))
    print(f"loaded {len(cleaned_messages)} cleaned messages")

    print("building training examples...")
    examples = build_examples(cleaned_messages)
    print(f"built {len(examples)} training examples")

    print("writing jsonl...")
    save_jsonl(examples, OUTPUT_JSONL)
    print(f"done! wrote {len(examples)} lines to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()
