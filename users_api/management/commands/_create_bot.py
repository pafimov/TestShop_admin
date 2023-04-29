from aiogram import Bot, Dispatcher
import environ

env = environ.Env()
environ.Env.read_env()

bot = Bot(token=env('TOKEN'))
dp = Dispatcher(bot)
