from users_api.management.commands._constants import all_categories, categories, page_size
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from users_api.models import Thing, CartObject

async def get_categories(page_num):
    n = len(categories)
    pages_count = (n+page_size-1)//page_size
    first_category = page_num*page_size
    cur_category = first_category
    kb = InlineKeyboardMarkup(row_width=1)
    while cur_category < n and cur_category < first_category + page_size:
        callback_data = 'chosen_' + str(cur_category)
        kb.add(InlineKeyboardButton(categories[cur_category], callback_data=callback_data))
        cur_category+=1
    if page_num > 0:
        callback_data = "page_" + str(page_num-1)
        kb.add(InlineKeyboardButton("Прошлая старинца", callback_data=callback_data))
    if page_num < pages_count-1:
        callback_data = "page_" + str(page_num+1)
        kb.add(InlineKeyboardButton("Следующая старинца", callback_data=callback_data))
    return kb

async def get_subcategories(category_num, page_num):
    category = categories[category_num]
    n = len(all_categories[category])
    pages_count = (n+page_size-1)//page_size
    first_category = page_num*page_size
    cur_category = first_category
    kb = InlineKeyboardMarkup(row_width=1)
    while cur_category < n and cur_category < first_category + page_size:
        callback_data = 'subchosen_' + str(cur_category)
        kb.add(InlineKeyboardButton(all_categories[category][cur_category], callback_data=callback_data))
        cur_category+=1
    if page_num > 0:
        callback_data = "subpage_" + str(page_num-1)
        kb.add(InlineKeyboardButton("Прошлая старинца", callback_data=callback_data))
    if page_num < pages_count-1:
        callback_data = "subpage_" + str(page_num+1)
        kb.add(InlineKeyboardButton("Следующая старинца", callback_data=callback_data))
    return kb

async def get_thing(thing : Thing):
    kb = InlineKeyboardMarkup(row_width=1)
    callback_data = "addtocart_" + str(thing.pk)
    kb.add(InlineKeyboardButton('Добавить в корзину', callback_data=callback_data))
    text = thing.name + "\n\n" + thing.description + "\n\n" + str(thing.price) + " рублей."
    return (text, kb)

async def get_cartobject(cart_object : CartObject):
    kb = InlineKeyboardMarkup(row_width=1)
    callback_data = "deletefromcart_" + str(cart_object.pk)
    thing = await cart_object.get_thing()
    kb.add(InlineKeyboardButton('Удалить из корзины', callback_data=callback_data))
    text = thing.name + "\n\nКоличество: " + str(cart_object.count) + ".\n\n"
    sum = cart_object.thing.price*cart_object.count
    text += str(thing.price) + " * " + str(cart_object.count) + " = " + str(sum) + " рублей."
    return (text, kb)
