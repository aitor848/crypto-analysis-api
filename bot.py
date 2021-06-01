import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = 'wss://stream.binance.com:9443/ws/ethusdt@kline_1m'

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.006

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)  #+tld='us')


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    """ Function to buy crypto."""
    try:
        print("Sending order...")
        order = client.create_order(
            side=side,
            quatity=quantity,
            symbol=symbol,
            type=order_type,
        )
        print(order)

    except Exception as e:
        return False

    return True


def on_open(ws):
    print('Opened connection!')


def on_close(ws):
    print('Closed connection!')


def on_message(ws, message):
    global closes

    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print(f"Candle closed at {close}")
        closes.append(float(close))
        print('###closes###')
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print('!!!All rsis calculated so far!!!')
            print(rsi)
            last_rsi = rsi[-1]
            print(f"The last rsi is {last_rsi}")

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbouth! Sell! Sell! Sell!")
                    # Put binance sell logic here:
                    order_succeeded = order(
                        SIDE_SELL,
                        TRADE_QUANTITY,
                        TRADE_SYMBOL,
                    )
                    if order_succeeded:
                        in_position = False
                else:
                    print(
                        "It is overbought, but We don't own any. Nothing to do."
                    )

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print(
                        "It is oversold, but you already own it, nothing to do."
                    )
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # Put binance buy order logic here:
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY,
                                            TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True


ws = websocket.WebSocketApp(SOCKET,
                            on_open=on_open,
                            on_close=on_close,
                            on_message=on_message)
ws.run_forever()