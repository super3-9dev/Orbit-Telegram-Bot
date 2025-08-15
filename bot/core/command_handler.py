from __future__ import annotations
from typing import Dict, Callable, Any
from .user_manager import UserManager

class CommandHandler:
    """
    Handles Telegram bot commands and user interactions.
    Processes commands like 'start', 'stop', 'status', etc.
    """
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.commands: Dict[str, Callable] = {
            'start': self.handle_start,
            'stop': self.handle_stop,
            'status': self.handle_status,
            'help': self.handle_help,
            'info': self.handle_info
        }
        
        print(f"[COMMAND HANDLER] Initialized with commands: {list(self.commands.keys())}")
        print(f"[COMMAND HANDLER] User manager: {type(user_manager).__name__}")
    
    async def process_command(self, user_id: int, message_text: str, username: str = None, first_name: str = None) -> str:
        """
        Process incoming Telegram messages and execute appropriate commands.
        
        Args:
            user_id: Telegram user ID
            message_text: Text content of the message
            username: Telegram username (optional)
            first_name: User's first name (optional)
            
        Returns:
            str: Response message to send back
        """
        # Clean and normalize the command
        command = message_text.strip().lower()
        
        # Remove leading slash if present for command matching
        clean_command = command.lstrip('/')
        
        print(f"[COMMAND HANDLER] Processing message: '{message_text}' -> clean: '{clean_command}'")
        print(f"[COMMAND HANDLER] Available commands: {list(self.commands.keys())}")
        
        # Check if it's a known command (with or without slash)
        if clean_command in self.commands:
            print(f"[COMMAND HANDLER] Command '{clean_command}' recognized, executing...")
            try:
                return await self.commands[clean_command](user_id, username, first_name)
            except Exception as e:
                print(f"[COMMAND HANDLER] Error processing command '{clean_command}': {e}")
                return self._get_error_message()
        else:
            print(f"[COMMAND HANDLER] Command '{clean_command}' not recognized")
        
        # Unknown command
        return self._get_unknown_command_message()
    
    async def handle_start(self, user_id: int, username: str = None, first_name: str = None) -> str:
        """Handle the 'start' command - register user for notifications."""
        try:
            # Check if user is already registered
            if self.user_manager.is_registered(user_id):
                return self._get_already_registered_message(username or first_name)
            
            # Register the new user
            is_new = self.user_manager.register_user(user_id, username, first_name)
            
            if is_new:
                # Return success message (welcome message will be sent separately)
                return self._get_registration_success_message(username or first_name)
            else:
                return self._get_registration_error_message()
                
        except Exception as e:
            print(f"[COMMAND HANDLER] Error in start command: {e}")
            return self._get_error_message()
    
    async def handle_stop(self, user_id: int, username: str = None, first_name: str = None) -> str:
        """Handle the 'stop' command - unregister user from notifications."""
        try:
            if not self.user_manager.is_registered(user_id):
                return self._get_not_registered_message()
            
            # Unregister the user
            self.user_manager.unregister_user(user_id)
            
            return self._get_unregistration_message(username or first_name)
            
        except Exception as e:
            print(f"[COMMAND HANDLER] Error in stop command: {e}")
            return self._get_error_message()
    
    async def handle_status(self, user_id: int, username: str = None, first_name: str = None) -> str:
        """Handle the 'status' command - show user's current status."""
        try:
            if not self.user_manager.is_registered(user_id):
                return self._get_not_registered_message()
            
            user_info = self.user_manager.get_user_info(user_id)
            return self._get_status_message(user_info, username or first_name)
            
        except Exception as e:
            print(f"[COMMAND HANDLER] Error in status command: {e}")
            return self._get_error_message()
    
    async def handle_help(self, user_id: int, username: str = None, first_name: str = None) -> str:
        """Handle the 'help' command - show available commands."""
        return self._get_help_message()
    
    async def handle_info(self, user_id: int, username: str = None, first_name: str = None) -> str:
        """Handle the 'info' command - show bot information."""
        return self._get_info_message()
    
    def _get_welcome_message(self, name: str) -> str:
        """Generate welcome message for new users."""
        return f"""🎉 <b>WELCOME TO ARBITRAGE BOT!</b> 🎉

👋 Hello <b>{name}</b>!

🚀 <b>You're now registered for arbitrage notifications!</b>

📊 <b>What you'll receive:</b>
   • Real-time arbitrage opportunities
   • Professional analysis reports
   • Profit potential calculations
   • Market insights and trends

⚡ <b>Notifications will be sent:</b>
   • Every 60 seconds during active scanning
   • Only when profitable opportunities are found
   • With detailed analysis and formatting

🎯 <b>Current Threshold:</b> -1% to +30% difference

💡 <b>Commands:</b>
   /start - Register for notifications
   /stop - Stop notifications
   /status - Check your status
   /help - Show all commands
   /info - Bot information

🔔 <b>You'll start receiving notifications immediately!</b>

Happy arbitrage hunting! 🚀💰"""
    
    def _get_registration_success_message(self, name: str) -> str:
        """Generate registration success message."""
        return f"""✅ <b>REGISTRATION SUCCESSFUL!</b> ✅

👋 Welcome aboard, <b>{name}</b>!

🎯 <b>You're now registered for arbitrage notifications!</b>

📱 <b>What happens next:</b>
   • You'll receive real-time arbitrage reports
   • Notifications every 60 seconds when opportunities arise
   • Professional analysis with profit calculations
   • Market insights and risk assessments

⚡ <b>First notification coming soon...</b>

💡 <b>Need help?</b> Send /help for available commands.

Happy trading! 🚀💰"""
    
    def _get_already_registered_message(self, name: str) -> str:
        """Generate message for already registered users."""
        return f"""ℹ️ <b>ALREADY REGISTERED</b> ℹ️

👋 Hello <b>{name}</b>!

✅ <b>You're already registered for notifications!</b>

📊 <b>Your current status:</b>
   • Receiving arbitrage reports
   • Active notification subscription
   • Real-time market monitoring

💡 <b>Commands:</b>
   /stop - Stop notifications
   /status - Check your status
   /help - Show all commands

🔔 <b>Continue receiving notifications as usual!</b>"""
    
    def _get_unregistration_message(self, name: str) -> str:
        """Generate unregistration confirmation message."""
        return f"""🛑 <b>NOTIFICATIONS STOPPED</b> 🛑

👋 Goodbye <b>{name}</b>!

❌ <b>You've been unregistered from notifications.</b>

📱 <b>What this means:</b>
   • No more arbitrage reports
   • Bot will stop sending messages
   • You can re-register anytime with /start

💡 <b>To re-enable notifications:</b>
   Send /start again

🔔 <b>Thanks for using Arbitrage Bot!</b>

Come back anytime! 👋"""
    
    def _get_not_registered_message(self) -> str:
        """Generate message for non-registered users."""
        return """❌ <b>NOT REGISTERED</b> ❌

⚠️ <b>You're not currently registered for notifications.</b>

📱 <b>To start receiving arbitrage reports:</b>
   Send /start to register

💡 <b>Available commands:</b>
   /start - Register for notifications
   /help - Show all commands
   /info - Bot information

🔔 <b>Register now to start receiving notifications!</b>"""
    
    def _get_status_message(self, user_info: dict, name: str) -> str:
        """Generate status message for registered users."""
        registered_at = user_info.get('registered_at', 'Unknown')
        last_notification = user_info.get('last_notification', 'Never')
        total_notifications = user_info.get('total_notifications', 0)
        
        return f"""📊 <b>USER STATUS</b> 📊

👤 <b>User:</b> {name}
✅ <b>Status:</b> Registered for notifications
📅 <b>Registered:</b> {registered_at}
🔔 <b>Last Notification:</b> {last_notification}
📈 <b>Total Notifications:</b> {total_notifications}

🎯 <b>Current Status:</b> Active
⚡ <b>Receiving:</b> Real-time arbitrage reports
🔄 <b>Scan Frequency:</b> Every 60 seconds

💡 <b>Commands:</b>
   /stop - Stop notifications
   /help - Show all commands
   /info - Bot information

🔔 <b>You're all set for arbitrage notifications!</b>"""
    
    def _get_help_message(self) -> str:
        """Generate help message with all available commands."""
        return """📚 <b>ARBITRAGE BOT COMMANDS</b> 📚

🚀 <b>Available Commands:</b>

/start - Register for arbitrage notifications
   • Start receiving real-time arbitrage reports
   • Get professional analysis and insights
   • Monitor profitable opportunities

/stop - Stop notifications
   • Unregister from the notification system
   • Stop receiving arbitrage reports
   • Can re-register anytime with /start

/status - Check your status
   • View registration details
   • See notification history
   • Check current subscription status

/help - Show this help message
   • Display all available commands
   • Get usage instructions

/info - Bot information
   • Learn about the bot's features
   • Understand how it works
   • Get technical details

📱 <b>How to use:</b>
   1. Send /start to register
   2. Receive notifications automatically
   3. Send /stop to unsubscribe
   4. Re-register anytime with /start

💡 <b>Need more help?</b>
   Contact the bot administrator

Happy arbitrage hunting! 🚀💰"""
    
    def _get_info_message(self) -> str:
        """Generate information message about the bot."""
        return """🤖 <b>ARBITRAGE BOT INFORMATION</b> 🤖

🎯 <b>What is this bot?</b>
   • Real-time arbitrage opportunity detector
   • Monitors Orbit LAY odds vs Golbet odds
   • Uses AI-powered analysis (OpenAI GPT-4)
   • Sends professional Telegram notifications

⚡ <b>How it works:</b>
   • Scrapes betting data from multiple sites
   • Compares odds using advanced algorithms
   • Filters opportunities by risk threshold
   • Sends formatted reports every 60 seconds

📊 <b>Features:</b>
   • Football 1X2 market analysis
   • -1% to +30% threshold filtering
   • Professional notification formatting
   • Persistent user management
   • Error handling and recovery

🔒 <b>Security:</b>
   • No hardcoded credentials
   • Environment variable configuration
   • Secure user data storage
   • Privacy-focused design

📈 <b>Performance:</b>
   • Asynchronous operation
   • Efficient data processing
   • Minimal resource usage
   • Scalable architecture

💡 <b>Technology Stack:</b>
   • Python 3.11+
   • Playwright for web scraping
   • OpenAI GPT-4 for analysis
   • Telegram Bot API
   • Pydantic for data validation

🚀 <b>Ready to start?</b>
   Send /start to register for notifications!

Happy trading! 🎯💰"""
    
    def _get_unknown_command_message(self) -> str:
        """Generate message for unknown commands."""
        return """❓ <b>UNKNOWN COMMAND</b> ❓

⚠️ <b>I don't recognize that command.</b>

💡 <b>Available commands:</b>
   /start - Register for notifications
   /stop - Stop notifications
   /status - Check your status
   /help - Show all commands
   /info - Bot information

🔔 <b>Send /help for a complete command list.</b>"""
    
    def _get_error_message(self) -> str:
        """Generate generic error message."""
        return """🚨 <b>ERROR OCCURRED</b> 🚨

❌ <b>Something went wrong while processing your request.</b>

💡 <b>Please try again or contact support if the problem persists.</b>

🔔 <b>Available commands:</b>
   /start - Register for notifications
   /help - Show all commands"""
    
    def _get_registration_error_message(self) -> str:
        """Generate registration error message."""
        return """❌ <b>REGISTRATION ERROR</b> ❌

⚠️ <b>Failed to register you for notifications.</b>

💡 <b>Please try again or contact support if the problem persists.</b>

🔔 <b>Available commands:</b>
   /start - Try registration again
   /help - Show all commands"""
