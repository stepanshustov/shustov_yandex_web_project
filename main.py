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

dp = Dispatcher()
bot = Bot(BOT_TOKEN)


class Fsm(StatesGroup):
    set_lan = State()


@dp.message(Command('start'))
async def st(m: Message, state: FSMContext):
    await m.answer("Hello, I will tell you the weather forecast anywhere and in any language.")
    await m.answer("What language do you speak?")
    await state.set_state(Fsm.set_lan)


@dp.message(Fsm.set_lan)
async def st_lan(m: Message, state: FSMContext):
    txt = text_translator(m.text.lower().strip().rstrip()).lower()
    if txt in LANGUAGES:
        users.add(m.from_user.id, LANGUAGES[txt])
        await m.answer(text_translator("Отлично, теперь введите название населенного пункта для прогноза погоды",
                                       dest=users[m.from_user.id]))
        await state.clear()
    else:
        await m.answer("Please check your spelling")


@dp.message()
async def mes(m: Message, state: FSMContext):
    st_, ic = weather(m.text)
    await m.answer(text_translator(st_, dest=users[m.from_user.id]))
    document = FSInputFile(f'ikons/{ic}')
    await bot.send_document(m.from_user.id, document)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    users = Users('users.db')
    asyncio.run(main())
