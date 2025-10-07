"""
Telegram bot logic and event handling.
"""

from typing import List
from telethon import TelegramClient, events
from loguru import logger
from command import Command
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME


class TelegramBot:
    def __init__(self, commands: List[Command]):
        self.commands = commands
        self.client = TelegramClient(
            TELEGRAM_SESSION_NAME,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        for command in self.commands:
            self._register_command(command)
    
    def _register_command(self, command: Command) -> None:
        @self.client.on(events.NewMessage(
            outgoing=True,
            pattern=command.get_pattern()
        ))
        async def handler(event):
            await command.execute(event)
    
    async def start(self) -> None:
        logger.info("Юзербот запускается...")
        await self.client.start()
        
        logger.info(f"Юзербот успешно запущен!")
        logger.info(f"Активные команды:")
        for cmd in self.commands:
            logger.info(f"  - {cmd.prefix}")
        
        await self.client.run_until_disconnected()
