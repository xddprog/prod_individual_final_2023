from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from datetime import datetime

from database.methods import Database
from FSMS.FSMS import (CheckTravelsFSM, CreateNoteFSM)


router = Router()


@router.callback_query(StateFilter(*[i for i in CreateNoteFSM.__states__]), F.data == 'back_to_menu')
@router.callback_query(CheckTravelsFSM.travel_info, F.data == 'back_to_menu')
async def cmd_back_to_menu_from_notes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    pages = data['pages']
    user = await Database.get_user(callback.from_user.id, return_user=True)
    menu = await pages.get_menu_page()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer(
        text=menu.text.format(
            user.nickname,
            user.age,
            user.description,
            user.country,
            user.city,
            user.full_address
        ),
        reply_markup=menu.reply_markup,
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == 'back_to_menu')
async def cmd_back_to_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    user = await Database.get_user(callback.from_user.id, return_user=True)
    menu = await pages.get_menu_page()
    await state.set_state(menu.state)
    await state.set_data({'user': user, 'pages': pages})
    await callback.message.edit_text(
        text=menu.text.format(
            user.nickname,
            user.age,
            user.description,
            user.country,
            user.city,
            user.full_address
        ),
        reply_markup=menu.reply_markup,
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == 'back')
async def cmd_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    prev_page = await pages.get_prev_page()
    await state.set_state(prev_page.state)
    await callback.message.edit_text(
        text=prev_page.text,
        reply_markup=prev_page.reply_markup,
        parse_mode=ParseMode.HTML
    )