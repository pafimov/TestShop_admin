from users_api.management.commands._create_bot import dp
from users_api.management.commands._constants import categories
from users_api.management.commands._keyboards import get_categories, get_subcategories
from users_api.management.commands._client import change_page, subchange_page
from aiogram import types
from users_api.models import Thing
from users_api.management.commands._filters import AdminFilter
from asgiref.sync import sync_to_async
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAddThing(StatesGroup):
    choosing_category = State()
    choosing_subcategory = State()
    choosing_name = State()
    choosing_description = State()
    choosing_price = State()
    choosing_pic = State()

async def add_thing(message : types.Message, state : FSMContext):
    kb = await get_categories(0)
    await message.answer('Выберите категорию:', reply_markup=kb)
    await state.set_state(FSMAddThing.choosing_category)

async def category_chosen(callback : types.CallbackQuery, state : FSMContext):
    message = callback.message
    category = int(callback.data[callback.data.index('_')+1:])
    await state.update_data(category=category)
    await message.delete()
    await state.set_state(FSMAddThing.choosing_subcategory)
    kb = await get_subcategories((await state.get_data())['category'], 0)
    await message.answer('Выберите подкатегорию:', reply_markup=kb)
    await callback.answer()

async def subcategory_chosen(callback : types.CallbackQuery, state : FSMContext):
    message = callback.message
    subcategory = int(callback.data[callback.data.index('_')+1:])
    await state.update_data(subcategory=subcategory)
    await message.delete()
    await state.set_state(FSMAddThing.choosing_name)
    await message.answer("Введите название товара:")
    await callback.answer()

async def name_chosen(message : types.Message, state : FSMContext):
    name = message.text
    if len(name) > 70:
        await message.reply("Слишком длинное название.")
        return
    
    await state.update_data(name=name)
    await message.answer("Введите описание товара:")
    await state.set_state(FSMAddThing.choosing_description)

async def description_chosen(message : types.Message, state : FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.answer("Введите цену товара:")
    await state.set_state(FSMAddThing.choosing_price)

async def price_chosen(message : types.Message, state : FSMContext):
    price = message.text
    try:
        price = int(price)
    except Exception:
        await message.reply("Введите корректное число!")
        return
    if price <= 0:
        await message.reply("Цена должна быть неотрицательной!")
        return
    await state.update_data(price=price)
    await message.answer("Отправьте фотографию товара:")
    await state.set_state(FSMAddThing.choosing_pic)

async def pic_chosen(message : types.Message, state : FSMContext):
    pic = message.photo[-1].file_id
    await state.update_data(pic=pic)
    data = await state.get_data()
    new_thing = Thing(category=data['category'], subcategory=data['subcategory'], name=data['name'],
                      description=data['description'], pic_id=data['pic'], price=data['price'])
    await new_thing.asave()
    await message.answer("Товар успешно добавлен!")
    await state.finish()

def register_handles():
    dp.filters_factory.bind(AdminFilter)
    dp.register_message_handler(add_thing, commands=['add'], admin=1)
    dp.register_callback_query_handler(category_chosen, Text(startswith="chosen_"), state=FSMAddThing.choosing_category)
    dp.register_callback_query_handler(subcategory_chosen, Text(startswith="subchosen_"), state=FSMAddThing.choosing_subcategory)
    dp.register_message_handler(name_chosen, state=FSMAddThing.choosing_name, content_types=['text'])
    dp.register_message_handler(description_chosen, state=FSMAddThing.choosing_description, content_types=['text'])
    dp.register_message_handler(price_chosen, state=FSMAddThing.choosing_price, content_types=['text'])
    dp.register_message_handler(pic_chosen, state=FSMAddThing.choosing_pic, content_types=['photo'])
    dp.register_callback_query_handler(change_page, Text(startswith="page_"), state=FSMAddThing.choosing_category)
    dp.register_callback_query_handler(subchange_page, Text(startswith="subpage_"), state=FSMAddThing.choosing_subcategory)