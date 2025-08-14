
from __future__ import annotations
import os
import httpx
import json
from datetime import datetime
import pytz

# Read TZ at import; read token/chat at send-time to avoid empty values from early import
TZ = os.getenv("TZ", "Asia/Tokyo")

def ts(dt) -> str:
    try:
        tz = pytz.timezone(TZ)
        return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

async def send_telegram(text: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        print("[TELEGRAM DISABLED]", text)
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"  # Enable HTML formatting
        })

def format_alert(match_name: str, league: str|None, market: str, selection: str,
                 orbit_odds: float, other_site: str, other_odds: float,
                 detected_dt, kickoff_dt=None, diff_pct=None, diff_abs=None):
    lines = []
    lines.append("🚨 <b>ARBITRAGE SIGNAL DETECTED</b> 🚨")
    lines.append("")
    lines.append(f"⚽ <b>Match:</b> {match_name}")
    if league:
        lines.append(f"🏆 <b>League:</b> {league}")
    lines.append(f"🎯 <b>Market:</b> {market} — {selection}")
    lines.append("")
    lines.append(f"📊 <b>Orbit LAY:</b> {orbit_odds:.2f}")
    lines.append(f"📊 <b>{other_site.title()}:</b> {other_odds:.2f}")
    if diff_abs is not None and diff_pct is not None:
        lines.append(f"💰 <b>Difference:</b> {diff_abs:+.2f} ({diff_pct:+.2f}%)")
    lines.append("")
    lines.append(f"⏰ <b>Detected:</b> {ts(detected_dt)}")
    if kickoff_dt:
        lines.append(f"⚽ <b>Kickoff:</b> {ts(kickoff_dt)}")
    return "\n".join(lines)

def format_ai_analysis_result(ai_result: str, orbit_data, golbet_data) -> str:
    """
    Format the AI analysis result for Telegram with improved UI and clear array parsing
    """
    try:
        # Clean the result string and try to parse JSON
        cleaned_result = ai_result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
        
        cleaned_result = cleaned_result.strip()
        opportunities = json.loads(cleaned_result)
        
        # Header with beautiful styling
        lines = []
        lines.append("🎯 <b>ARBITRAGE OPPORTUNITIES REPORT</b> 🎯")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        # Analysis summary
        lines.append("📊 <b>ANALYSIS SUMMARY</b>")
        lines.append(f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"🔍 <b>Data Sources:</b>")
        lines.append(f"   • Orbit: <code>{len(orbit_data)}</code> matches")
        lines.append(f"   • Golbet: <code>{len(golbet_data)}</code> matches")
        lines.append("")
        lines.append("🎯 <b>FILTERING CRITERIA</b>")
        lines.append("   • Percentage threshold: <code>-1% to +30%</code>")
        lines.append("   • Only profitable opportunities within range")
        lines.append("")
        
        if isinstance(opportunities, list) and len(opportunities) > 0:
            lines.append(f"💰 <b>FOUND {len(opportunities)} PROFITABLE OPPORTUNITIES</b> 💰")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            
            for i, opp in enumerate(opportunities, 1):
                # Opportunity header
                lines.append(f"🎯 <b>OPPORTUNITY {i}</b>")
                lines.append("")
                
                # Match details
                lines.append(f"⚽ <b>Match:</b> <code>{opp.get('match_name', 'Unknown Match')}</code>")
                lines.append(f"🎲 <b>Market:</b> <code>{opp.get('market_type', '1X2')}</code>")
                lines.append("")
                
                # Odds comparison
                lines.append("📊 <b>ODDS COMPARISON</b>")
                orbit_odds = opp.get('orbit_lay_odds', 0)
                golbet_odds = opp.get('comparison_odds', 0)
                lines.append(f"   🔴 <b>Orbit LAY:</b> <code>{orbit_odds:.2f}</code>")
                lines.append(f"   🟢 <b>Golbet:</b> <code>{golbet_odds:.2f}</code>")
                lines.append("")
                
                # Profit analysis
                lines.append("💵 <b>PROFIT ANALYSIS</b>")
                odds_diff_str = opp.get('odds_difference', '0.00 (0.00%)')
                lines.append(f"   💰 <b>Difference:</b> <code>{odds_diff_str}</code>")
                
                # Calculate and show profit potential with threshold compliance
                if orbit_odds > 0 and golbet_odds > 0:
                    diff_abs = golbet_odds - orbit_odds
                    diff_percentage = (diff_abs / orbit_odds) * 100
                    
                    # Show threshold compliance
                    if -1 <= diff_percentage <= 30:
                        lines.append(f"   ✅ <b>Threshold Status:</b> <code>WITHIN RANGE</code>")
                        if diff_percentage > 0:
                            lines.append(f"   💚 <b>Profit Potential:</b> <code>+{diff_abs:.2f} (+{diff_percentage:.2f}%)</code>")
                        else:
                            lines.append(f"   🟡 <b>Risk Level:</b> <code>{diff_abs:.2f} ({diff_percentage:.2f}%)</code>")
                    else:
                        lines.append(f"   ❌ <b>Threshold Status:</b> <code>OUTSIDE RANGE</code>")
                        lines.append(f"   ⚠️ <b>Filtered Out:</b> <code>{diff_percentage:.2f}% not in -1% to +30%</code>")
                
                lines.append("")
                lines.append(f"⏰ <b>Detected:</b> <code>{opp.get('detection_time', 'N/A')}</code>")
                
                # Add separator between opportunities
                if i < len(opportunities):
                    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    lines.append("")
        
        else:
            lines.append("❌ <b>NO ARBITRAGE OPPORTUNITIES FOUND</b> ❌")
            lines.append("")
            lines.append("📋 <b>Possible Reasons:</b>")
            lines.append("   • No opportunities within -1% to +30% threshold")
            lines.append("   • All differences are outside the acceptable range")
            lines.append("   • Market conditions are unfavorable")
            lines.append("   • Data quality issues")
            lines.append("   • All odds are properly aligned")
            lines.append("")
            lines.append("💡 <b>Threshold Reminder:</b>")
            lines.append("   • Only opportunities with -1% ≤ difference ≤ +30%")
            lines.append("   • This ensures manageable risk levels")
            lines.append("   • Prevents extreme arbitrage situations")
        
        # Footer with status
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚡ <b>Real-time monitoring active</b>")
        lines.append("🎯 <b>Threshold filtering: -1% to +30%</b>")
        lines.append("🔄 <b>Next scan in 60 seconds</b>")
        
        return "\n".join(lines)
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a formatted version of the raw result
        lines = []
        lines.append("⚠️ <b>AI ANALYSIS PARSE ERROR</b> ⚠️")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("🔍 <b>Raw AI Response:</b>")
        lines.append(f"<code>{ai_result}</code>")
        lines.append("")
        lines.append("❌ <b>Error Details:</b>")
        lines.append(f"<code>{str(e)}</code>")
        lines.append("")
        lines.append("💡 <b>Suggestions:</b>")
        lines.append("   • Check AI response format")
        lines.append("   • Verify JSON structure")
        lines.append("   • Review prompt instructions")
        return "\n".join(lines)
