from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from lexicon import messages, buttons_texts
from FSMS.FSMS import CheckTravelsFSM
from keyboards.keyboards import Keyboards
from database.methods import Database
from filters import filters
from utils.pages import Pages


router = Router()


@router.callback_query(CheckTravelsFSM.travel_info, F.data == 'check_points')
async def cmd_check_travel_points(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    travel = data['travel']
    await pages.update_states(callback=callback, state=state)
    await callback.message.edit_text(
        text=messages.travel_points_text['check_points'].format(
            len(travel.points)
        )
    )
