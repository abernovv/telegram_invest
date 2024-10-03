from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as rq

from config import name_strategs


start = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='меню')],
    [KeyboardButton(text='написать в поддержку')],
   ],
    resize_keyboard=True)

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='информация о доступных стратегиях', callback_data='info_strategs')],
    [InlineKeyboardButton(text='мои токены/счета', callback_data='my_token')]
])


async def viewing_strateg():
    keyboard = InlineKeyboardBuilder()
    for i in range(len(name_strategs)-1):
        keyboard.add(InlineKeyboardButton(text=name_strategs[i][1], callback_data=f'view_{name_strategs[i][0]}'))
    keyboard.add(InlineKeyboardButton(text='просмотреть все стратегии', callback_data=f'view_all'))
    keyboard.add(InlineKeyboardButton(text='назад', callback_data=f'mein_menu'))
    return keyboard.adjust(1).as_markup()


view_strategs_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='назад', callback_data='info_strategs')]
])

insert_my_token = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='назад', callback_data='my_token')]
])

async def my_token(tg_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.select_user_strateg(tg_id)
    for i in range(len(data)):
        keyboard.add(InlineKeyboardButton(text=data[i][0], callback_data=f'setings_my_token_{i}'))
    keyboard.add(InlineKeyboardButton(text='просмотреть все cчета', callback_data=f'my_token_view_all'))
    keyboard.add(InlineKeyboardButton(text='добавить токен/cчет', callback_data=f'insert_my_token'))
    keyboard.add(InlineKeyboardButton(text='назад', callback_data=f'mein_menu'))
    return keyboard.adjust(1).as_markup()


def setings_my_token(index):
    t = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='просмотреть состояние токена/счета', callback_data=f'my_token_view_{index}')],
    [InlineKeyboardButton(text='начать следовать cтратегии / обновить стратегию', callback_data=f'update_my_token_{index}')],
    [InlineKeyboardButton(text='удалить токен/счет', callback_data=f'delete_my_token_{index}')],
    [InlineKeyboardButton(text='назад', callback_data='my_token')]
    ])
    return t


async def update_my_token(index):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(name_strategs)):
        keyboard.add(InlineKeyboardButton(text=name_strategs[i][1], callback_data=f'install_update_{name_strategs[i][0]}_{index}'))
    keyboard.add(InlineKeyboardButton(text='назад', callback_data=f'setings_my_token_{index}'))
    return keyboard.adjust(1).as_markup()


def install_update(index, s):
    t = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='подключить', callback_data=f'token_update_{index}_{s}')],
    [InlineKeyboardButton(text='назад', callback_data=f'setings_my_token_{index}')]
    ])
    return t