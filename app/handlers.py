import time

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router


from tinkoff.invest import Client, RequestError
from invest_api.print_portfel import print_activ_str

from config import TOKEN_STRATEG, name_strategs
import app.keyboards as kb

import app.database.requests as rq

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from aiogram.types import FSInputFile, InputMediaPhoto

router = Router()


class Reg_token(StatesGroup):
    token = State()
    stra = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    # await message.answer(f' hello {message.from_user.username} \nyou ID: {message.from_user.id}',
    #                      reply_markup=kb.start)
    await message.answer(f'Автоследование может быть полезным как для новичков,'
                         f' так и для опытных инвесторов.Возможность получать доход с минимумом усилий.\n'
                         f' Для новичков в инвестициях следование готовой стратегии дает возможность получать доход'
                         f' без необходимости посвящать много времени изучению основ биржевой торговли.\nМинимальные затраты времени.'
                         f' Сервис автоследования полностью автоматизирован. После подключения к стратегии подписчику не придется думать,'
                         f' какие именно активы нужно покупать и когда их продавать: за всё отвечает автоследование.'
                         f' Сделки по стратегии будут автоматически повторяться на счетах подписчиков.',
        reply_markup=kb.start)



#====================main_menu==============================================================================================
@router.message(F.text == 'меню')
async def main_menu(message: Message):
    await message.answer(f'тут вы сможете управлять своими счетами и выбирать стратегии', reply_markup=kb.main)
    await message.delete(id=message.message_id)


