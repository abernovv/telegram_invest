import asyncio
import bd_script
from bd_script import ASYNC_SELECT, ASYNC_INSERT, ASYNC_DELETE, ASYNC_UPDATE
from config import db_config

bd_script.db_config_local = db_config


#========================================user_data=================================================================
async def insert_user(tg_id, type, token, name,id_account):
    await ASYNC_INSERT('user_data', name=name, token=token, type=type,id_account=id_account , user_id=str(tg_id))


async def select_user_strateg(tg_id):
    return await ASYNC_SELECT('user_data', ['name', 'type', 'token'], w_s=True, w_c='user_id', w_d=str(tg_id))

async def select_strateg(strateg):
    return await ASYNC_SELECT('user_data', ['user_id', 'token'], w_s=True, w_c='type', w_d=strateg)


async def select_id_account(id_account): #находим по уникальному индитефикатору совпадение в бд что бы пользователь не мог добавить 2 одинаковых счета
    return await ASYNC_SELECT('user_data', ['id_account'], w_s=True, w_c='id_account', w_d=str(id_account))


async def update(token, type): # обновить стратегию которой будет следовать пользователь
    await ASYNC_UPDATE('user_data', type=type, w_s=True, w_c='token', w_d=token)


async def delete_token(s): # удаление токена пользователя
    await ASYNC_DELETE('user_data', token=s)


#========================================strategs=================================================================
async def insert_strategs(tg_id, type, token, name,id_account):
    await ASYNC_INSERT('strategs', name=name, token=token, type=type, id_account=id_account , user_id=str(tg_id))


async def select_id_strategs(id_account): #находим по уникальному индитефикатору совпадение в бд что бы пользователь не мог добавить 2 одинаковых счета
    return await ASYNC_SELECT('strategs', ['id_account'], w_s=True, w_c='id_account', w_d=str(id_account))


async def select_type_strateg(type): #находим по уникальному индитефикатору совпадение в бд что бы пользователь не мог добавить 2 одинаковых счета
    return await ASYNC_SELECT('strategs', ['id_account'], w_s=True, w_c='type', w_d=type)


async def select_token_strategs(tg_id): #вернет список стратегий персональных \ авторских \ всех
    arr = []
    if tg_id != 'all':
        arr = await ASYNC_SELECT('strategs', ['type', 'token', 'name'], w_s=True, w_c='user_id', w_d=str(tg_id))
    else:
        arr = await ASYNC_SELECT('strategs', ['type', 'token', 'name'])

    return {arr[i][0]: [arr[i][1], arr[i][2]] for i in range(len(arr))}


async def delet_strategs(type):
    user = await select_strateg(type)
    for i in user:
        await update(i[1], 'none')
    await ASYNC_DELETE('strategs',type=type)


#========================================strategs_grafs=================================================================
async def insert_graf(type, price): # каждый день после закрытия биржи добавляется стоимость портфеля
    await ASYNC_INSERT('strategs_grafs', type=type, price=str(price))


async def select_graf(type): # вернет все изменения цен для создания графика
    return await ASYNC_SELECT('strategs_grafs', ['price'], w_s=True, w_c='type', w_d=type)


async def main():
    user = await select_strateg('teni2')

    for i in user:
        await update(i[1],'none')


if __name__ == "__main__":
    asyncio.run(main())

#CREATE USER db_user WITH PASSWORD 'password';
#CREATE DATABASE invest;
#GRANT ALL PRIVILEGES ON DATABASE invest to db_user; версии до 15

#CREATE TABLE strategs_grafs (id SERIAL PRIMARY KEY,type TEXT, price TEXT);

#CREATE TABLE user_data (id SERIAL PRIMARY KEY, user_id TEXT,id_account TEXT, token TEXT, type TEXT, name TEXT);

#CREATE TABLE strategs (id SERIAL PRIMARY KEY, user_id TEXT,id_account TEXT, type TEXT, token TEXT, name TEXT); # добавить стартовую стоимость портфеля ? \ менять процент каждую ночь ? \ добавит возможность сортировки по прибыли