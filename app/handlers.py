from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from tinkoff.invest import Client, RequestError
import os
import random
import string


from invest_api.print_portfel import print_activ_str
import app.keyboards as kb
import app.database.requests as rq



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
                         f' Сделки по стратегии будут автоматически повторяться на счетах подписчиков.\n\nКакие есть риски в автоследовании?\n'
                         f'В целом в инвестициях всегда есть риск не получить ожидаемую доходность или даже потерять часть от вложенных средств,'
                         f' если экономическая ситуация резко обострится или случится что‑то непредвиденное: гарантировать доходность на фондовом рынке невозможно.\n\n'
                         f'Дополнительный риск, связанный с автоследованием, выражается в том, что решение о покупке или продаже активов на счете инвестора принимает не он сам,'
                         f' а автор выбранной им стратегии. Если по каким‑то причинам стратегия не оправдает ожиданий, это может привести к убыткам инвесторов,'
                         f' которые на нее подписались.\n\n Кроме того, в автоследовании есть риск технического сбоя, хотя он и маловероятен.'
                         f' В случае технического сбоя вы в любой момент можете отключить автоследование, чтобы торговать на счете самостоятельно. ',
                         reply_markup=kb.start)



#====================main_menu==============================================================================================
@router.message(F.text == 'меню')
async def main_menu(message: Message):
    await message.answer(f'тут вы сможете управлять своими счетами и выбирать стратегии',
                          reply_markup = await kb.main(message.chat.id))
    await message.delete(id=message.message_id)


