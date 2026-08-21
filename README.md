AI Email Classifier
AI-powered email classification using Python and an LLM API. Automatically categorizes incoming emails by category, priority, and sentiment — converting unstructured text into structured data ready for downstream systems.

Problem
Business email inboxes receive hundreds of messages daily. Manually reading and triaging each one is time-consuming, inconsistent, and doesn't scale. Traditional rule-based systems (keyword matching, regex) are brittle and can't understand context or tone.

Solution
This project uses a Large Language Model (LLM) to analyze email text and return structured classification in JSON format. The system reads emails from a CSV file, classifies each one through an LLM API call, and writes the results to a JSON file — creating an automated pipeline that can integrate with existing business tools (Excel, SQL databases, Power Automate flows).

Architecture
emails.csv
│
▼
Python (csv.DictReader)
│
▼
LLM API (Groq — OpenAI-compatible)
│ • System prompt defines classification schema
│ • JSON mode ensures structured output
│ • Temperature 0 for deterministic classification
│
▼
JSON parsing + validation
│ • Verify expected fields
│ • Error records for failed classifications
│
▼
results.json
│ • Structured classifications
│ • Metadata (timestamp, totals, error count)
│ • Ready for downstream consumption


## Technologies

| Technology | Purpose |
|---|---|
| Python | Core language |
| OpenAI SDK | LLM API client (OpenAI-compatible — works with Groq, OpenAI, and other providers) |
| Groq API | LLM inference (currently gpt-oss-120b) |
| python-dotenv | Environment variable management for API keys |
| CSV / JSON | Input and output formats |

## Installation

```bash
# Clone the repository
git clone https://github.com/JorgeLSa/ai-email-classifier.git
cd ai-email-classifier

# Create and activate virtual environment
python -m venv .venv

# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure your API key
# Copy .env.example to .env and add your Groq API key


Usage

python main.py

The script reads emails.csv, classifies each email, and writes results to results.json.

Example
Input (emails.csv):

id,email_text
1,I have been waiting for my invoice for two weeks. Please send it as soon as possible.
2,Your new dashboard feature is amazing, the team loves it. Great work!
3,I need pricing information for 50 enterprise licenses.

Output (results.json):
{
  "processed_at": "2025-01-15T10:30:00",
  "total": 3,
  "errors": 0,
  "results": [
    {
      "id": "1",
      "category": "Billing",
      "priority": "High",
      "sentiment": "Negative",
      "error": null
    },
    {
      "id": "2",
      "category": "Other",
      "priority": "Low",
      "sentiment": "Positive",
      "error": null
    },
    {
      "id": "3",
      "category": "Sales",
      "priority": "Medium",
      "sentiment": "Neutral",
      "error": null
    }
  ]
}

Error Handling
The system includes 6 layers of protection:

Input validation — Empty or whitespace-only emails are rejected before any API call
Connection errors — Handles network failures gracefully
Rate limiting — Catches 429 errors when exceeding request limits
API errors — Captures HTTP errors (401, 404, 500, etc.)
JSON parsing — Handles cases where the model returns non-JSON content
Field validation — Verifies all expected fields are present in the response
Failed classifications return an error record instead of crashing the pipeline:

json

{
  "id": "5",
  "category": null,
  "priority": null,
  "sentiment": null,
  "error": "Empty email text"
}

Project Structure

ai-email-classifier/
├── .env.example      # Environment variable template
├── .gitignore        # Files excluded from version control
├── emails.csv        # Sample input data
├── main.py           # Core logic: classification, CSV processing, error handling
├── README.md         # Project documentation
└── requirements.txt  # Python dependencies

Future Improvements
 Read emails directly from an API or database instead of CSV
 Add retry logic with exponential backoff for rate-limited requests
 Support batch API calls to reduce latency
 Add unit tests with pytest
 Extend classification categories dynamically via configuration
 Deploy as a REST API endpoint (FastAPI)
 Integrate with Power Automate for end-to-end email automation

 