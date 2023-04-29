from users_api.management.commands._create_bot import dp
from aiogram import types

async def start_command(message : types.Message):
    await message.reply("Hi!")

def register_handles():
    dp.register_message_handler(start_command, commands=['start', 'help'])