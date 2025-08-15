#!/usr/bin/env python3
"""
Notification module for sending Telegram messages.
"""

import os
import httpx
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def format_alert(opportunity: Dict) -> str:
    """
    Format a single arbitrage opportunity alert.
    
    Args:
        opportunity: Dictionary containing opportunity data
        
    Returns:
        Formatted alert message
    """
    try:
        match_name = opportunity.get('match_name', 'Unknown Match')
        orbit_odds = opportunity.get('orbit_lay_odds', 'N/A')
        comparison_odds = opportunity.get('comparison_odds', 'N/A')
        odds_diff = opportunity.get('odds_difference', 'N/A')
        market_type = opportunity.get('market_type', 'N/A')
        detection_time = opportunity.get('detection_time', 'N/A')
        
        message = f"""🎯 <b>ARBITRAGE OPPORTUNITY DETECTED!</b> 🎯

⚽ <b>Match:</b> {match_name}
🏟️ <b>Market:</b> {market_type}
📊 <b>Orbit LAY:</b> {orbit_odds}
📊 <b>Golbet:</b> {comparison_odds}
💰 <b>Difference:</b> {odds_diff}
⏰ <b>Detected:</b> {detection_time}

💡 <b>How to Use:</b>
   • <b>Lay</b> on Orbit at the LAY odds
   • <b>Back</b> on Golbet at the comparison odds
   • <b>Profit</b> from the odds difference

🚀 <b>Happy arbitrage hunting!</b> 💰"""
        
        return message
        
    except Exception as e:
        print(f"Error formatting alert: {e}")
        return f"🎯 <b>ARBITRAGE OPPORTUNITY</b> 🎯\n\n{str(opportunity)}"

def format_arbitrage_results(result: List[Dict], orbit_data: List[Dict], golbet_data: List[Dict]) -> str:
    """
    Format arbitrage opportunities results for the new Python-based system.
    
    Args:
        result: List of arbitrage opportunities
        orbit_data: Orbit market data
        golbet_data: Golbet market data
        
    Returns:
        Formatted message
    """
    try:
        if not result or not isinstance(result, list) or len(result) == 0:
            return "❌ No arbitrage opportunities found in this analysis cycle."
        
        lines = []
        lines.append("🎯 <b>ARBITRAGE OPPORTUNITIES DETECTED!</b> 🎯")
        lines.append("")
        
        lines.append(f"📊 <b>Analysis Summary:</b>")
        lines.append(f"   • <b>Total Opportunities:</b> {len(result)}")
        lines.append(f"   • <b>Threshold Applied:</b> -1% to +30%")
        lines.append(f"   • <b>Data Sources:</b> Orbit + Golbet")
        lines.append(f"   • <b>Matching Method:</b> Python-based (no AI)")
        lines.append("")
        
        lines.append("⚽ <b>Opportunities Found:</b>")
        lines.append("")
        
        for i, opp in enumerate(result, 1):
            try:
                match_name = opp.get('match_name', 'Unknown Match')
                orbit_odds = opp.get('orbit_lay_odds', 'N/A')
                comparison_odds = opp.get('comparison_odds', 'N/A')
                odds_diff = opp.get('odds_difference', 'N/A')
                market_type = opp.get('market_type', 'N/A')
                detection_time = opp.get('detection_time', 'N/A')
                
                lines.append(f"<b>{i}. {match_name}</b>")
                lines.append(f"   🏟️ <b>Market:</b> {market_type}")
                lines.append(f"   📊 <b>Orbit LAY:</b> {orbit_odds}")
                lines.append(f"   📊 <b>Golbet:</b> {comparison_odds}")
                lines.append(f"   💰 <b>Difference:</b> {odds_diff}")
                lines.append(f"   ⏰ <b>Detected:</b> {detection_time}")
                
                if i < len(result):
                    lines.append("   ─────────────────────")
                lines.append("")
            except Exception as e:
                print(f"Error formatting opportunity {i}: {e}")
                continue
        
        lines.append("💡 <b>How to Use:</b>")
        lines.append("   • <b>Lay</b> on Orbit at the LAY odds")
        lines.append("   • <b>Back</b> on Golbet at the comparison odds")
        lines.append("   • <b>Profit</b> from the odds difference")
        lines.append("")
        lines.append("🚀 <b>Happy arbitrage hunting!</b> 💰")
        
        return "\n".join(lines)
        
    except Exception as e:
        print(f"Error formatting arbitrage results: {e}")
        return f"""🎯 <b>ARBITRAGE OPPORTUNITIES</b> 🎯

🤖 <b>Python Analysis Result:</b>
{str(result)}

⚠️ <b>Note:</b> Raw result displayed due to formatting error."""

def format_ai_analysis_result(result, orbit_data, golbet_data):
    """
    Format AI analysis result into a clean, readable message.
    This function is kept for backward compatibility but now calls the new function.
    """
    return format_arbitrage_results(result, orbit_data, golbet_data)

async def send_telegram(message: str, chat_id: Optional[str] = None) -> bool:
    """
    Send a message to Telegram.
    
    Args:
        message: Message to send
        chat_id: Optional chat ID (if not provided, uses default)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not TELEGRAM_BOT_TOKEN:
            print("❌ TELEGRAM_BOT_TOKEN not set")
            return False
        
        target_chat_id = chat_id or TELEGRAM_CHAT_ID
        if not target_chat_id:
            print("❌ No chat ID available")
            return False
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        data = {
            "chat_id": target_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram message sent successfully to {target_chat_id}")
                return True
            else:
                print(f"❌ Failed to send Telegram message: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

async def broadcast_to_users(message: str, user_ids: List[str]) -> None:
    """
    Send a message to multiple users.
    
    Args:
        message: Message to send
        user_ids: List of user IDs to send to
    """
    if not user_ids:
        print("⚠️ No users to broadcast to")
        return
    
    print(f"📢 Broadcasting message to {len(user_ids)} users...")
    
    success_count = 0
    for user_id in user_ids:
        try:
            if await send_telegram(message, user_id):
                success_count += 1
            else:
                print(f"❌ Failed to send to user {user_id}")
        except Exception as e:
            print(f"❌ Error sending to user {user_id}: {e}")
    
    print(f"📢 Broadcast completed: {success_count}/{len(user_ids)} successful")
