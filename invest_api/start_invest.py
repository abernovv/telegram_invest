import time
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType
from config import TOKEN_STRATEG
from invest_api.print_portfel import activs, print_portfolio
import datetime

import app.database.requests as rq


start_time = datetime.time(10, 1, 30)   # 10:01 утра
end_time = datetime.time(22, 30, 50)    # 22:30 вечера


async def comparison(old, token):
    try:
        new = await activs(token)
        if len(new[0]) == len(old[0]):
            for i in range(len(new[0])):
                if not(new[0][i] == old[0][i] and new[0][i] == old[0][i]):
                    print(new[0][i], old[0][i], new[0][i], old[0][i])
                    old.clear()
                    for i in new:
                        old.append(i)
                    return 1
        else:
            old.clear()
            for i in new:
                old.append(i)
            return 1
        return 0

    except RequestError as e:
        print(str(e))


def buysell(token, act):
    ignorlist = ["RUB000UTSTOM", "BBG0013HGFT4", "BBG0013HJJ31"]

    money = 0
    for i in range(len(act)):
        if act[i][0] == 'RUB000UTSTOM':
            money = act[i][1]

    with Client(token) as client:
        accounts = client.users.get_accounts()
        for i in range(len(act)):
            if not (act[i][0] in ignorlist):
                bids = []
                asks = []
                if int(act[i][1]) != 0:
                    book = client.market_data.get_order_book(figi=act[i][0], depth=2)
                    bids = [p.price for p in book.bids]
                    asks = [p.price for p in book.asks]
                if int(act[i][1]) < 0:
                    # sell = client.orders.post_order(
                    #     order_id=str(datetime.datetime.now().time()),
                    #     figi=act[i][0],
                    #     price=asks[0],
                    #     quantity=act[i][1],
                    #     account_id=accounts.accounts[0].id,
                    #     direction=OrderDirection.ORDER_DIRECTION_SELL,
                    #     order_type=OrderType.ORDER_TYPE_LIMIT
                    # )
                    print(f'продать {act[i][0]} : {act[i][1]}')
                elif int(act[i][1]) > 0 and (money > bids[0].units * act[i][1]):
                    money -= bids[0].units * int(act[i][1])
                    # buy = client.orders.post_order(
                    #     order_id=str(datetime.datetime.now().time()),
                    #     figi=acc.figi,
                    #     price=bids[0],
                    #     quantity=act[i][1],
                    #     account_id=accounts.accounts[0].id,
                    #     direction=OrderDirection.ORDER_DIRECTION_BUY,
                    #     order_type=OrderType.ORDER_TYPE_LIMIT
                    # )
                    print(f'купить {act[i][0]} : {act[i][1]}')




#создает список покупок\продаж
async def buy_sell_list(strategs_arr, token, token_id):
    user = []
    with Client(token) as client:
        accounts = client.users.get_accounts()
        t = print_portfolio(client, accounts, 0)
        user = [t['figi'], t['quantity'], t['lots'], t['balans'], accounts.accounts[0].name]
        orders = client.orders.get_orders(account_id=accounts.accounts[0].id)
        # print(user)
        for order in orders.orders:
            for i in range(len(user[0])):
                if order.figi == user[0][i]:
                    if order.direction == 1:
                        user[2][i] += (order.lots_requested - order.lots_executed)
                    if order.direction == 2:
                        user[2][i] -= (order.lots_requested - order.lots_executed)

    if token_id == '500961694':
        user[3] = int(user[3]) + 5000
    print(user[3], user[4])
    multiplier = (int(user[3]) * 1.0) / int(strategs_arr[3])

    # Создаем словарь для хранения итоговых значений
    result_dict = {}

    # Добавляем значения из первого списка
    for i in range(len(strategs_arr[0])):
        result_dict[str(strategs_arr[0][i])] = int(strategs_arr[2][i] * multiplier)

    # Вычитаем значения из второго списка
    for i in range(len(user[0])):
        key = str(user[0][i])
        if key != 'RUB000UTSTOM':
            if key in result_dict:
                result_dict[key] -= user[2][i]
            else:
                result_dict[key] = -user[2][i]  # Если имени нет, добавляем как отрицательное значение
        else:
            result_dict[key] = user[2][i]
            if token_id == '500961694':
                result_dict[key] += 5000

    # Преобразуем словарь в список для вывода
    result_list = [(name, value) for name, value in result_dict.items()]

    # for name, value in result_list:
    #     print("    ",name, value)

    buysell(token, result_list)

async def proverka(ARR,name):
    if await comparison(ARR, TOKEN_STRATEG[name]):
        print(name)
        # for i in range(len(ARR[0])):
        #      print(ARR[0][i], ARR[2][i])
        data = await rq.select_strateg(name)
        for d in data:
            await buy_sell_list(ARR, d[1], d[0])
            time.sleep(1)
    time.sleep(2)


async def start_invest():
    try:
        TENI = ["", 0, 0, 0]
        RF = ["", 0, 0, 0]
        VOLNA = ["", 0, 0, 0]
        while 1:
            current_time = datetime.datetime.now().time()  # Получение текущего времени
            if ((datetime.time(14, 0, 30) <= current_time <= datetime.time(14, 1, 0)) or
                    (datetime.time(18, 0, 30) <= current_time <= datetime.time(18, 1, 0))):
                print("CLEAR STRATEGS")
                TENI = ["", 0, 0, 0]
                RF = ["", 0, 0, 0]
                VOLNA = ["", 0, 0, 0]
            if start_time <= current_time <= end_time:
                await proverka(TENI, 'teni')
                await proverka(RF, 'rost')
                await proverka(VOLNA, 'volna')


    except RequestError as e:
        print(str(e))
        time.sleep(10)
        await start_invest()
