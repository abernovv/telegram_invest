import asyncpg, traceback, json, datetime, nest_asyncio, asyncio, gnupg
nest_asyncio.apply()

conn            = ''
db_config_local = {}

MAIL = None
PASSPHRASE = None
PUBLIC_KEY = None
PRIVATE_KEY = None

def encrypt_message(message, recipient, open_key):
    try:
        gpg = gnupg.GPG()
        gpg.encoding = 'utf-8'
        import_result = gpg.import_keys(open_key)
        encrypted_data = gpg.encrypt(message, recipient)
        return str(encrypted_data)
    except:
        print(traceback.format_exc(), '\nDATA: {0}\n\n'.format([message]), 'encrypt_message\n\n')
        return message

def decrypt_message(encrypted_message, private_key, passphrase):
    try:
        gpg = gnupg.GPG()
        gpg.import_keys(private_key)
        decrypted_data = gpg.decrypt(encrypted_message, passphrase=passphrase)
        return str(decrypted_data)

    except:
        print(traceback.format_exc(), '\nDATA: {0}\n\n'.format([encrypted_message]), 'decrypt_message\n\n')
        return encrypted_message

async def async_connection_db(db_host, user_name, user_password, db_name):
    connection_db = None
    try:
        connection_db = await asyncpg.connect(
            host=db_host,
            user=user_name,
            password=user_password,
            database=db_name
        )

    except Exception: print(traceback.format_exc(), '\nDATA: {0}\n\n'.format([db_host, user_name, user_password, db_name]), 'connection_db\n\n')
    return connection_db

# UPDATE-----------------------------------------------------------------------

async def ASYNC_UPDATE(table: str, **kwargs):
    """

    Parameters
    ----------
    table : Table name BD.
    **kwargs : Set w_s - 'where_status' True/False,
        w_c - 'where_column' always if True status,
        w_d - 'where_data' always if True status,
        add - addition to the request,
        '%column' = '%data',
        name_column, data_column = '%key', '%data',
        pgp_d = ['%column'].

    Returns
    -------
    None.

    """
    try:
        conn = await async_connection_db(db_host=db_config_local["psql"]["host"], user_name=db_config_local["psql"]["user"],
                                         user_password=db_config_local["psql"]["pass"],
                                         db_name=db_config_local["psql"]["database"])
        await update(table, conn, kwargs)

    except Exception:
        print("ASYNC_UPDATE", traceback.format_exc())
    finally:
        await conn.close()

async def update(table, conn, kwargs):
    column_data = ['name_column', 'data_column', 'add', 'w_s', 'w_c', 'w_d', 'int', 'pgp_d']
    if kwargs.get('pgp_d') != None and type(kwargs.get('pgp_d')) == list and (MAIL != None and PUBLIC_KEY != None):
        kwargs.update({column: encrypt_message(str(kwargs.get(column)), MAIL, PUBLIC_KEY) for column in kwargs.get('pgp_d')})
    name_column, data_column, join_data = kwargs.get('name_column'), kwargs.get('data_column'), [
        f'''{set_name}={set_data}''' if kwargs.get('int') else f'''{set_name}="{set_data}"''' for set_name, set_data in kwargs.items() if
        set_name not in column_data]
    if kwargs.get('j_s'):
        if kwargs.get('w_s'):
            await conn.execute(
                f"UPDATE {table} SET {kwargs.get('j_c')} = %s WHERE {kwargs.pop('w_c')}='{kwargs.pop('w_d')}'",
                (json.dumps(kwargs.get('j_d')),))
        else:
            await conn.execute(f"UPDATE {table} SET {kwargs.get('j_c')} = %s ", (json.dumps(kwargs.get('j_d')),))
    else:
        if kwargs.get('w_s'):
            await conn.execute(
                f"""UPDATE {table} SET {', '.join([f'''{set_name}=${i + 1}''' for i, (set_name, set_data) in enumerate(kwargs.items()) if set_name not in column_data])}{(", " if len(join_data) != 0 else '') + f"{name_column}='{data_column}'" if name_column != None and data_column != None else ''} WHERE {kwargs.pop('w_c')}='{kwargs.pop('w_d')}' {kwargs.get('add') if kwargs.get('add') != None else ''}""",
                *[f'{set_data}' for set_name, set_data in kwargs.items() if set_name not in column_data]
            )
        else:
            await conn.execute(
                f"""UPDATE {table} SET {', '.join([f'''{set_name}=${i + 1}''' for i, (set_name, set_data) in enumerate(kwargs.items()) if set_name not in column_data])}{(", " if len(join_data) != 0 else '') + f"{name_column}='{data_column}'" if name_column != None and data_column != None else ''} {kwargs.get('add') if kwargs.get('add') != None else ''}""",
                *[f'{set_data}' for set_name, set_data in kwargs.items() if set_name not in column_data]
            )

