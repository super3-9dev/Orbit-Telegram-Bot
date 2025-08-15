from __future__ import annotations
import asyncio
import os
import httpx
from typing import Dict, Any
from dotenv import load_dotenv
from .core.user_manager import UserManager
from .core.command_handler import CommandHandler
from datetime import datetime

# Load environment variables
load_dotenv()

class TelegramBot:
    """
    Main Telegram bot handler that processes incoming messages and commands.
    Manages user interactions and command processing.
    """
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        self.user_manager = UserManager()
        self.command_handler = CommandHandler(self.user_manager)
        
        # Bot information
        self.bot_info = None
        self.last_update_id = 0
        
        print(f"[TELEGRAM BOT] Initialized with token: {self.bot_token[:10]}...")
        print(f"[TELEGRAM BOT] {self.user_manager.get_user_count()} registered users loaded")
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information from Telegram."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        self.bot_info = data['result']
                        print(f"[TELEGRAM BOT] Bot info: @{self.bot_info['username']} ({self.bot_info['first_name']})")
                        return self.bot_info
        except Exception as e:
            print(f"[TELEGRAM BOT] Error getting bot info: {e}")
        return None
    
    async def get_updates(self) -> list:
        """Get updates from Telegram."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 5,  # Very short timeout for immediate response
                'allowed_updates': ['message']
            }
            
            print(f"[TELEGRAM BOT] Polling for updates with offset {self.last_update_id + 1}")
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        updates = data['result']
                        if updates:
                            self.last_update_id = updates[-1]['update_id']
                            print(f"[TELEGRAM BOT] Received {len(updates)} updates, new offset: {self.last_update_id}")
                        return updates
                    else:
                        print(f"[TELEGRAM BOT] Telegram API error: {data}")
                else:
                    print(f"[TELEGRAM BOT] HTTP error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[TELEGRAM BOT] Error getting updates: {e}")
        return []
    
    async def get_current_updates(self) -> list:
        """Get all current updates without offset to process pending messages."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {
                'timeout': 1,
                'allowed_updates': ['message']
            }
            
            print("[TELEGRAM BOT] Getting current updates to process pending messages...")
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        updates = data['result']
                        if updates:
                            self.last_update_id = updates[-1]['update_id']
                            print(f"[TELEGRAM BOT] Found {len(updates)} pending updates, new offset: {self.last_update_id}")
                        return updates
                else:
                    print(f"[TELEGRAM BOT] HTTP error getting current updates: {response.status_code}")
        except Exception as e:
            print(f"[TELEGRAM BOT] Error getting current updates: {e}")
        return []
    
    async def process_message(self, message: Dict[str, Any]) -> None:
        """Process a single message from Telegram."""
        try:
            # Extract message data
            chat_id = message['message']['chat']['id']
            user_id = message['message']['from']['id']
            text = message['message'].get('text', '')
            username = message['message']['from'].get('username')
            first_name = message['message']['from'].get('first_name')
            
            print(f"[TELEGRAM BOT] Message from user {user_id} (@{username}): '{text}'")
            print(f"[TELEGRAM BOT] Chat ID: {chat_id}, User ID: {user_id}")
            
            # Check for admin commands first
            if text.strip().lower() in ['broadcast', 'status']:
                print(f"[TELEGRAM BOT] Processing admin command: {text}")
                await self.handle_admin_command(message)
                return
            
            # Check if this is a start command before processing
            is_start_command = text.strip().lower() in ['start', '/start']
            was_registered_before = self.user_manager.is_registered(user_id)
            
            print(f"[TELEGRAM BOT] Is start command: {is_start_command}")
            print(f"[TELEGRAM BOT] Was registered before: {was_registered_before}")
            
            # Process the command immediately
            print(f"[TELEGRAM BOT] Processing command...")
            response = await self.command_handler.process_command(user_id, text, username, first_name)
            print(f"[TELEGRAM BOT] Command response: {response[:100]}...")
            
            # Send response back to user immediately
            print(f"[TELEGRAM BOT] Sending response to user...")
            success = await self.send_message(chat_id, response)
            
            if not success:
                print(f"[TELEGRAM BOT] ❌ Failed to send response to user {user_id}")
                return
            
            # If this was a successful registration (start command and user is now registered)
            if is_start_command and not was_registered_before and self.user_manager.is_registered(user_id):
                print(f"[TELEGRAM BOT] 🎉 New user registered, sending welcome message to {user_id}")
                welcome_msg = self.command_handler._get_welcome_message(username or first_name)
                
                # Send welcome message after a short delay
                await asyncio.sleep(1)  # Small delay between messages
                welcome_success = await self.send_message(chat_id, welcome_msg)
                
                if welcome_success:
                    print(f"[TELEGRAM BOT] ✅ Welcome message sent successfully to {user_id}")
                    
                    # Schedule broadcast message to all registered users after 1 minute
                    broadcast_message = f"""📢 <b>NEW USER REGISTRATION</b> 📢

👋 A new user has joined the arbitrage bot!

👤 <b>User:</b> {username or first_name or 'Unknown'}
🆔 <b>User ID:</b> {user_id}
⏰ <b>Registered:</b> Just now

🎯 <b>Total Registered Users:</b> {self.user_manager.get_user_count()}

🚀 <b>Welcome aboard!</b> The arbitrage opportunities will be shared with all registered users.

Happy trading! 🎯💰"""
                    
                    # Schedule the broadcast in a separate task
                    asyncio.create_task(self.schedule_broadcast(broadcast_message, 60))
                    print(f"[TELEGRAM BOT] 📅 Scheduled broadcast message in 60 seconds")
                    
                else:
                    print(f"[TELEGRAM BOT] ❌ Failed to send welcome message to {user_id}")
            else:
                print(f"[TELEGRAM BOT] ℹ️ No welcome message needed")
                print(f"[TELEGRAM BOT] Is start command: {is_start_command}")
                print(f"[TELEGRAM BOT] Was registered before: {was_registered_before}")
                print(f"[TELEGRAM BOT] Is registered now: {self.user_manager.is_registered(user_id)}")
            
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send a message to a specific chat."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    print(f"[TELEGRAM BOT] Message sent to {chat_id}")
                    return True
                else:
                    print(f"[TELEGRAM BOT] Failed to send message. Status: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"[TELEGRAM BOT] Error sending message: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test the bot's connection to Telegram."""
        try:
            print("[TELEGRAM BOT] Testing connection to Telegram...")
            
            # Test getMe endpoint
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        bot_info = data['result']
                        print(f"[TELEGRAM BOT] ✅ Connection successful!")
                        print(f"[TELEGRAM BOT] Bot: @{bot_info['username']} ({bot_info['first_name']})")
                        print(f"[TELEGRAM BOT] Bot ID: {bot_info['id']}")
                        return True
                    else:
                        print(f"[TELEGRAM BOT] ❌ Telegram API error: {data}")
                        return False
                else:
                    print(f"[TELEGRAM BOT] ❌ HTTP error: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Connection test failed: {e}")
            return False
    
    async def clear_webhook(self) -> bool:
        """Clear any existing webhook to ensure polling works correctly."""
        try:
            print("[TELEGRAM BOT] Clearing any existing webhook...")
            url = f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
            params = {'drop_pending_updates': 'true'}
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        print("[TELEGRAM BOT] ✅ Webhook cleared successfully")
                        return True
                    else:
                        print(f"[TELEGRAM BOT] ❌ Failed to clear webhook: {data}")
                        return False
                else:
                    print(f"[TELEGRAM BOT] ❌ HTTP error clearing webhook: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error clearing webhook: {e}")
            return False
    
    async def test_message_sending(self, chat_id: int) -> bool:
        """Test if the bot can send messages to a specific chat."""
        try:
            test_message = "🧪 <b>BOT RESPONSIVENESS TEST</b> 🧪\n\n✅ Bot is working and can send messages!\n⏰ Test completed at: " + str(datetime.now())
            
            print(f"[TELEGRAM BOT] Testing message sending to chat {chat_id}...")
            success = await self.send_message(chat_id, test_message)
            
            if success:
                print(f"[TELEGRAM BOT] ✅ Test message sent successfully to {chat_id}")
            else:
                print(f"[TELEGRAM BOT] ❌ Failed to send test message to {chat_id}")
            
            return success
            
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error in message sending test: {e}")
            return False
    
    async def run(self) -> None:
        """Main bot loop - continuously process messages."""
        print("[TELEGRAM BOT] Starting bot...")
        
        # Test connection first
        if not await self.test_connection():
            print("[TELEGRAM BOT] ❌ Connection test failed, exiting")
            return
        
        # Clear any existing webhook to ensure polling works
        await self.clear_webhook()
        
        # Get bot info
        bot_info = await self.get_bot_info()
        if not bot_info:
            print("[TELEGRAM BOT] ❌ Failed to get bot info, exiting")
            return
        
        print(f"[TELEGRAM BOT] 🚀 Bot @{bot_info['username']} is now running!")
        print("[TELEGRAM BOT] 📱 Send 'start' or '/start' to register for arbitrage notifications")
        print("[TELEGRAM BOT] 🛑 Press Ctrl+C to stop")
        
        # Process any pending messages first
        print("[TELEGRAM BOT] 🔍 Checking for pending messages...")
        pending_updates = await self.get_current_updates()
        if pending_updates:
            print(f"[TELEGRAM BOT] 📨 Processing {len(pending_updates)} pending messages...")
            for update in pending_updates:
                if 'message' in update:
                    print(f"[TELEGRAM BOT] 📨 Processing pending update: {update['update_id']}")
                    await self.process_message(update)
            print("[TELEGRAM BOT] ✅ Pending messages processed")
        else:
            print("[TELEGRAM BOT] ✅ No pending messages found")
        
        print("[TELEGRAM BOT] 🔍 Now listening for new messages...")
        print("[TELEGRAM BOT] 📊 Arbitrage results will be sent automatically when detected")
        
        try:
            while True:
                try:
                    # Get updates
                    updates = await self.get_updates()
                    
                    # Process each update immediately
                    for update in updates:
                        if 'message' in update:
                            print(f"[TELEGRAM BOT] 📨 Processing new update: {update['update_id']}")
                            await self.process_message(update)
                    
                    # Very short delay for responsive message handling
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"[TELEGRAM BOT] ❌ Error in main loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except KeyboardInterrupt:
            print("\n[TELEGRAM BOT] 🛑 Bot stopped by user")
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Unexpected error: {e}")
        finally:
            print("[TELEGRAM BOT] 🔄 Bot shutdown complete")

    async def broadcast_to_users(self, message: str) -> None:
        """Broadcast a message to all registered users."""
        try:
            registered_users = self.user_manager.get_registered_users()
            if not registered_users:
                print("[TELEGRAM BOT] No registered users to broadcast to")
                return
            
            print(f"[TELEGRAM BOT] Broadcasting message to {len(registered_users)} users...")
            
            for user_id in registered_users:
                try:
                    # Get user info for personalization
                    user_info = self.user_manager.get_user_info(user_id)
                    username = user_info.get('username', 'User')
                    first_name = user_info.get('first_name', 'User')
                    
                    # Personalize message
                    personalized_message = message.replace("{username}", username).replace("{first_name}", first_name)
                    
                    # Send message to user
                    success = await self.send_message(user_id, personalized_message)
                    if success:
                        print(f"[TELEGRAM BOT] ✅ Message sent to user {user_id} ({username or first_name})")
                        # Update user activity
                        self.user_manager.update_user_activity(user_id)
                    else:
                        print(f"[TELEGRAM BOT] ❌ Failed to send message to user {user_id}")
                        
                except Exception as e:
                    print(f"[TELEGRAM BOT] ❌ Error sending message to user {user_id}: {e}")
                    continue
            
            print(f"[TELEGRAM BOT] ✅ Broadcasting completed to {len(registered_users)} users")
            
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error in broadcasting: {e}")
    
    async def schedule_broadcast(self, message: str, delay_seconds: int = 60) -> None:
        """Schedule a broadcast message after a delay."""
        print(f"[TELEGRAM BOT] 📅 Scheduling broadcast in {delay_seconds} seconds...")
        await asyncio.sleep(delay_seconds)
        await self.broadcast_to_users(message)

    async def handle_admin_command(self, message: Dict[str, Any]) -> None:
        """Handle admin commands for testing and management."""
        try:
            chat_id = message['message']['chat']['id']
            user_id = message['message']['from']['id']
            text = message['message'].get('text', '')
            
            # Check if this is an admin command
            if text.strip().lower() == 'broadcast':
                # Send test broadcast immediately
                test_message = f"""🧪 <b>ADMIN BROADCAST TEST</b> 🧪

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 <b>Admin:</b> {user_id}
📢 <b>Type:</b> Manual broadcast test

🎯 <b>This is a test message to all registered users!</b>

✅ <b>Bot is working correctly!</b>"""
                
                await self.broadcast_to_users(test_message)
                await self.send_message(chat_id, "✅ Test broadcast sent to all registered users!")
                
            elif text.strip().lower() == 'status':
                # Send bot status
                registered_users = self.user_manager.get_registered_users()
                status_message = f"""📊 <b>BOT STATUS</b> 📊

🤖 <b>Bot:</b> @{self.bot_info['username'] if self.bot_info else 'Unknown'}
👥 <b>Registered Users:</b> {len(registered_users)}
⏰ <b>Uptime:</b> Active
🔄 <b>Status:</b> Running

📱 <b>Commands:</b>
   • start - Register for notifications
   • broadcast - Send test message (admin)
   • status - Show bot status (admin)

🎯 <b>Bot is operational!</b>"""
                
                await self.send_message(chat_id, status_message)
                
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error in admin command: {e}")
            await self.send_message(chat_id, "❌ Error processing admin command")

    async def send_arbitrage_results(self, arbitrage_data: str) -> None:
        """Send arbitrage results to all registered users."""
        try:
            registered_users = self.user_manager.get_registered_users()
            if not registered_users:
                print("[TELEGRAM BOT] No registered users to send arbitrage results to")
                return
            
            print(f"[TELEGRAM BOT] Sending arbitrage results to {len(registered_users)} users...")
            
            # Format the arbitrage message
            arbitrage_message = f"""🎯 <b>ARBITRAGE OPPORTUNITIES DETECTED!</b> 🎯

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> {len(registered_users)} registered users

{arbitrage_data}

🚀 <b>Happy arbitrage hunting!</b> 💰"""
            
            await self.broadcast_to_users(arbitrage_message)
            print(f"[TELEGRAM BOT] ✅ Arbitrage results sent to {len(registered_users)} users")
            
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error sending arbitrage results: {e}")
    
    async def send_no_opportunities_message(self) -> None:
        """Send message when no arbitrage opportunities are found."""
        try:
            registered_users = self.user_manager.get_registered_users()
            if not registered_users:
                return
            
            no_opportunities_message = f"""🔍 <b>ARBITRAGE SCAN COMPLETED</b> 🔍

⏰ <b>Scan Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> {len(registered_users)} registered users

📊 <b>Scan Results:</b>
   • ✅ <b>Data Collection:</b> Successful
   • ✅ <b>AI Analysis:</b> Completed
   • ❌ <b>Opportunities Found:</b> None

🎯 <b>Threshold Filtering:</b>
   • <b>Range:</b> -1% to +30%
   • <b>Status:</b> Applied successfully
   • <b>Result:</b> No opportunities met criteria

💡 <b>What This Means:</b>
   • Market conditions are currently unfavorable
   • Odds are too close or outside profitable range
   • This is normal - opportunities come and go
   • Stay patient and keep monitoring

🔄 <b>Next Actions:</b>
   • <b>Next Scan:</b> In 60 seconds
   • <b>Continuous Monitoring:</b> Active
   • <b>Real-time Alerts:</b> Ready

🌟 <b>Stay Optimistic!</b>
   • Opportunities will appear when market conditions change
   • The bot is working correctly and protecting you from bad bets
   • Quality over quantity - we only want profitable opportunities

🎯 <b>Keep monitoring - your next big opportunity is coming!</b> 💰🚀"""
            
            await self.broadcast_to_users(no_opportunities_message)
            print(f"[TELEGRAM BOT] ✅ Enhanced no opportunities message sent to {len(registered_users)} users")
            
        except Exception as e:
            print(f"[TELEGRAM BOT] ❌ Error sending no opportunities message: {e}")

async def main():
    """Main function to run the Telegram bot."""
    try:
        bot = TelegramBot()
        await bot.run()
    except Exception as e:
        print(f"[MAIN] Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
