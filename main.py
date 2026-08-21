import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = """You are an email classification assistant for a business.
Analyze the email provided by the user and respond ONLY with a JSON object
using exactly this schema:

{
  "category": "Billing" | "Technical Support" | "Sales" | "Complaint" | "Other",
  "priority": "High" | "Medium" | "Low",
  "sentiment": "Positive" | "Neutral" | "Negative"
}

Rules:
- Respond with the JSON object only. No explanations, no markdown, no extra text.
"""
#python -c "from dotenv import load_dotenv; import os; load_dotenv(); from openai import OpenAI; c = OpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url='https://api.groq.com/openai/v1'); [print(m.id) for m in c.models.list().data]"
MODEL = "openai/gpt-oss-120b" #cambialo por uno de tu lista "qwen/qwen3.6-27b"

def classify_email(email_text: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw_content = response.choices[0].message.content
    return json.loads(raw_content)


def main():
    email = (
        "I have been waiting for my invoice for two weeks. "
        "Please send it as soon as possible."
    )

    print("Email:")
    print(email)
    print()

    result = classify_email(email)

    print("Classification:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()