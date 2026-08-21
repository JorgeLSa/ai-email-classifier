import csv
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-120b"

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


def classify_email(email_text: str) -> dict:
    error_record = {
        "category": None,
        "priority": None,
        "sentiment": None,
        "error": None,
    }

    if not email_text or not email_text.strip():
        error_record["error"] = "Empty email text"
        return error_record

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

    raw_content = response.choices[0].message.content

    try:
        result = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError):
        error_record["error"] = f"Invalid JSON from model: {raw_content[:100]}"
        return error_record

    expected_keys = {"category", "priority", "sentiment"}
    missing = expected_keys - set(result.keys())
    if missing:
        error_record["error"] = f"Missing fields: {missing}"
        error_record.update({k: result.get(k) for k in expected_keys if k in result})
        return error_record

    result["error"] = None
    return result


def process_csv(input_path: str, output_path: str) -> dict:
    results = []

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email_id = row["id"]
            email_text = row["email_text"]

            classification = classify_email(email_text)
            classification["id"] = email_id

            results.append(classification)
            status = "ok" if classification["error"] is None else "ERROR"
            print(f"  [{status}] Email {email_id}: {classification.get('category', 'N/A')}")

    output = {
        "processed_at": datetime.now().isoformat(),
        "total": len(results),
        "errors": sum(1 for r in results if r["error"] is not None),
        "results": results,
    }

    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


def main():
    input_file = "emails.csv"
    output_file = "results.json"

    print("AI Email Classifier")
    print(f"Processing {input_file}...")
    print()

    output = process_csv(input_file, output_file)

    print()
    print(f"Done: {output['total']} emails processed, {output['errors']} errors")
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()