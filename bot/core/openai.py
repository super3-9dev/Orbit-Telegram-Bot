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
3. Only include opportunities where Orbit LAY odds <= Golbet odds
4. Return results in this exact JSON format with these 6 required fields:

{{
    "opportunities": [
        {{
            "match_name": "Team A vs Team B",
            "orbit_lay_odds": 2.50,
            "comparison_odds": 2.60,
            "odds_difference": "0.10 (3.85%)",
            "market_type": "1X2",
            "detection_time": "2024-01-15 14:30:25"
        }}
    ]
}}

Requirements:
- Match name: Full team names (e.g., "Arsenal vs Chelsea")
- Orbit LAY odds: The pink box value from Orbit
- Comparison odds: The corresponding odds from Golbet
- Odds difference: Both numeric difference and percentage
- Market type: Always "1X2" for football matches
- Detection time: Current timestamp in YYYY-MM-DD HH:MM:SS format

Only return valid arbitrage opportunities where Orbit LAY <= Golbet odds.
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
        print("--------------------------------")
        print(completion.choices[0].message.content)
        print("--------------------------------")
        return completion.choices[0].message.content
    except openai.RateLimitError:
        print("Rate limit exceeded")
        return None
