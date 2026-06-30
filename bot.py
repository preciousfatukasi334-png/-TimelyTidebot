import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable (Railway will set this)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Dictionary to store user preferences (in production, use a database)
user_data = {}

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"🌊 Hello {user.first_name}!\n\n"
        f"Welcome to TimelyTideBot! I'm here to provide you with tide information.\n\n"
        f"🔹 /tide - Get current tide information\n"
        f"🔹 /daily - Get today's tide forecast\n"
        f"🔹 /weekly - Get weekly tide forecast\n"
        f"🔹 /setlocation - Set your preferred location\n"
        f"🔹 /help - Show this message again\n\n"
        f"🚀 Let's get started! Use /setlocation to set your area first."
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    help_text = (
        "🌊 <b>TimelyTideBot Help</b>\n\n"
        "/start - Welcome message\n"
        "/tide - Get current tide information\n"
        "/daily - Get today's tide forecast\n"
        "/weekly - Get weekly tide forecast\n"
        "/setlocation - Set your preferred location\n"
        "/help - Show this help menu\n\n"
        "💡 <i>Tip: Use /setlocation to get accurate tide data for your area!</i>"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


async def tide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get current tide information."""
    user_id = update.effective_user.id
    location = user_data.get(user_id, {}).get("location", "Unknown Location")
    
    # This is sample data - replace with actual API call
    tide_info = get_sample_tide_data(location)
    
    message = (
        f"🌊 <b>Current Tide Information</b>\n"
        f"📍 Location: {location}\n"
        f"🕐 Time: {datetime.now().strftime('%H:%M')}\n"
        f"📊 {tide_info}\n\n"
        f"🔄 Use /daily for full day forecast"
    )
    await update.message.reply_text(message, parse_mode="HTML")


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get daily tide forecast."""
    user_id = update.effective_user.id
    location = user_data.get(user_id, {}).get("location", "Unknown Location")
    
    # Sample daily data
    daily_data = get_sample_daily_forecast(location)
    
    message = (
        f"📅 <b>Today's Tide Forecast</b>\n"
        f"📍 {location}\n"
        f"📆 {datetime.now().strftime('%A, %B %d, %Y')}\n\n"
        f"{daily_data}\n\n"
        f"📊 Use /weekly for 7-day forecast"
    )
    await update.message.reply_text(message, parse_mode="HTML")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get weekly tide forecast."""
    user_id = update.effective_user.id
    location = user_data.get(user_id, {}).get("location", "Unknown Location")
    
    # Sample weekly data
    weekly_data = get_sample_weekly_forecast(location)
    
    message = (
        f"📅 <b>Weekly Tide Forecast</b>\n"
        f"📍 {location}\n\n"
        f"{weekly_data}\n\n"
        f"🌊 Use /tide for real-time information"
    )
    await update.message.reply_text(message, parse_mode="HTML")


async def setlocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set user's preferred location."""
    keyboard = [
        [
            InlineKeyboardButton("🌊 Miami, FL", callback_data="miami"),
            InlineKeyboardButton("🌊 Los Angeles, CA", callback_data="la"),
        ],
        [
            InlineKeyboardButton("🌊 New York, NY", callback_data="ny"),
            InlineKeyboardButton("🌊 Seattle, WA", callback_data="seattle"),
        ],
        [
            InlineKeyboardButton("🌊 Custom Location", callback_data="custom"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📍 Please select your location:",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks for location selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    location_map = {
        "miami": "Miami, FL",
        "la": "Los Angeles, CA",
        "ny": "New York, NY",
        "seattle": "Seattle, WA",
    }
    
    if query.data in location_map:
        location = location_map[query.data]
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["location"] = location
        
        await query.edit_message_text(
            f"✅ Location set to: <b>{location}</b>\n\n"
            f"Now use /tide to get tide information!",
            parse_mode="HTML"
        )
    elif query.data == "custom":
        await query.edit_message_text(
            "🔧 Please type your location manually.\n"
            "Example: <b>San Francisco, CA</b>\n\n"
            "Send a message with your location.",
            parse_mode="HTML"
        )
        # Set a flag to expect custom location input
        context.user_data["awaiting_custom_location"] = True


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages (for custom location input)."""
    user_id = update.effective_user.id
    text = update.message.text
    
    if context.user_data.get("awaiting_custom_location"):
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["location"] = text
        context.user_data["awaiting_custom_location"] = False
        
        await update.message.reply_text(
            f"✅ Location set to: <b>{text}</b>\n\n"
            f"Use /tide to get tide information!",
            parse_mode="HTML"
        )
    else:
        # If user sends a regular message, suggest commands
        await update.message.reply_text(
            "🤔 I didn't understand that.\n"
            "Type /help to see available commands."
        )


# ============ DATA FUNCTIONS (Replace with real API) ============

def get_sample_tide_data(location: str) -> str:
    """Return sample tide data - replace with actual API call."""
    tides = [
        "🌅 High Tide: 6:30 AM (3.2 ft)",
        "🌅 Low Tide: 12:45 PM (0.5 ft)",
        "🌅 High Tide: 7:15 PM (2.8 ft)",
        "🌅 Low Tide: 11:30 PM (0.3 ft)",
    ]
    return "\n".join(tides)


def get_sample_daily_forecast(location: str) -> str:
    """Return sample daily forecast - replace with actual API call."""
    return (
        "🌅 6:30 AM - High Tide (3.2 ft)\n"
        "🌊 9:15 AM - Mid Tide (1.8 ft)\n"
        "🌅 12:45 PM - Low Tide (0.5 ft)\n"
        "🌊 3:30 PM - Mid Tide (1.9 ft)\n"
        "🌅 7:15 PM - High Tide (2.8 ft)\n"
        "🌊 11:30 PM - Low Tide (0.3 ft)"
    )


def get_sample_weekly_forecast(location: str) -> str:
    """Return sample weekly forecast - replace with actual API call."""
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return "\n".join([
        f"📅 {weekdays[i]}: High 3.2ft @ 6:30 AM | Low 0.5ft @ 12:45 PM"
        for i in range(7)
    ])


# ============ MAIN FUNCTION ============

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tide", tide))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))
    application.add_handler(CommandHandler("setlocation", setlocation))
    
    # Register callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Register message handler for text input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot (long polling)
    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
    
