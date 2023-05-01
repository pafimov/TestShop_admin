import asyncio
import os
from users_api.management.commands._create_bot import dp, bot
from users_api.management.commands._constants import needed_channel, needed_channel_id
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from asgiref.sync import sync_to_async
from users_api.models import UserFree, Thing, CartObject
from users_api.management.commands._keyboards import get_categories, get_subcategories, get_thing, get_cartobject
from aiogram.dispatcher.filters import Text
import pandas as pd

class FSMregistration(StatesGroup):
    waiting_name = State()

class FSMChooseThings(StatesGroup):
    choosing_category = State()
    choosing_subcategory = State()


async def check_if_subscribed(user_id):
    user_channel_status = await bot.get_chat_member(chat_id=needed_channel_id, user_id=user_id)
    # print(user_channel_status)
    if user_channel_status["status"] != 'left':
        return 1
    else:
        return 0

#start
async def start_command(message : types.Message, state : FSMContext):
    user_id = message.from_id
    if not await check_if_subscribed(user_id):
        await message.reply("Вы не подписаны на канал " + needed_channel + " !")
        return
    try:
        user = await UserFree.objects.aget(telegram_id=user_id)
        await message.reply("Вы уже зарегистрированы!")
        return 
    except Exception:   
        await message.reply("Здравствуйте! Введите ваше имя.")
        await state.set_state(FSMregistration.waiting_name.state)

#general info about commands
async def help_command(message : types.Message, state : FSMContext):
    message.reply("Это бот-магазин.\n/goods - открыть каталог и посмотреть интересующие товары.\n/cart - просмотреть корзину.")

async def name_chosen(message : types.Message, state: FSMContext):
    name = message.text
    user_id = message.from_id
    new_user = UserFree(telegram_id=user_id, telegram_username=message.from_user.username, sum_bought=0, name=name)
    try:
        await new_user.asave()
        await message.answer("Вы успешно зарегистрированы! Отправьте команду /help для получения справки о командах.")
        await state.finish()
    except Exception:
        await message.answer("Введите корректное имя!")

#categories pagination
async def change_page(callback : types.CallbackQuery):
    message = callback.message
    page = int(callback.data[callback.data.index('_')+1:])
    kb = await get_categories(page)
    await message.edit_reply_markup(reply_markup=kb)
    await callback.answer()

#subcategories pagination
async def subchange_page(callback : types.CallbackQuery, state: FSMContext):
    message = callback.message
    page = int(callback.data[callback.data.index('_')+1:])
    kb = await get_subcategories((await state.get_data())['category'], page)
    await message.edit_reply_markup(reply_markup=kb)
    await callback.answer()

async def choose_things(message: types.Message, state : FSMContext):
    kb = await get_categories(0)
    await message.answer("Выберите категорию:", reply_markup=kb)
    await state.set_state(FSMChooseThings.choosing_category)

async def category_chosen(callback: types.CallbackQuery, state : FSMContext):
    message = callback.message
    category = int(callback.data[callback.data.index('_')+1:])
    await state.update_data(category=category)
    await message.delete()
    await state.set_state(FSMChooseThings.choosing_subcategory)
    kb = await get_subcategories((await state.get_data())['category'], 0)
    await message.answer('Выберите подкатегорию:', reply_markup=kb)
    await callback.answer()

async def subcategory_chosen(callback : types.CallbackQuery, state : FSMContext):
    message = callback.message
    subcategory = int(callback.data[callback.data.index('_')+1:])
    await state.update_data(subcategory=subcategory)
    await message.delete()
    data = await state.get_data()
    goods = await sync_to_async(Thing.objects.filter)(category=data['category'], subcategory=data['subcategory'])
    await state.finish()
    tasks = []
    goods = await sync_to_async(list)(goods) 
    for thing in goods:
        details = await get_thing(thing)
        tasks.append(asyncio.create_task(message.answer_photo(photo=thing.pic_id, caption=details[0], reply_markup=details[1])))
    await asyncio.gather(*tasks)
    await callback.answer()


class FSMAddToCart(StatesGroup):
    choosing_count = State()


