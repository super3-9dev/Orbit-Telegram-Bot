from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable instead of hardcoding
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=api_key)


def compare(orbit_data, golbet_data):
    try:
        # Convert the arrays to string representations for the prompt
        user_prompt = f"""
Analyze this football betting data to find arbitrage opportunities:

ORBIT DATA (LAY odds - pink box values):
{orbit_data}

GOLBET DATA (BACK odds):
{golbet_data}

Instructions:
1. Match teams with the same names between Orbit and Golbet
2. Compare Orbit LAY odds with Golbet odds for each selection (1, X, 2)
3. Calculate the percentage difference: ((Golbet odds - Orbit LAY odds) / Orbit LAY odds) × 100
4. ONLY include opportunities where the percentage difference is between -1% and +30%
5. Return ONLY the array of opportunities, no JSON wrapper, no explanations:

[
    {{
        "match_name": "Team A vs Team B",
        "orbit_lay_odds": 2.00,
        "comparison_odds": 2.20,
        "odds_difference": "0.20 (10.00%)",
        "market_type": "1X2",
        "detection_time": "2024-01-15 14:30:25"
    }}
]

Requirements:
- Match name: Full team names (e.g., "Arsenal vs Chelsea")
- Orbit LAY odds: The pink box value from Orbit
- Comparison odds: The corresponding odds from Golbet
- Odds difference: Both numeric difference and percentage
- Market type: Always "1X2" for football matches
- Detection time: Current timestamp in YYYY-MM-DD HH:MM:SS format

IMPORTANT FILTERING RULES:
- Percentage difference must be >= -1% AND <= +30%
- Formula: ((Golbet odds - Orbit LAY odds) / Orbit LAY odds) × 100
- Examples:
  • Orbit: 2.00, Golbet: 2.20 → +10% → INCLUDE ✅
  • Orbit: 2.00, Golbet: 1.95 → -2.5% → EXCLUDE ❌
  • Orbit: 2.00, Golbet: 2.80 → +40% → EXCLUDE ❌

Only return valid arbitrage opportunities within the -1% to +30% threshold.
Return ONLY the array, no other text, no JSON wrapper, no explanations.
Do NOT wrap the result in ```json or any code block. Return only the array.
"""
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )
        # Remove any accidental code block markers from the response
        content = completion.choices[0].message.content
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    except openai.RateLimitError:
        print("Rate limit exceeded")
        return None
