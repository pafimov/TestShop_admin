from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from users_api.management.commands._constants import admins

class AdminFilter(BoundFilter):
    key = 'admin'

    def __init__(self, admin):
        self.admin = admin
    
    async def check(self, message : types.Message):
        user_id = message.from_id
        return user_id in admins
        