async def add_to_cart(callback : types.CallbackQuery, state : FSMContext):
    message = callback.message
    thing_id = int(callback.data[callback.data.index('_')+1:])
    await state.update_data(thing_id=thing_id)
    try:
        user= await UserFree.objects.aget(telegram_id=callback.from_user.id)
        thing= await Thing.objects.aget(pk=thing_id)
    except Exception:
        await message.answer("Произошла внутренняя ошибка. Выберите другой товар.")
        await callback.answer()
        return
    try:
        cart_object = await CartObject.objects.aget(user=user, thing=thing)
        await state.set_state(FSMAddToCart.choosing_count)
        await message.answer("Этот товар уже есть у Вас в корзине.\nЕсли вы хотите изменить количество, введите новое количество.\nЕсли вы хотите отменить изменение количества, то отправьте команду /cancel ")
    except Exception:
        await message.answer("Введите желаемое количество:")
        await state.set_state(FSMAddToCart.choosing_count)
    await callback.answer()

async def count_chosen(message : types.Message, state : FSMContext):
    count = message.text
    try:
        count = int(count)
    except Exception:
        await message.reply("Введите корректное число!")
        return
    if count <= 0:
        await message.reply("Количество должно быть неотрицательным!")
        return
    data = await state.get_data()
    try:
        user = await UserFree.objects.aget(telegram_id=message.from_id)
        thing = await Thing.objects.aget(pk=data['thing_id'])
    except Exception:
        await message.reply("Произошла внутренняя ошибка. Выберите другой товар, либо другое количество.")
        await state.finish()
        return
    await state.finish()
    try:
        old_cart =await CartObject.objects.aget(user=user, thing=thing)
        await old_cart.adelete()
    except Exception:
        pass

    new_cart = CartObject(count=count, thing=thing, user=user)
    await new_cart.asave()
    await message.answer("Товар добавлен в корзину.\n\n Чтобы просмотреть корзину, отправьте команду /cart ")

async def view_cart(message : types.Message):
    try:
        user = await UserFree.objects.aget(telegram_id=message.from_id)
    except Exception:
        await message.answer("Произошла системная ошибка.")
        return
    
    #get cart object for the user
    cart_objects = await sync_to_async(CartObject.objects.filter)(user=user)
    cart_objects = await sync_to_async(list)(cart_objects)
    
    #displaying cart
    tasks = []
    for cart_object in cart_objects:
        details = await get_cartobject(cart_object)
        tasks.append(asyncio.create_task(message.answer_photo(cart_object.thing.pic_id, caption=details[0], reply_markup=details[1])))
    if len(tasks) == 0:
        await message.answer("Корзина пуста!")
        return
    await asyncio.gather(*tasks)
    await message.answer("Отправьте команду /order для оформления заказа.")

async def del_from_cart(callback : types.CallbackQuery, state : FSMContext):
    message = callback.message
    cart_object_id = int(callback.data[callback.data.index('_')+1:])
    #try search for object to delete
    try:
        cart_object = await CartObject.objects.aget(pk=cart_object_id)
    except Exception:
        await message.reply("Произошла внутренняя ошибка.")
        await callback.answer()
        return
    await cart_object.adelete()
    await message.delete()
    await callback.answer()

async def cancel(message : types.Message, state : FSMContext):
    cur_state = await state.get_state()
    if cur_state != None and cur_state != FSMregistration.waiting_name:
        await state.finish()
        await message.reply("Действие отменено.")
    else:
        await message.reply("Вы сейчас не в действии.")

async def order(message : types.Message, state : FSMContext):
    try:
        user = await UserFree.objects.aget(telegram_id=message.from_id)
    except Exception:
        await message.answer("Произошла системная ошибка.")
        return
    
    #get cart object for the user
    cart_objects = await sync_to_async(CartObject.objects.filter)(user=user)
    cart_objects = await sync_to_async(list)(cart_objects)
    
    #calculate total sum
    payload = ''
    sum = 0
    for cart_object in cart_objects:
        payload += str(cart_object.pk) + ","
        thing = await cart_object.get_thing()
        sum += thing.price * cart_object.count
    payload = payload[:-1]
    #send a payment to user
    print("XD")
    try:
        await bot.send_invoice(chat_id= message.from_id, title='Покупка в TG магазине.', provider_token='381764678:TEST:55883', currency='rub',
                      prices=[types.LabeledPrice(label="Товары в корзине", amount=sum*100)], need_phone_number=True, description='Shop in TG payment',
                      payload=payload, max_tip_amount=5000, suggested_tip_amounts=[1000, 2000, 3000])
    except Exception:
        await message.answer("Сумма слишком мала для оформления заказа!")

