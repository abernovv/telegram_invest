import asyncio
import bd_script
from bd_script import ASYNC_SELECT, ASYNC_INSERT, ASYNC_DELETE, ASYNC_UPDATE
from config import db_config

bd_script.db_config_local = db_config


async def insert_user(tg_id, type, token, name,id_account):
    await ASYNC_INSERT('user_data', name=name, token=token, type=type,id_account=id_account , user_id=str(tg_id))


#CREATE TABLE strategs (id SERIAL PRIMARY KEY, user_id TEXT,id_account TEXT, type TEXT, token TEXT, name TEXT);
async def insert_strategs(tg_id, type, token, name,id_account):
    await ASYNC_INSERT('strategs', name=name, token=token, type=type, id_account=id_account , user_id=str(tg_id))



async def insert_graf(type, price):
    await ASYNC_INSERT('strategs_grafs', type=type, price=str(price))


async def select_graf(type):
    data = await ASYNC_SELECT('strategs_grafs', ['price'], w_s=True, w_c='type', w_d=type)
    return data


async def select_user_strateg(tg_id):
    data = await ASYNC_SELECT('user_data', ['name', 'type', 'token'], w_s=True, w_c='user_id', w_d=str(tg_id))
    return data


async def select_strateg(strateg):
    data = await ASYNC_SELECT('user_data', ['user_id', 'token'], w_s=True, w_c='type', w_d=strateg)
    return data


async def select_id_account(id_account):
    data = await ASYNC_SELECT('user_data', ['id_account'], w_s=True, w_c='id_account', w_d=str(id_account))
    return data

async def select_id_strategs(id_account):
    data = await ASYNC_SELECT('strategs', ['id_account'], w_s=True, w_c='id_account', w_d=str(id_account))
    return data



async def update(token, type):
    await ASYNC_UPDATE('user_data', type=type, w_s=True, w_c='token', w_d=token)


async def delete_token(s):
    await ASYNC_DELETE('user_data', token=s)


async def select_token_strategs(tg_id):
    arr = []
    if tg_id != 'all':
        arr = await ASYNC_SELECT('strategs', ['type', 'token', 'name'], w_s=True, w_c='user_id', w_d=str(tg_id))
    else:
        arr = await ASYNC_SELECT('strategs', ['type', 'token', 'name'])

    TOKEN_STRATEG_V2 = {arr[i][0]: [arr[i][1], arr[i][2]] for i in range(len(arr))}
    return TOKEN_STRATEG_V2

# async def main():
#     print( await ASYNC_SELECT('strategs', ['type', 'token', 'name'] ) )
#
# if __name__ == "__main__":
#     asyncio.run(main())

#CREATE USER db_user WITH PASSWORD 'password';
#CREATE DATABASE invest;
#GRANT ALL PRIVILEGES ON DATABASE invest to db_user; версии до 15

#CREATE TABLE strategs_grafs (id SERIAL PRIMARY KEY,type TEXT, price TEXT);

#CREATE TABLE user_data (id SERIAL PRIMARY KEY, user_id TEXT,id_account TEXT, token TEXT, type TEXT, name TEXT);

#CREATE TABLE strategs (id SERIAL PRIMARY KEY, user_id TEXT,id_account TEXT, type TEXT, token TEXT, name TEXT);