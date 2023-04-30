from django.core.management.base import BaseCommand
from aiogram import executor, types
import asyncio
from users_api.management.commands._create_bot import dp
from  users_api.management.commands import _client
from  users_api.management.commands import _admin

class Command(BaseCommand):
    help = 'START BOT'

    def handle(self, *args, **options):
        _client.register_handles()
        _admin.register_handles()
        executor.start_polling(dp, skip_updates=True)