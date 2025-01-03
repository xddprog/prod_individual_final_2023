from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from lexicon import messages, buttons_texts
from FSMS.FSMS import RegistrationFSM, ProfileEditFSM
from keyboards.keyboards import Keyboards
from database.methods import Database
from filters import filters
from utils.pages import Pages


router = Router()


@router.message(CommandStart(), filters.CheckExistsUser())
async def cmd_start_and_set_nickname(message: Message, state: FSMContext):
    await state.update_data(user_id=message.from_user.id)
    await message.answer(
        text=messages.registration_texts['nickname']
    )
    await state.set_state(RegistrationFSM.nickname)


@router.message(CommandStart())
async def cmd_start_and_set_nickname_error(message: Message, state: FSMContext):
    await message.answer(
        text=messages.errors['user_exists']
    )


@router.message(Command('menu'), ~filters.CheckExistsUser())
async def cmd_check_profile(message: Message, state: FSMContext):
    user = await Database.get_user(message.from_user.id, return_user=True)
    await state.update_data(user=user, pages=Pages())
    await message.answer(
        text=messages.my_profile_texts['check_profile'].format(
            user.nickname,
            user.age,
            user.description,
            user.country,
            user.city,
            user.full_address
        ),
        reply_markup=Keyboards.base_keyboard(buttons_texts.profile_buttons),
        parse_mode=ParseMode.HTML
    )


@router.message(Command('menu'))
async def cmd_check_profile(message: Message, state: FSMContext):
    await message.answer(
        text=messages.errors['user_not_exists']
    )