# INSERT-----------------------------------------------------------------------

async def ASYNC_INSERT(table: str, **kwargs):
    """

    Parameters
    ----------
    table : Table name BD.
    **kwargs : '%columns' = '%values',
        add - addition to the request,
        pgp_d = ['%column'].

    Returns
    -------
    None.

    """
    try:
        conn = await async_connection_db(db_host=db_config_local["psql"]["host"], user_name=db_config_local["psql"]["user"],
                                         user_password=db_config_local["psql"]["pass"],
                                         db_name=db_config_local["psql"]["database"])
        await insert(table, conn, kwargs)

    except Exception:
        print("ASYNC_INSERT", traceback.format_exc())
    finally:
        await conn.close()


async def insert(table, conn, kwargs):
    column_data = ['add', 'pgp_d']
    if kwargs.get('pgp_d') != None and type(kwargs.get('pgp_d')) == list and (MAIL != None and PUBLIC_KEY != None):
        kwargs.update({column: encrypt_message(str(kwargs.get(column)), MAIL, PUBLIC_KEY) for column in kwargs.get('pgp_d')})
    await conn.execute(
        f"""INSERT INTO {table} ({', '.join([column_name for column_name, column_value in kwargs.items() if column_name not in column_data])}) VALUES ({', '.join([f"${i + 1}" for i, (column_name, column_value) in enumerate(kwargs.items()) if column_name not in column_data])}) {kwargs.get('add') if kwargs.get('add') != None else ''}""",
        *[f'{column_value}' for column_name, column_value in kwargs.items() if column_name not in column_data]
    )

# DELETE-----------------------------------------------------------------------

async def ASYNC_DELETE(table: str, **kwargs):
    """

    Parameters
    ----------
    table : Table name BD.
    **kwargs : '%where_column' = '%where_data',
        add - addition to the request.
        delete_all - delete all data

    Returns
    -------
    None.

    """
    try:
        conn = await async_connection_db(db_host=db_config_local["psql"]["host"], user_name=db_config_local["psql"]["user"],
                                         user_password=db_config_local["psql"]["pass"],
                                         db_name=db_config_local["psql"]["database"])
        await delete(table, conn, kwargs)

    except Exception:
        print("ASYNC_DELETE", traceback.format_exc())
    finally:
        await conn.close()


async def delete(table, conn, kwargs):
    if kwargs.get('delete_all'):
        await conn.execute(
            f"DELETE FROM {table}")
    else:
        await conn.execute(
            f"DELETE FROM {table} WHERE {list(kwargs.items())[0][0]}=$1 {kwargs.get('add') if kwargs.get('add') != None else ''}", int(list(kwargs.items())[0][1]) if kwargs.get('int') else f'{list(kwargs.items())[0][1]}')


# SELECT-----------------------------------------------------------------------

