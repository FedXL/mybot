from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class SuperMenu(KeyboardButton,ReplyKeyboardMarkup):

    __btnMain = KeyboardButton('Назад')
    __btn1 = KeyboardButton('Сделать заказ')
    __btn2 = KeyboardButton('Koнсультация')
    menu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btn1).add(__btn2)

    __btnFAQ = KeyboardButton('FAQ')
    __btnTranzit = KeyboardButton('Посчитать примерную стоимость заказа транзитом через Казахстан')
    __btnInvoice = KeyboardButton('Посчитать примерную стоимость по выкупу заказа')
    consMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnFAQ).\
                                                        add(__btnTranzit).\
                                                        add(__btnInvoice).\
                                                        add(__btnMain)

    __btnBuyKazah = KeyboardButton('Заказ через Казахстан')
    __btnBuyTranzit = KeyboardButton('Заказ Tradeinn')
    __btnBuyInvoice = KeyboardButton('Выкуп заказа')
    invoiceMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnBuyKazah).\
                                                            add(__btnBuyTranzit).\
                                                            add(__btnBuyInvoice).\
                                                            add(__btnMain)
    __btnFaqKazah = KeyboardButton('Покупка транзитом через Казахстан')
    __btnFaqTranzit = KeyboardButton('Покупка на Tradeinn')
    __btnFaqPosrednik = KeyboardButton('Покупка через почтовых посредников')
    faqMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnFaqKazah).\
                                                        add(__btnFaqTranzit).\
                                                        add(__btnFaqPosrednik).\
                                                        add(__btnMain)

    __btnHrefs = KeyboardButton('Предоставлю ссылки на товары')
    __btnKabinet = KeyboardButton('Предоставлю доступ в личный кабинет')
    kaz_choice_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnHrefs).\
                                                                add(__btnKabinet).\
                                                                add(__btnMain)

    cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnMain)


    __btnOrder = KeyboardButton('Завершить заказ')
    kaz_order = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnOrder).add(__btnMain)

    __btnEuro = KeyboardButton("Евро")
    __btnUsd = KeyboardButton("Доллар")
    EuroBaksMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnEuro, __btnUsd).add( __btnMain)

    __btnComment = KeyboardButton("Без комментариев")
    CommentMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(__btnComment).add(__btnOrder).add(__btnMain)