@router.callback_query(F.data == 'mein_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f'тут вы сможете управлять своими счетами и выбирать стратегии',
                                     reply_markup=await kb.main(callback.message.chat.id))


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
@router.callback_query(F.data.startswith('info_strategs_'))
async def info_strategs(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    name = callback.data.split('_')[2]
    await callback.answer()
    await callback.message.delete(id=callback.message.message_id)
    await callback.message.answer('просмотр стратегий', reply_markup= await kb.viewing_strateg(name))


@router.callback_query(F.data.startswith('view_'))
async def view_strategs(callback: CallbackQuery):
    name = callback.data.split('_')[2]
    TOKEN_STRATEG_V2 = await rq.select_token_strategs(name)

    await callback.answer()
    s = callback.data.split('_')[1]
    if s != 'all':
        await callback.message.delete(id=callback.message.message_id)
        if os.path.exists('images/'+s+'.png') == 1:
            await callback.message.answer_photo(photo=FSInputFile('images/'+s+'.png'),caption=f' ``` {await print_activ_str(TOKEN_STRATEG_V2.get(s)[0])} ```',
                                     reply_markup=await kb.view_strategs_menu(name,s), parse_mode="MarkdownV2")
        else:
            await callback.message.answer(text=f' ``` {await print_activ_str(TOKEN_STRATEG_V2.get(s)[0])}  ```',
                                             reply_markup=await kb.view_strategs_menu(name,s), parse_mode="MarkdownV2")
    else:
        st = " "
        for i in TOKEN_STRATEG_V2.keys():
            if i != 'none':
                st += await print_activ_str(TOKEN_STRATEG_V2.get(i)[0]) + "\n"
                await callback.message.edit_text(text=f' ``` {st} ```',
                                                 reply_markup=await kb.view_strategs_menu(name,'admin1'), parse_mode="MarkdownV2")

#===========================add_user_strategs_==================================================================================

@router.callback_query(F.data.startswith('add_user_strategs_'))
async def insert_my_token(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reg_token.token)
    await state.update_data(stra='user_strategs')
    await callback.message.edit_text('Введите ваш токен', reply_markup= await kb.view_strategs_menu(callback.message.chat.id,'admin1'))


@router.callback_query(F.data.startswith('delete_strategs_'))
async def delete_strategs(callback: CallbackQuery):
    type = callback.data.split('_')[2]
    await callback.message.delete(id=callback.message.message_id)#============================================================================
    await rq.delet_strategs(type)
    await callback.message.answer('стратегия удалена',
                                  reply_markup=await kb.view_strategs_menu(callback.message.chat.id, 'admin1'))


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
    await state.update_data(stra='user_token')
    await callback.message.edit_text('Введите ваш токен', reply_markup=kb.insert_my_token )


#================================setings_my_token===========================================================
@router.callback_query(F.data.startswith('setings_my_token_'))
async def setings_my_token(callback: CallbackQuery):
    TOKEN_STRATEG_V2 = await rq.select_token_strategs('admin')
    await callback.answer()
    index = callback.data.split('_')[3]
    edit = await rq.select_user_strateg(callback.from_user.id)
    name = ""

    for i in TOKEN_STRATEG_V2.keys():
        if i == edit[int(index)][1]:
            name = TOKEN_STRATEG_V2[i][1]

    await callback.message.edit_text(text=f'{edit[int(index)][0]}\nактивная  стратегия: { name }',
                                     reply_markup=await kb.setings_my_token(index,callback.message.chat.id))


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


@router.callback_query(F.data.startswith('update_my_token_'))#========================================================================================================
async def update_my_token_(callback: CallbackQuery):
    index = callback.data.split('_')[3]
    chat = callback.data.split('_')[4]
    await callback.message.edit_text(text=f'доступные сратегии',
                                     reply_markup=await kb.update_my_token(index,chat))


@router.callback_query(F.data.startswith('install_update_'))
async def install_update(callback: CallbackQuery):
    chatt = callback.data.split('_')[4]
    TOKEN_STRATEG_V2 = await rq.select_token_strategs(chatt)
    await callback.answer()
    s = callback.data.split('_')[2]
    index = callback.data.split('_')[3]
    if s != 'none':
        await callback.message.edit_text(text=f' ``` {await print_activ_str(TOKEN_STRATEG_V2.get(s)[0] ) } ```',
                                         parse_mode="MarkdownV2", reply_markup=await kb.install_update(index, s))
    else:
        await callback.message.edit_text(text=f'отключение стратегии ', reply_markup=await kb.install_update(index, s))


@router.callback_query(F.data.startswith('token_update_'))
async def token_update(callback: CallbackQuery):
    await callback.answer()
    index = callback.data.split('_')[2]
    s = callback.data.split('_')[3]

    data = await rq.select_user_strateg(callback.from_user.id)
    await rq.update(data[int(index)][2], s)

    await callback.message.edit_text(text=f'{data[int(index)][0]} ,cтратегия обновлена',
                                         reply_markup=kb.insert_my_token)


def generate_random_word(length=5):
    # Используем буквы и цифры
    characters = string.ascii_letters + string.digits
    random_word = ''.join(random.choice(characters) for _ in range(length))
    return random_word




@router.message(Reg_token.token)
async def reg_tokens(message: Message, state: FSMContext):
    await state.update_data(token=message.text)
    data = await state.get_data()

    try:
        with (Client(data["token"]) as client):
            name = client.users.get_accounts()
            id_account = name.accounts[0].id
            if( (len(await rq.select_id_account(id_account) ) == 0 and data['stra'] == 'user_token') or
                (len(await rq.select_id_strategs(id_account) ) == 0 and data['stra'] == 'user_strategs')):
                if name.accounts[0].access_level == 1:
                    if(data['stra'] == 'user_token'):
                        await message.answer(f' регистрацию нового токена успешна\n'
                                             f'счет {name.accounts[0].name} подключен\n'
                                             f'уровень доступа {name.accounts[0].access_level} ',
                                             reply_markup=kb.insert_my_token )
                        await rq.insert_user(message.from_user.id, 'none', data["token"], name.accounts[0].name, id_account)

                    elif(data['stra'] == 'user_strategs'):
                        await message.answer(f' регистрацию новой стратегии успешна\n'
                                             f'счет {name.accounts[0].name} подключен\n'
                                             f'уровень доступа {name.accounts[0].access_level} ',
                                             reply_markup=await kb.view_strategs_menu(message.chat.id,'admin1'))


                        type_strategs = str(message.chat.id) + '-' + str(id_account)

                        await rq.insert_strategs(message.chat.id, type_strategs, data["token"], name.accounts[0].name, id_account)

                    await state.clear()
                else:
                    await message.answer('токену не хватает уровня доступа\nВведите ваш токен повторно',
                                         reply_markup= kb.insert_my_token if data['stra'] == 'user_token'
                                         else await kb.view_strategs_menu(message.chat.id,'admin1') )
            else:
                await message.answer('токену уже существует\nВведите ваш токен повторно',
                                     reply_markup=kb.insert_my_token if data['stra'] == 'user_token'
                                     else await kb.view_strategs_menu(message.chat.id,'admin1') )
    except RequestError as e:
        await message.answer('токен не подошел\nВведите ваш токен повторно',
                                     reply_markup=kb.insert_my_token if data['stra'] == 'user_token'
                                     else await kb.view_strategs_menu(message.chat.id,'admin1') )