async def ASYNC_SELECT(table: str, column: list, **kwargs):
    """"

    Parameters
    ----------
    table : Table name BD.
    column : List table columns
    **kwargs : Set w_s - 'where_status' True/False,
        w_c - 'where_column' always if True status,
        w_d - 'where_data' always if True status,
        add - addition to the request,
        pgp_d = ['%column'],
        en_w_d - 'encrypt_where_data' True/False.

    Returns
    -------
    Data.

    """
    try:
        conn = await async_connection_db(db_host=db_config_local["psql"]["host"], user_name=db_config_local["psql"]["user"],
                                         user_password=db_config_local["psql"]["pass"],
                                         db_name=db_config_local["psql"]["database"])
        return await select(table, column, conn, kwargs)

    except Exception:
        print("ASYNC_SELECT:", traceback.format_exc())
    finally:
        await conn.close()


async def select(table, column, conn, kwargs):
    if kwargs.get('en_w_d'):
        kwargs.update({'w_d': encrypt_message(str(kwargs.get('w_d')), MAIL, PUBLIC_KEY)})
    if kwargs.get('w_s'):
        result = await conn.fetch(
                     f"SELECT {', '.join(column)} FROM {table} WHERE {kwargs.pop('w_c')}=$1 {kwargs.get('add') if kwargs.get('add') != None else ''}", int(kwargs.pop('w_d')) if kwargs.get('int') else str(kwargs.pop('w_d')))
    else:
        result = await conn.fetch(
                     f"SELECT {', '.join(column)} FROM {table} {kwargs.get('add') if kwargs.get('add') != None else ''}")
    if kwargs.get('pgp_d') != None and type(kwargs.get('pgp_d')) == list and (MAIL != None and PASSPHRASE != None and PUBLIC_KEY != None and PRIVATE_KEY != None):
        new_result = []
        for r in result:
            new_row = dict(r)
            for pgp_column in kwargs.get('pgp_d'):
                new_row[pgp_column] = decrypt_message(r[pgp_column], PRIVATE_KEY, PASSPHRASE)
            new_result.append(new_row)
        result = new_result
    return result


async def test_main():
    global db_config_local, MAIL, PASSPHRASE, PUBLIC_KEY, PRIVATE_KEY
    db_config = {
        "psql": {
            "host": "127.0.0.1",
            "user": "db_user",
            "pass": "12345678",
            "database": "invest"
        }
    }

    time_start = datetime.datetime.now()
    db_config_local = db_config

    # await ASYNC_DELETE('bs.user_data', login='login_user')
    # data = await ASYNC_SELECT('bs.user_data', ['id'], w_s=True, w_c='login', w_d='login_user')
    # if len(data) == 0:
    #     await ASYNC_INSERT('bs.user_data', login='login_user', password='password', cookies={'data': 145116})
    # else: print(data)
    # await ASYNC_UPDATE('bs.user_data', cookies={'data': 759687059687}, w_s=True, w_c='login', w_d='login_user')
    # data = await ASYNC_SELECT('bs.user_data', ['id', 'login', 'password', 'cookies'], w_s=True, w_c='login', w_d='login_user')
    # print(data)
    # print(data[0]['id'])

    try:
        await ASYNC_DELETE('bs.user_data', cookies="123")
    except: None
    data = await ASYNC_SELECT('bs.user_data', ['id'], w_s=True, w_c='login', w_d='login_user_data')
    if len(data) == 0:
        await ASYNC_INSERT('bs.user_data', login='login_user_data', password='password', cookies='123', pgp_d=['login', 'password'])
    else: print(data)
    data = await ASYNC_SELECT('bs.user_data', ['id', 'login', 'password', 'cookies'], w_s=True, w_c='cookies', w_d='123')
    print(data)
    await ASYNC_UPDATE('bs.user_data', password='password123', w_s=True, w_c='cookies', w_d='123', pgp_d=['password'])
    data = await ASYNC_SELECT('bs.user_data', ['id', 'login', 'password', 'cookies'], w_s=True, w_c='cookies', w_d='123', pgp_d=['login', 'password'])
    print(data)
    await ASYNC_DELETE('bs.user_data', cookies={'data': 145116})
    print(datetime.datetime.now() - time_start)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_main())