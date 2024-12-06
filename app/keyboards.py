from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as rq


start = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='меню')],
    [KeyboardButton(text='как получить токен')],
   ],
    resize_keyboard=True)

async def main(id):
    Keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='авторские стратегии', callback_data='info_strategs_admin')],
        [InlineKeyboardButton(text='мои стратегии', callback_data=f'info_strategs_{id}')],
        [InlineKeyboardButton(text='мои токены/счета', callback_data='my_token')]
    ])
    return Keyboard


async def viewing_strateg(name):
    TOKEN_STRATEG_V2 = await rq.select_token_strategs(name)
    keyboard = InlineKeyboardBuilder()
    for i in TOKEN_STRATEG_V2.keys():
        if i != 'none':
            keyboard.add(InlineKeyboardButton(text=TOKEN_STRATEG_V2[i][1], callback_data=f'view_{i}_{name}'))
    if name != 'admin':
        keyboard.add(InlineKeyboardButton(text='добавить стратегию', callback_data=f'add_user_strategs_{name}'))
    keyboard.add(InlineKeyboardButton(text='просмотреть все стратегии', callback_data=f'view_all_{name}'))
    keyboard.add(InlineKeyboardButton(text='назад', callback_data=f'mein_menu'))
    return keyboard.adjust(1).as_markup()


async def view_strategs_menu(id,type):
    keyboard = InlineKeyboardBuilder()
    if id != 'admin' and type != 'admin1':
        keyboard.add(InlineKeyboardButton(text='удалить стратегию', callback_data=f'delete_strategs_{type}'))
    keyboard.add(InlineKeyboardButton(text='назад', callback_data=f'info_strategs_{id}'))
    return keyboard.adjust(1).as_markup()

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


async def setings_my_token(index,chat_id):
    t = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='просмотреть состояние токена/счета', callback_data=f'my_token_view_{index}')],
    [InlineKeyboardButton(text='обновить на авторскую стратегию', callback_data=f'update_my_token_{index}_admin')],
    [InlineKeyboardButton(text='обновить на свою стратегию', callback_data=f'update_my_token_{index}_{chat_id}')],
    [InlineKeyboardButton(text='отключить следование', callback_data=f'token_update_{index}_none')],
    [InlineKeyboardButton(text='удалить токен/счет', callback_data=f'delete_my_token_{index}')],
    [InlineKeyboardButton(text='назад', callback_data='my_token')]
    ])
    return t


async def update_my_token(index,chat):
    TOKEN_STRATEG_V2 = await rq.select_token_strategs(chat)
    keyboard = InlineKeyboardBuilder()
    for i in TOKEN_STRATEG_V2.keys():
        keyboard.add(InlineKeyboardButton(text=TOKEN_STRATEG_V2[i][1], callback_data=f'install_update_{i}_{index}_{chat}'))
    keyboard.add(InlineKeyboardButton(text='назад', callback_data=f'setings_my_token_{index}'))
    return keyboard.adjust(1).as_markup()


async def install_update(index, s):
    t = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='подключить', callback_data=f'token_update_{index}_{s}')],
    [InlineKeyboardButton(text='назад', callback_data=f'setings_my_token_{index}')]
    ])
    return t
