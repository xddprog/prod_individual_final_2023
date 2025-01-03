import os

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from lexicon import messages, buttons_texts
from keyboards.keyboards import Keyboards
from utils.routing import RoutingMethods
from database.methods import Database
from FSMS.FSMS import CheckTravelsFSM, CreateNoteFSM, NotesFSM, NoteEditFSM


router = Router()


@router.callback_query(F.data == 'check_travels')
async def cmd_check_travels(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    user = data['user']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(CheckTravelsFSM.choose_travel)
    await callback.message.edit_text(
        text=messages.check_travels_texts['check_all_travels'].format(
            len(user.travels)
        ),
        reply_markup=Keyboards.user_travels_keyboard(user.travels),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(CheckTravelsFSM.choose_travel, F.data != 'back_to_menu')
async def cmd_check_travel_info(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    travel_id = callback.data.split(':')[-1]
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    travel = await Database.get_travel(travel_id)
    await state.update_data(travel=travel)
    await state.set_state(CheckTravelsFSM.travel_info)
    await callback.message.edit_text(
        text=messages.check_travels_texts['check_one_travel'].format(
            travel.name,
            len(travel.users),
            travel.points[-1].start_date,
            len(travel.points)
        ),
        reply_markup=Keyboards.check_travel_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(CheckTravelsFSM.travel_info, F.data == 'delete_travel')
async def cmd_delete_travel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(CheckTravelsFSM.delete_or_not)
    await callback.message.edit_text(
        text=messages.check_travels_texts['delete'],
        reply_markup=Keyboards.yes_no_keyboard()
    )


@router.callback_query(CheckTravelsFSM.delete_or_not, F.data == 'yes')
async def cmd_delete_travel_accept(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    travel = data['travel']
    await Database.delete_travel(travel.travel_id, callback.from_user.id)
    await callback.message.edit_text(
        text=messages.check_travels_texts['delete_successfully'],
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )


@router.callback_query(CheckTravelsFSM.delete_or_not, F.data == 'no')
async def cmd_delete_travel_accept(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    travel = data['travel']
    pages = data['pages']
    prev_page = pages.get_prev_page()
    await state.set_state(prev_page.state)
    await callback.message.edit_text(
        text=prev_page.text,
        reply_markup=prev_page.reply_markup
    )


@router.callback_query(CheckTravelsFSM.travel_info, F.data == 'create_map')
async def cmd_get_travel_map(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    travel = data['travel']
    points = travel.points
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    if data.get('file'):
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=data.get('file'),
            caption='',
            reply_markup=Keyboards.base_keyboard(
                buttons_texts.save_button,
                back_buttons=True
            )
        )
    else:
        file_path = await RoutingMethods.create_travel_map(points, travel.travel_mode, travel.travel_id)
        photo = FSInputFile(path=file_path)
        msg = await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo,
            caption='',
            reply_markup=Keyboards.base_keyboard(
                buttons_texts.save_button,
                back_buttons=True
            )
        )
        await state.update_data(file=msg.photo[-1].file_id)
        await state.set_state(CheckTravelsFSM.check_map)
        os.remove(file_path)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(CheckTravelsFSM.check_map, F.data == 'save_in_notes')
async def cmd_save_map_to_notes_privacy(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(CreateNoteFSM.is_private)
    await callback.message.answer(
        text=messages.create_note_texts['is_private'],
        reply_markup=Keyboards.base_keyboard(buttons_data=buttons_texts.is_private_buttons, back_buttons=True)
    )
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
