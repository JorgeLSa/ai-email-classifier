import json
import os

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError

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
    error_record = {
        "category": None,
        "priority": None,
        "sentiment": None,
        "error": None,
    }

    # 1. Validación de entrada
    if not email_text or not email_text.strip():
        error_record["error"] = "Empty email text"
        return error_record

    # 2. Llamada a la API con manejo de errores específicos
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": email_text},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
    except APIConnectionError:
        error_record["error"] = "Connection failed: check internet connection"
        return error_record
    except RateLimitError:
        error_record["error"] = "Rate limit exceeded: too many requests"
        return error_record
    except APIStatusError as e:
        error_record["error"] = f"API error {e.status_code}: {e.message}"
        return error_record

    # 3. Parseo del JSON
    raw_content = response.choices[0].message.content

    try:
        result = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError):
        error_record["error"] = f"Invalid JSON from model: {raw_content[:100]}"
        return error_record

    # 4. Validación de campos esperados
    expected_keys = {"category", "priority", "sentiment"}
    missing = expected_keys - set(result.keys())
    if missing:
        error_record["error"] = f"Missing fields: {missing}"
        error_record.update({k: result.get(k) for k in expected_keys if k in result})
        return error_record

    # 5. Éxito
    result["error"] = None
    return result


def main():
    test_emails = [
        "I have been waiting for my invoice for two weeks. Please send it as soon as possible.",
        "Your new dashboard feature is amazing, the team loves it. Great work!",
        "I need pricing information for 50 enterprise licenses. Can someone from sales contact me?",
        "Hi",
        "",  # edge case: empty email
        "Thank you for resolving my login issue so quickly. You guys are great.",
    ]

    for i, email in enumerate(test_emails, 1):
        print(f"--- Email {i} ---")
        print(f"Text: {email}")
        result = classify_email(email)
        print("Classification:")
        print(json.dumps(result, indent=2))
        print()


if __name__ == "__main__":
    main()