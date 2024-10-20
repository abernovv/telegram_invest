import pandas as pd
from tinkoff.invest import Client, RequestError, PortfolioResponse, PortfolioPosition
from config import FULL_MAIN_TOKEN

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

with Client(FULL_MAIN_TOKEN) as client:
    instr = client.instruments.get_assets().assets
    assets = {}

    for i in instr:
        if len(i.instruments):
            assets[i.instruments[0].figi] = i.instruments[0].ticker


def print_portfolio(client, accounts, accid):
    total_balance = 0.0
    r: PortfolioResponse = client.operations.get_portfolio(account_id=accounts.accounts[accid].id)

    # Преобразование данных в DataFrame
    df = pd.DataFrame([portfolio_position_to_dict(p) for p in r.positions])

    # Расчет баланса текущего счета
    account_balance = df['sell_sum'].sum()
    total_balance += account_balance

    # Вывод информации о портфеле
    #print(df.head(100))

    account_info = {'balans': total_balance, 'figi': df['figi'], 'quantity': df['quantity'], 'lots': df['lots']}
    return account_info


async def print_activ_str(token):
    activ = await activs(token)
    s = activ[4] + " : " + str(int(activ[3])) + "p\nfigi/ticker" + " "*2 + "  |quantity   |lots\n"
    for i in range(len(activ[0])):
        if activ[0][i] in assets.keys():
            s += assets[activ[0][i]].ljust(15) + "|" + str(int(activ[1][i])).ljust(11) + "|" + str(activ[2][i]) + '\n'
        elif activ[0][i] == "RUB000UTSTOM":
            text = "RUB"
            s += text.ljust(15) + "|" + str(int(activ[1][i])).ljust(11) + "|" + str(activ[2][i]) + '\n'
        else:
            s += str(activ[0][i]).ljust(15) + "|" + str(int(activ[1][i])).ljust(11) + "|" + str(activ[2][i]) + '\n'
    return s


async def activs(token):
    try:
        with Client(token) as client:
            accounts = client.users.get_accounts()
            t = print_portfolio(client, accounts, 0)
            return [t['figi'], t['quantity'], t['lots'], t['balans'], accounts.accounts[0].name]
    except RequestError as e:
        print(f"Ошибка запроса: {e}")
    return 0


def portfolio_position_to_dict(p: PortfolioPosition):
    r = {
        'figi': p.figi,
        'quantity': cast_money(p.quantity),
        'expected_yield': cast_money(p.expected_yield),
        'lots': p.quantity_lots.units,
        'instrument_type': p.instrument_type,
        'average_buy_price': cast_money(p.average_position_price),
    }

    r['sell_sum'] = (r['average_buy_price'] * r['quantity']) + r['expected_yield']
    return r


def cast_money(v):
    return v.units + v.nano / 1e9  # nano - 9 нулей