@router.callback_query(F.data == 'mein_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f'тут вы сможете управлять своими счетами и выбирать стратегии', reply_markup=kb.main)


#===========================helper===========================================================================================
@router.message(F.text == 'как получить токен')
async def main_menu(message: Message):
    await message.delete(id=message.message_id)
    photo_paths = ['images/1.png', 'images/2.png']  # Укажите путь к вашей фотографии
    photos_with_captions = [
        ('images/1.png', 'https://www.tbank.ru/invest/settings/api/'),
        ('images/2.png', ''),
    ]

    media = [
        InputMediaPhoto(media=FSInputFile(photo_path), caption=caption)
        for photo_path, caption in photos_with_captions
    ]

    await message.answer_media_group(media=media)


#=============================info_strategs============================================================================================
@router.callback_query(F.data == 'info_strategs')
async def info_strategs(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete(id=callback.message.message_id)
    await callback.message.answer('просмотр стратегий', reply_markup= await kb.viewing_strateg())


@router.callback_query(F.data.startswith('view_'))
async def view_strategs(callback: CallbackQuery):
    await callback.answer()
    s = callback.data.split('_')[1]
    if s != 'all':
        await callback.message.delete(id=callback.message.message_id)
        await callback.message.answer_photo(photo=FSInputFile('images/'+s+'.png'),caption=f' ``` {await print_activ_str(TOKEN_STRATEG.get(s))} ```',
                                     reply_markup=kb.view_strategs_menu, parse_mode="MarkdownV2")
    else:
        s = " "
        for i in TOKEN_STRATEG.values():
            s += await print_activ_str(i) + "\n"
            await callback.message.edit_text(text=f' ``` {s} ```',
                                             reply_markup=kb.view_strategs_menu, parse_mode="MarkdownV2")


#=============================my_token===========================================================================================
@router.callback_query(F.data == 'my_token')
async def my_token(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_text('работа с токеном\счетом', reply_markup=await kb.my_token(callback.from_user.id))


@router.callback_query(F.data.startswith('insert_my_token'))
async def insert_my_token(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reg_token.token)
    await state.update_data(stra='none')
    await callback.message.edit_text('Введите ваш токен', reply_markup=kb.insert_my_token)


#================================setings_my_token===========================================================
@router.callback_query(F.data.startswith('setings_my_token_'))
async def setings_my_token(callback: CallbackQuery):
    await callback.answer()
    index = callback.data.split('_')[3]
    edit = await rq.select_user_strateg(callback.from_user.id)
    name = ""
    for i in range(len(name_strategs)):
        if name_strategs[i][0] == edit[int(index)][1]:
            name = name_strategs[i][1]
    await callback.message.edit_text(text=f'{edit[int(index)][0]}\nактивная  стратегия: { name }',
                                     reply_markup=kb.setings_my_token(index))


@router.callback_query(F.data.startswith('delete_my_token_'))
async def delete_my_token(callback: CallbackQuery):
    await callback.answer()
    index = callback.data.split('_')[3]
    cthet = await rq.select_user_strateg(callback.from_user.id)
    await rq.delete_token(cthet[int(index)][2])
    await callback.message.edit_text(f'токен/cчет успешно удален', reply_markup=kb.insert_my_token)


@router.callback_query(F.data.startswith('my_token_view_'))
async def my_token_view(callback: CallbackQuery):
    await callback.answer()
    index = callback.data.split('_')[3]
    cthet = await rq.select_user_strateg(callback.from_user.id)
    if index != "all":
        await callback.message.edit_text(text=f' ``` {await print_activ_str(cthet[int(index)][2])} ```',
                                         reply_markup=kb.insert_my_token, parse_mode="MarkdownV2")
    else:
        s = " "
        for i in range(len(cthet)):
            s += await print_activ_str(cthet[i][2]) + "\n"
            await callback.message.edit_text(text=f' ``` {s} ```',
                                             reply_markup=kb.insert_my_token, parse_mode="MarkdownV2")


@router.callback_query(F.data.startswith('update_my_token_'))
async def update_my_token_(callback: CallbackQuery):
    index = callback.data.split('_')[3]
    await callback.message.edit_text(text=f'доступные сратегии',
                                     reply_markup=await kb.update_my_token(index))


@router.callback_query(F.data.startswith('install_update_'))
async def install_update(callback: CallbackQuery):
    await callback.answer()
    s = callback.data.split('_')[2]
    index = callback.data.split('_')[3]
    if s != 'none':
        await callback.message.edit_text(text=f' ``` {await print_activ_str(TOKEN_STRATEG.get(s) ) } ```',
                                         parse_mode="MarkdownV2", reply_markup=kb.install_update(index, s))
    else:
        await callback.message.edit_text(text=f'отключение стратегии ', reply_markup=kb.install_update(index, s))


@router.callback_query(F.data.startswith('token_update_'))
async def token_update(callback: CallbackQuery):
    await callback.answer()
    index = callback.data.split('_')[2]
    s = callback.data.split('_')[3]

    data = await rq.select_user_strateg(callback.from_user.id)
    await rq.update(data[int(index)][2], s)

    await callback.message.edit_text(text=f'{data[int(index)][0]} ,cтратегия обновлена',
                                         reply_markup=kb.insert_my_token)



@router.message(Reg_token.token)
async def reg_tokens(message: Message, state: FSMContext):
    await state.update_data(token=message.text)
    data = await state.get_data()
    try:
        with Client(data["token"]) as client:
            name = client.users.get_accounts()
            if len(await rq.select_token(data["token"])) == 0:
                if name.accounts[0].access_level == 1:
                    await message.answer(f' регистрацию нового токена успешна\n'
                                         f'счет {name.accounts[0].name} подключен\n'
                                         f'уровень доступа {name.accounts[0].access_level} ',
                                         reply_markup=kb.insert_my_token)
                    await rq.insert(message.from_user.id, data['stra'], data["token"], name.accounts[0].name)
                    await state.clear()
                else:
                    await message.answer('токену не хватает уровня доступа\nВведите ваш токен повторно',
                                         reply_markup=kb.insert_my_token)
            else:
                await message.answer('токену уже существует\nВведите ваш токен повторно',
                                     reply_markup=kb.insert_my_token)
    except RequestError as e:
        await message.answer('токен не подошел\nВведите ваш токен повторно',
                                     reply_markup=kb.insert_my_token)


