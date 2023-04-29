from django.core.management.base import BaseCommand
from aiogram import executor
from users_api.management.commands._create_bot import dp
from  users_api.management.commands import _client

class Command(BaseCommand):
    help = 'START BOT'

    def handle(self, *args, **options):
        _client.register_handles()
        executor.start_polling(dp, skip_updates=True)