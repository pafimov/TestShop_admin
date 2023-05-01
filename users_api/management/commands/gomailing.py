from django.core.management.base import BaseCommand
from users_api.models import UserFree
from users_api.management.commands._create_bot import bot
import asyncio

class Command(BaseCommand):
    help = 'START BOT'
    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)
        parser.add_argument('text', nargs='+', type=str)
    
    async def create_run_tasks(self, users, path, text):
        tasks = []
        for user in users:
            f = open(path, 'rb')
            tasks.append(asyncio.create_task(bot.send_photo(user.telegram_id, photo=f, caption=text)))
        await asyncio.wait(tasks)

    def handle(self, *args, **options):
        print("XD")
        path = options['path'][0]
        text = options['text'][0]
        users = UserFree.objects.all()
        users = list(users)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.create_run_tasks(users, path, text))
        loop.close()
        # print(options)