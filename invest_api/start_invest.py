import asyncio
import datetime

from pandas.core.dtypes.cast import np_can_hold_element

from invest_api.print_portfel import activs, print_portfolio
from tinkoff.invest import Client, OrderDirection, OrderType, RequestError
import matplotlib
import matplotlib.pyplot as plt

import app.database.requests as rq
from config import ADMIN_CHAT


n=0
start_time = datetime.time(10-n, 1, 30)   # 10:01 утра начало торгового дня
end_time = datetime.time(22-n, 30, 50)    # 22:30 вечера конец торгового дня


async def comparison(old, token):
    try:
        new = await activs(token)
        if len(new[0]) == len(old[0]):
            for i in range(len(new[0])):
                if not(new[0][i] == old[0][i] and new[1][i] == old[1][i]):
                    print(new[0][i], old[0][i], new[1][i], old[1][i])
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
        return 0


def buysell(token, act):
    ignorlist = ["RUB000UTSTOM", "BBG0013HGFT4", "BBG0013HJJ31"] # бумаги которые мы будем игнорировать по типу валюты

    money = 0
    for i in range(len(act)):
        if act[i][0] == 'RUB000UTSTOM':
            money = act[i][1]

    with Client(token) as client:
        accounts = client.users.get_accounts()
        for i in range(len(act)): #проходим по всем позициям которые отличчаются от авторской стратегии
            if not (act[i][0] in ignorlist):
                bids = []
                asks = []
                if int(act[i][1]) != 0:
                    book = client.market_data.get_order_book(figi=act[i][0], depth=2)
                    bids = [p.price for p in book.bids]
                    asks = [p.price for p in book.asks]
                if int(act[i][1]) < 0: # создает офер на продажу если у человека больше акций чем у автора
                    sell = client.orders.post_order(
                        order_id=str(datetime.datetime.now().time()),
                        figi=act[i][0],
                        price=asks[0],
                        quantity=-act[i][1],
                        account_id=accounts.accounts[0].id,
                        direction=OrderDirection.ORDER_DIRECTION_SELL,
                        order_type=OrderType.ORDER_TYPE_LIMIT
                    )
                    print(f'продать {act[i][0]} : {-act[i][1]}')
                elif int(act[i][1]) > 0 and (money > bids[0].units * act[i][1]): # создает офер на покупку если у человека меньше акций чем у автора и проверяет что ему хватит денег
                    money -= bids[0].units * int(act[i][1])
                    buy = client.orders.post_order(
                        order_id=str(datetime.datetime.now().time()),
                        figi=act[i][0],
                        price=bids[0],
                        quantity=act[i][1],
                        account_id=accounts.accounts[0].id,
                        direction=OrderDirection.ORDER_DIRECTION_BUY,
                        order_type=OrderType.ORDER_TYPE_LIMIT
                    )
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

    if token_id in ADMIN_CHAT:
        user[3] = int(user[3]) + 5000

    multiplier = round( (int(user[3]) * 1.0) / int(strategs_arr[3]),2)

    print(user[3], user[4], round(multiplier, 2))
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
            if token_id in ADMIN_CHAT:
                result_dict[key] += 5000

    # Преобразуем словарь в список для вывода
    result_list = [(name, value) for name, value in result_dict.items()]

    # for name, value in result_list:
    #     print("    ",name, value)

    buysell(token, result_list)


async def proverka(ARR, name):
    try:
        TOKEN_STRATEG_V2 = await rq.select_token_strategs('all')
        if await comparison(ARR, TOKEN_STRATEG_V2[name][0]):
            # for i in range(len(ARR[0])):
            #      print(ARR[0][i], ARR[2][i])
            await asyncio.sleep(10)
            data = await rq.select_strateg(name)
            ARR = await activs(TOKEN_STRATEG_V2[name][0])
            print(f"\033[1;32;40m {name} {ARR[3] } \033[0m")
            for d in data:
                await buy_sell_list(ARR, d[1], d[0])
                await asyncio.sleep(1)
        await asyncio.sleep(2)
    except RequestError as e:
        print(str(e))
        return 0


#функция которая создает график исходы из данных в базе данных
matplotlib.use('Agg')
async def creat_grafs():
    print("creat_graf")
    TOKEN_STRATEG_V2 = await rq.select_token_strategs('all')
    for i in TOKEN_STRATEG_V2.keys():
        if i != "none":
            activ = await activs(TOKEN_STRATEG_V2[i][0])
            await rq.insert_graf(i, str(int(activ[3])))
            s = await rq.select_graf(i)
            arr = []
            for j in range(len(s)):
                arr.append(int(s[j][0]))
            plt.plot(arr)
            plt.title('График динамики стратегии ' + activ[4])
            plt.xlabel('Индекс')
            plt.ylabel('цена')

            # Сохранение графика как изображения
            plt.savefig('images/'+i+'.png', format='png')  # Сохранение в формате PNG
            plt.close()


def clear_strategies(strateg):
    for key in strateg.keys():
        strateg[key] = ["", 0, 0, 0]


async def start_invest():
    try:
        creat_graf = 0
        TOKEN_STRATEG_V2 = await rq.select_token_strategs('all')
        strategies = {key: ["", 0, 0, 0] for key in TOKEN_STRATEG_V2 if key != 'none'}
        time_intervals = [10, 12, 14, 16, 18]  # время в которое будут проверяться все аккаунты на совпадение со стратегией
        while 1:
            current_time = datetime.datetime.now().time()  # Получение текущего времени
            if any(datetime.time(hour - n, 0, 50)
                   <= current_time <=
                   datetime.time(hour - n, 1, 0) for hour in time_intervals):
                print("CLEAR STRATEGS")
                TOKEN_STRATEG_V2 = await rq.select_token_strategs('all') # получение списка всех стратегий
                strategies = {key: ["", 0, 0, 0] for key in TOKEN_STRATEG_V2 if key != 'none'}
                clear_strategies(strategies)

            if start_time <= current_time <= end_time: # время торгового деня
                creat_graf = 0
                for key in TOKEN_STRATEG_V2.keys(): # проходит по всем стратегиям
                    if key != 'none':
                        await proverka(strategies[key], key)

            elif creat_graf == 0: # когда заканчивается торговый день, генерирует граф в котором отображается изменение
                creat_graf = 1
                await creat_grafs()

    except RequestError as e:
        print(str(e))
        await asyncio.sleep(10)
        await start_invest()



