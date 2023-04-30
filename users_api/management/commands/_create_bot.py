from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import environ

env = environ.Env()
environ.Env.read_env()

storage = MemoryStorage()
bot = Bot(token=env('TOKEN'))
dp = Dispatcher(bot, storage=storage)
