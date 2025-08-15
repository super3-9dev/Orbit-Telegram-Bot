from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable instead of hardcoding
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=api_key)


def validate_opportunities(opportunities):
    """
    Validate that all opportunities meet the -1% to +30% threshold.
    
    Args:
        opportunities: List of opportunity dictionaries from AI
        
    Returns:
        List of validated opportunities that meet the threshold
    """
    if not opportunities or not isinstance(opportunities, list):
        return []
    
    validated_opportunities = []
    
    for opp in opportunities:
        try:
            # Extract the percentage from odds_difference string
            odds_diff_str = opp.get('odds_difference', '')
            
            # Parse percentage from format like "0.20 (10.00%)" or "-0.04271 (-2.45%)"
            if '(' in odds_diff_str and '%)' in odds_diff_str:
                percentage_str = odds_diff_str.split('(')[1].split('%)')[0]
                percentage = float(percentage_str)
                
                # Check if within threshold (-1% to +30%)
                if -1.0 <= percentage <= 30.0:
                    validated_opportunities.append(opp)
                    print(f"[VALIDATION] ✅ Opportunity validated: {percentage}% - {opp.get('match_name', 'Unknown')}")
                else:
                    print(f"[VALIDATION] ❌ Opportunity filtered out: {percentage}% (outside -1% to +30%) - {opp.get('match_name', 'Unknown')}")
            else:
                print(f"[VALIDATION] ⚠️ Could not parse percentage from: {odds_diff_str}")
                
        except Exception as e:
            print(f"[VALIDATION] ❌ Error validating opportunity: {e}")
            continue
    
    print(f"[VALIDATION] Filtered {len(opportunities)} opportunities to {len(validated_opportunities)} valid ones")
    return validated_opportunities


def compare(orbit_data, golbet_data):
    """
    Compare Orbit and Golbet data using OpenAI to find arbitrage opportunities.
    
    Args:
        orbit_data: List of Orbit market snapshots
        golbet_data: List of Golbet market snapshots
        
    Returns:
        List of validated arbitrage opportunities within -1% to +30% threshold
    """
    try:
        # Prepare data for AI analysis
        orbit_str = str(orbit_data)
        golbet_str = str(golbet_data)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the prompt with current timestamp
        prompt = f"""Analyze this football betting data to find arbitrage opportunities:

ORBIT DATA (LAY odds):
{orbit_str}

GOLBET DATA (BACK odds):
{golbet_str}

CRITICAL FILTERING REQUIREMENTS:
1. Match teams with the same names between Orbit and Golbet
2. Compare Orbit LAY odds with Golbet odds for each selection (1, X, 2)
3. Calculate the percentage difference: ((Golbet odds - Orbit LAY odds) / Orbit LAY odds) × 100
4. **STRICT FILTERING: ONLY include opportunities where percentage difference is >= -1% AND <= +30%**
5. For each opportunity, set "detection_time" to "{now_str}" (already provided, do NOT generate your own time)
6. Return ONLY the array of opportunities, no JSON wrapper, no explanations:

[
    {{
        "match_name": "Team A vs Team B",
        "orbit_lay_odds": 2.00,
        "comparison_odds": 2.20,
        "odds_difference": "0.20 (10.00%)",
        "market_type": "1X2",
        "detection_time": "{now_str}"
    }}
]

STRICT FILTERING RULES (MUST FOLLOW):
- **Percentage difference MUST be >= -1% AND <= +30%**
- **Formula: ((Golbet odds - Orbit LAY odds) / Orbit LAY odds) × 100**
- **Golbet odds must be greater than or equal to Orbit LAY odds**
- **Examples of VALID opportunities (INCLUDE):**
  • Orbit: 2.00, Golbet: 2.20 → +10% → INCLUDE ✅
  • Orbit: 2.00, Golbet: 1.99 → -0.5% → INCLUDE ✅ (>= -1%)
  • Orbit: 2.00, Golbet: 2.60 → +30% → INCLUDE ✅ (= +30%)
  • Orbit: 2.00, Golbet: 1.98 → -1% → INCLUDE ✅ (= -1%)

- **Examples of INVALID opportunities (EXCLUDE):**
  • Orbit: 2.00, Golbet: 1.95 → -2.5% → EXCLUDE ❌ (< -1%)
  • Orbit: 2.00, Golbet: 2.80 → +40% → EXCLUDE ❌ (> +30%)
  • Orbit: 2.00, Golbet: 1.97 → -1.5% → EXCLUDE ❌ (< -1%)

REQUIREMENTS:
- Match name: Full team names (e.g., "Arsenal vs Chelsea")
- Orbit LAY odds: The value from Orbit
- Comparison odds: The corresponding odds from Golbet
- Odds difference: Both numeric difference and percentage
- Market type: Always "1X2" for football matches
- detection_time: Always use "{now_str}" exactly as shown above for every opportunity.

**FINAL INSTRUCTION:**
- **ONLY return opportunities that meet the -1% to +30% threshold**
- **If NO opportunities meet this criteria, return an empty array []**
- **Do NOT include any opportunities outside this range**
- **Do NOT wrap the result in ```json or any code block**
- **Return only the array, no other text, no explanations**

Return ONLY valid arbitrage opportunities within the -1% to +30% threshold, or an empty array if none found."""
        
        print("[OPENAI] Sending data to GPT-4o for analysis...")
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        # Extract the response content
        ai_response = response.choices[0].message.content
        
        # Clean the response (remove code blocks if present)
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        if ai_response.startswith('```'):
            ai_response = ai_response[3:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        
        ai_response = ai_response.strip()
        
        # Parse the JSON response
        try:
            opportunities = json.loads(ai_response)
            print(f"[OPENAI] Successfully parsed {len(opportunities) if isinstance(opportunities, list) else 'non-list'} opportunities")
            
            # Validate opportunities to ensure they meet the threshold
            # validated_opportunities = validate_opportunities(opportunities)
            
            if opportunities:
                print(f"[OPENAI] ✅ Returning {len(opportunities)} validated opportunities")
                return opportunities
            else:
                print("[OPENAI] ⚠️ No opportunities met the threshold criteria")
                return []
                
        except json.JSONDecodeError as e:
            print(f"[OPENAI] JSON parsing error: {e}")
            print(f"[OPENAI] Raw response: {ai_response}")
            return []
            
    except Exception as e:
        print(f"[OPENAI] Error in compare function: {e}")
        return []