async def pre_checkout(pre_checkout_query : types.PreCheckoutQuery):
    
    #check if payment is for current cart of user
    user =await UserFree.objects.aget(telegram_id=pre_checkout_query.from_user.id)
    payload = pre_checkout_query.invoice_payload.split(',')
    cart = await sync_to_async(CartObject.objects.filter)(user=user)
    cart = await sync_to_async(list)(cart)
    ok = True
    for cart_object in cart:
        cur_id = str(cart_object.pk)
        if not cur_id in payload:
            ok = False
            break
    if len(cart) != len(payload):
        ok = False
    if ok == False:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message="Выполните перерассчёт корзины.")
    else:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def payment_successful(message : types.Message):
    user =await UserFree.objects.aget(telegram_id=message.from_id)
    await message.answer("Оплата прошла успешно!\nСпасибо за Ваш заказ!")
    
    #get payment details
    data= message.successful_payment.to_python()
    number = data['order_info']['phone_number']

    #load to excel file
    new_num = len(os.listdir('./orders'))+1
    personal_info = pd.DataFrame({'Имя' : [user.name], 'Номер телефона' : [number], 'Telegram' : [user.telegram_username], 'Telegram ID' : [user.telegram_id]})
    order_info = {'Артикул' : [], 'Название' : [], 'Кол-во' : []}
    cart_q = await sync_to_async(CartObject.objects.filter)(user=user)
    cart = await sync_to_async(list)(cart_q)
    for cart_object in cart:
        thing = await cart_object.get_thing()
        order_info['Артикул'].append(thing.pk)
        order_info['Название'].append(thing.name)
        order_info['Кол-во'].append(cart_object.count)
    order_info = pd.DataFrame(order_info)
    sheets = {'Заказчик' : personal_info, 'Заказ' : order_info}
    writer = pd.ExcelWriter('./orders/' + str(new_num) + ".xlsx", engine='xlsxwriter')
    for sheet_name in sheets.keys():
        sheets[sheet_name].to_excel(writer, sheet_name=sheet_name)
    writer.close()
    
    #clear cart
    await cart_q.adelete()
    
    #increase sum_bought of user
    user.sum_bought += data['total_amount']//100
    await user.asave()

def register_handles():
    dp.register_message_handler(cancel, commands=['cancel'], state="*")
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(name_chosen, content_types=['text'], state=FSMregistration.waiting_name)
    dp.register_message_handler(choose_things, commands=['goods'])
    dp.register_callback_query_handler(change_page, Text(startswith="page_"), state=FSMChooseThings.choosing_category)
    dp.register_callback_query_handler(subchange_page, Text(startswith="subpage_"), state=FSMChooseThings.choosing_subcategory)
    dp.register_callback_query_handler(category_chosen, Text(startswith="chosen_"), state=FSMChooseThings.choosing_category)
    dp.register_callback_query_handler(subcategory_chosen, Text(startswith="subchosen_"), state=FSMChooseThings.choosing_subcategory)
    dp.register_callback_query_handler(add_to_cart, Text(startswith="addtocart_"))
    dp.register_callback_query_handler(del_from_cart, Text(startswith="deletefromcart_"))
    dp.register_message_handler(count_chosen, state=FSMAddToCart.choosing_count, content_types=['text'])
    dp.register_message_handler(view_cart, commands=['cart'])
    dp.register_message_handler(order, commands=['order'])
    dp.register_pre_checkout_query_handler(pre_checkout)
    dp.register_message_handler(payment_successful, content_types=['successful_payment'])
    
