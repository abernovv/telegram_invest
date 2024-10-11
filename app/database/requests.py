import bd_script
from bd_script import ASYNC_SELECT, ASYNC_INSERT,ASYNC_DELETE, ASYNC_UPDATE
from config import db_config

bd_script.db_config_local = db_config


import asyncio

#async def test():
#     data = await ASYNC_SELECT('user_data', ['name'], w_s=True, w_c='user_id', w_d=tg_id)
#     await ASYNC_UPDATE('user_data', token=token, w_s=True, w_c='type', w_d=type)
#     await ASYNC_DELETE('user_data', token='sdfsd')
#     await ASYNC_INSERT('user_data', name='shdjf', user_id='dsufh')
#     print(data)


async def insert(tg_id, type, token, name):
    await ASYNC_INSERT('user_data', name=name, token=token, type=type, user_id=str(tg_id))


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


async def select_token(token):
    data = await ASYNC_SELECT('user_data', ['user_id'], w_s=True, w_c='token', w_d=token)
    return data


async def update(token, type):
    await ASYNC_UPDATE('user_data', type=type, w_s=True, w_c='token', w_d=token)


async def delete_token(s):
    await ASYNC_DELETE('user_data', token=s)


async def main():
    await ASYNC_DELETE('user_data', user_id='500961694')

if __name__ == "__main__":
    asyncio.run(main())


#CREATE USER db_user WITH PASSWORD 'password';
#CREATE DATABASE invest;
#GRANT ALL PRIVILEGES ON DATABASE invest to db_user;
#CREATE TABLE strategs_grafs (type TEXT, price TEXT);
#CREATE TABLE user_data (id SERIAL PRIMARY KEY, user_id TEXT, token TEXT, type TEXT, name TEXT);


