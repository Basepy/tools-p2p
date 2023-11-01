from telebot import types


def menu_01():
    teclado_01 = types.InlineKeyboardMarkup()
    bt_menu_01 = types.InlineKeyboardButton("BTC", callback_data='btn_btc')
    teclado_01.add(bt_menu_01)
    return teclado_01

