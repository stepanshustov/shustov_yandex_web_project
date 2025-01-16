import mimetypes
import time

import Weather
from config import *
from addution import *

import asyncio
import aiogram
from aiogram import Dispatcher, Bot
from aiogram.filters import *
from aiogram.types import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import *
from aiogram.types.input_file import FSInputFile
from aiogram import F
from aiogram.utils.keyboard import *

import aioschedule


async def main():
    dp = Dispatcher()
    bot = Bot(BOT_TOKEN)
    state_data = dict()

    class Fsm(StatesGroup):
        set_lan = State()
        for_weather = State()
        cur_weather = State()
        utc_us = State()
        add_d_w = State()

    async def add_menu_ikb(uid):

        ikb = InlineKeyboardBuilder()
        b1 = InlineKeyboardButton(text=text_translator('Current weather', dest=users[uid].lang),
                                  callback_data='current_weather')
        b2 = InlineKeyboardButton(text=text_translator('Weather forecast', dest=users[uid].lang),
                                  callback_data='forecast_weather')
        b3 = InlineKeyboardButton(text=text_translator('Notifications', dest=users[uid].lang),
                                  callback_data='notifications')
        ikb.row(b1, b2)
        ikb.row(b3)
        users.menu_keyboard[uid] = ikb

    async def add_notif_ikb(uid):
        ikb = InlineKeyboardBuilder()
        b1 = InlineKeyboardButton(text=text_translator('Current weather', dest=users[uid].lang),
                                  callback_data='add_current_weather')
        b2 = InlineKeyboardButton(text=text_translator('Weather forecast', dest=users[uid].lang),
                                  callback_data='add_forecast_weather')
        b3 = InlineKeyboardButton(text=text_translator('Your list of notifications', dest=users[uid].lang),
                                  callback_data='notifications_list')
        ikb.row(b1, b2)
        ikb.row(b3)
        users.notif_keyboard[uid] = ikb

    async def menu_mes(uid):
        if uid not in users.menu_keyboard:
            await add_menu_ikb(uid)
        await bot.send_message(chat_id=uid,
                               text=text_translator("menu:", dest=users[uid].lang),
                               reply_markup=users.menu_keyboard[uid].as_markup())

    @dp.message(Command('start'))
    async def st(m: Message, state: FSMContext):
        await m.answer("Hello, I will tell you the weather forecast anywhere and in any language.")
        await m.answer("What language do you speak?")
        await state.set_state(Fsm.set_lan)

    @dp.message(Fsm.set_lan)
    async def st_lan(m: Message, state: FSMContext):
        txt = text_translator(m.text.lower().strip().rstrip()).lower()
        if txt in LANGUAGES:
            users.add_user(m.from_user.id, LANGUAGES[txt])
            await state.set_state(Fsm.utc_us)
            await m.answer(text=text_translator("Введите ваш часовой пояс от -12 до +12", txt))
            await add_menu_ikb(m.from_user.id)
            await add_notif_ikb(m.from_user.id)
        else:
            await m.answer("Please check your spelling")

    @dp.message(Fsm.utc_us)
    async def utc_m(m: Message, state: FSMContext):
        try:
            d = int(m.text.replace(' ', '').strip())
            if d < -12 or d > 12:
                raise Exception
            users[m.from_user.id].utc = d
            users.session.commit()
            await menu_mes(m.from_user.id)
        except Exception as ex:
            await m.answer(text_translator("Проверьте правильность", users[m.from_user.id].lang))

    @dp.callback_query(F.data == 'current_weather')
    async def cur_w(c: CallbackQuery, state: FSMContext):
        await state.set_state(Fsm.cur_weather)
        await bot.send_message(chat_id=c.from_user.id,
                               text=text_translator('Введите название населенного пункта',
                                                    dest=users[c.from_user.id].lang))

    @dp.callback_query(F.data == 'forecast_weather')
    async def for_w(c: CallbackQuery, state: FSMContext):
        await state.set_state(Fsm.for_weather)
        await bot.send_message(chat_id=c.from_user.id,
                               text=text_translator('Введите название населенного пункта',
                                                    dest=users[c.from_user.id].lang))

    @dp.callback_query(F.data == 'notifications')
    async def del_m(c: CallbackQuery, state: FSMContext):
        if c.from_user.id not in users.notif_keyboard:
            await add_notif_ikb(c.from_user.id)
        await bot.send_message(chat_id=c.from_user.id,
                               text=text_translator(text="Create a notification about:",
                                                    dest=users[c.from_user.id].lang),
                               reply_markup=users.notif_keyboard[c.from_user.id].as_markup())

    @dp.callback_query(F.data == 'notifications_list')
    async def notif_list(c: CallbackQuery, state: FSMContext):
        lst_not = users.get_all_delayed_for_us(c.from_user.id)
        if len(lst_not) == 0:
            await bot.send_message(chat_id=c.from_user.id,
                                   text=text_translator(text="У вас нет созданных уведомлений",
                                                        dest=users[c.from_user.id].lang))
            await menu_mes(c.from_user.id)
            return
        ikb = InlineKeyboardBuilder()
        for el in lst_not:
            el: Delayed
            t = 'текущая погода' if el.tp == 1 else "прогноз погоды"
            ikb.row(InlineKeyboardButton(
                text=text_translator(f'{el.city} {el.time} {t}', dest=users[c.from_user.id].lang),
                callback_data='_'),
                InlineKeyboardButton(text=text_translator("Удалить", users[c.from_user.id].lang),
                                     callback_data=f'del_notif;{el.id}'))
        await bot.send_message(chat_id=c.from_user.id,
                               text=text_translator("Your list of notifications", users[c.from_user.id].lang),
                               reply_markup=ikb.as_markup())
        await menu_mes(c.from_user.id)

    @dp.message(Fsm.cur_weather)
    async def cur_w_mes(m: Message, state: FSMContext):
        if m.from_user.id not in users.menu_keyboard:
            await add_menu_ikb(m.from_user.id)
        st_, ic = current_weather(m.text)
        await m.answer(text_translator(st_, dest=users[m.from_user.id].lang),
                       reply_markup=users.menu_keyboard[m.from_user.id].as_markup(), parse_mode='html')
        if ic:
            document = FSInputFile(f'ikons/{ic}')
            await bot.send_document(m.from_user.id, document)

    @dp.message(Fsm.for_weather)
    async def for_w_mes(m: Message, state: FSMContext):
        if m.from_user.id not in users.menu_keyboard:
            await add_menu_ikb(m.from_user.id)

        lst = forecast_weather(m.text.strip())
        for el in lst:
            await m.answer(text_translator(el, dest=users[m.from_user.id].lang), parse_mode='html')
        await menu_mes(m.from_user.id)

    @dp.callback_query()
    async def cal_q(c: CallbackQuery, state: FSMContext):
        data = c.data.split(';')
        # print(1)
        if data[0] == 'del_notif':
            users.del_delayed(int(data[1]))
            await bot.send_message(chat_id=c.from_user.id,
                                   text=text_translator('Успешно удалено', users[c.from_user.id].lang))
            await menu_mes(c.from_user.id)
        elif data[0] == 'add_current_weather' or data[0] == 'add_forecast_weather':
            # print(2)
            await state.set_state(Fsm.add_d_w)
            state_data[c.from_user.id] = data[0]
            await bot.send_message(chat_id=c.from_user.id,
                                   text=text_translator("""Напишите через пробел место для погоды и время, в которое должно прийти уведомление.
Например: Москва 12:34""", dest=users[c.from_user.id].lang))

    @dp.message()
    async def mess_(m: Message, state: FSMContext):
        try:
            a, b = m.text.strip().lower().split()
            h, mn = map(int, b.split(':'))
            c, d = Weather.local_coord(a)
            if c is None:
                raise Exception
            if not (0 <= h <= 12 and 0 <= mn <= 59):
                raise Exception
            tp = 0
            if state_data[m.from_user.id] == 'add_current_weather':
                tp = 1
            users.add_delayed_message(m.from_user.id, a, tp, f'{h}:{mn}')
            await m.answer(text=text_translator("Успешно", dest=users[m.from_user.id].lang))
            await state.clear()
            await menu_mes(m.from_user.id)
        except Exception as ex:
            await m.answer(text_translator("Проверьте правильность написания", dest=users[m.from_user.id].lang))
            print(ex)

    async def delayed_message(uid: int, city: str, tp: int, tm: str):
        if len(city.strip().split(';')) == 2:
            city = tuple(map(float, city.rstrip().split(';')))
        if tp == 1:
            txt = [current_weather(city)]
        else:
            txt = forecast_weather(city)
        await bot.send_message(chat_id=uid,
                               text=text_translator(text=f"""Ваш отложенный запрос на {tm}""", dest=users[uid].lang),
                               parse_mode='html')
        for el in txt:
            await bot.send_message(chat_id=uid,
                                   text=text_translator(text=el, dest=users[uid].lang),
                                   parse_mode='html')
        # print(txt)

    async def fun_on_start():
        while True:
            used_time = set()
            dtn = datetime.now()
            h, m = dtn.hour, dtn.minute
            if (h, m) not in used_time:
                for el in users.get_all_delayed_for_time(f'{h}:{m}'):
                    el: Delayed
                    await delayed_message(el.user_id, el.city, el.tp, f'{h - 4 + users[el.user_id].utc}:{m}')
                    await menu_mes(el.user_id)
            else:
                used_time.add((h, m))
            await asyncio.sleep(40)

    async def on_start():
        asyncio.create_task(fun_on_start())

    dp.startup.register(on_start)
    await dp.start_polling(bot)


if __name__ == '__main__':
    while True:
        try:
            # print(2)
            engine = create_engine(f"sqlite:///{'users.db'}", echo=False)
            Base.metadata.create_all(engine)
            with Session(engine) as session:
                users = Users(engine, session)
                # print(users[1947257111].locals[0].city)
                asyncio.run(main())
        except Exception as ex:
            time.sleep(1)
            print(ex)
