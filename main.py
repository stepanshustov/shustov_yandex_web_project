import time

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

    class Fsm(StatesGroup):
        set_lan = State()
        for_weather = State()
        cur_weather = State()

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

            ikb = InlineKeyboardBuilder()
            ikb.add(InlineKeyboardButton(text=text_translator('current weather', dest=users[m.from_user.id].lang),
                                         callback_data='current_weather'))
            ikb.add(InlineKeyboardButton(text=text_translator('weather forecast', dest=users[m.from_user.id].lang),
                                         callback_data='forecast_weather'))
            users.keyboard[m.from_user.id] = ikb

            await m.answer(
                text_translator("menu:", dest=users[m.from_user.id].lang),
                reply_markup=ikb.as_markup())
            await state.clear()
        else:
            await m.answer("Please check your spelling")

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

    @dp.message(Fsm.cur_weather)
    async def mes_1(m: Message, state: FSMContext):
        if m.from_user.id not in users.keyboard:
            ikb = InlineKeyboardBuilder()
            ikb.add(InlineKeyboardButton(text=text_translator('current weather', dest=users[m.from_user.id].lang),
                                         callback_data='current_weather'))
            ikb.add(InlineKeyboardButton(text=text_translator('weather forecast', dest=users[m.from_user.id].lang),
                                         callback_data='forecast_weather'))
            users.keyboard[m.from_user.id] = ikb
        st_, ic = current_weather(m.text)
        await m.answer(text_translator(st_, dest=users[m.from_user.id].lang),
                       reply_markup=users.keyboard[m.from_user.id].as_markup(), parse_mode='html')
        if ic:
            document = FSInputFile(f'ikons/{ic}')
            await bot.send_document(m.from_user.id, document)

    @dp.message(Fsm.for_weather)
    async def ms_2(m: Message, state: FSMContext):
        if m.from_user.id not in users.keyboard:
            ikb = InlineKeyboardBuilder()
            ikb.add(InlineKeyboardButton(text=text_translator('current weather', dest=users[m.from_user.id].lang),
                                         callback_data='current_weather'))
            ikb.add(InlineKeyboardButton(text=text_translator('weather forecast', dest=users[m.from_user.id].lang),
                                         callback_data='forecast_weather'))
            users.keyboard[m.from_user.id] = ikb
        lst = forecast_weather(m.text.strip())
        for el in lst:
            await m.answer(text_translator(el, dest=users[m.from_user.id].lang), parse_mode='html')
        await m.answer(text_translator("menu:",
                                       dest=users[m.from_user.id].lang),
                       reply_markup=users.keyboard[m.from_user.id].as_markup())

    async def delayed_message(uid: int, city: str, tp: int):
        if tp == 1:
            txt = current_weather(city)
        else:
            txt = forecast_weather(city)
        await bot.send_message(chat_id=uid, text=text_translator(text=txt, dest=users[uid].lang))

    async def on_start():
        pass

    # dp.startup.register(on_start())
    await dp.start_polling(bot)


if __name__ == '__main__':
    while True:
        try:
            engine = create_engine(f"sqlite:///{'users.db'}", echo=False)
            Base.metadata.create_all(engine)
            with Session(engine) as session:
                users = Users(engine, session)
                asyncio.run(main())
        except Exception as ex:
            time.sleep(1)
            print(ex)
