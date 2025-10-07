import asyncio
from bot import TelegramBot
from command_registry import AVAILABLE_COMMANDS


# ============================================
# Configure which commands to use in the bot
# ============================================

ACTIVE_COMMANDS = [
    AVAILABLE_COMMANDS["kawai"],
]


# ============================================
# Main entry point
# ============================================

async def main():
    bot = TelegramBot(ACTIVE_COMMANDS)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
