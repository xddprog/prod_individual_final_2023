from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from datetime import datetime

from lexicon import messages, buttons_texts
from keyboards.keyboards import Keyboards
from utils.routing import RoutingMethods
from utils.location import LocationMethods
from utils.pages import Pages
from database.methods import Database
from filters import filters
from FSMS.FSMS import AddTravelFSM


router = Router()


@router.callback_query(F.data == 'add_travel')
async def cmd_add_new_travel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddTravelFSM.mode)
    await callback.message.edit_text(
        text=messages.add_travel_texts['mode'],
        reply_markup=Keyboards.base_keyboard(
            buttons_texts.travel_modes,
            back_buttons=True,
            only_back_to_menu=True
        )
    )


@router.callback_query(AddTravelFSM.mode, F.data == 'drive')
async def cmd_travel_drive_mode(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(mode=callback.data)
    await state.set_state(AddTravelFSM.start_travel_date)
    await callback.message.edit_text(
        text=messages.add_travel_texts['start_date'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(AddTravelFSM.start_travel_date, F.text, filters.ValidStartDate())
async def cmd_get_start_travel_date(message: Message, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    start_travel_date = datetime.strptime(message.text, '%d.%m.%Y %H.%M')
    await pages.update_states(message=message, state=state)
    await state.update_data(start_travel_date=start_travel_date)
    await state.set_state(AddTravelFSM.name)
    await message.answer(
        text=messages.add_travel_texts['name'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(AddTravelFSM.name, filters.NicknameValid())
async def cmd_travel_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddTravelFSM.description)
    await message.answer(
        text=messages.add_travel_texts['description'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(AddTravelFSM.name)
async def cmd_travel_name(message: Message):
    await message.answer(
        text=messages.errors['incorrect_name'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(AddTravelFSM.description)
async def cmd_travel_description_text(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddTravelFSM.address)
    await message.answer(
        text=messages.add_travel_texts['address'],
        reply_markup=Keyboards.location_keyboard()
    )


@router.message(AddTravelFSM.address, F.text, filters.CheckAddress())
async def cmd_travel_address_text(message: Message, state: FSMContext):
    data = await state.get_data()
    address = data['address']
    await state.set_state(AddTravelFSM.check_address)
    await message.answer(
        text=messages.add_travel_texts['set_address'].format(address),
        reply_markup=Keyboards.yes_no_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(AddTravelFSM.address)
async def cmd_travel_address_text_error(message: Message):
    await message.answer(
        text=messages.errors['incorrect_address'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(AddTravelFSM.address, F.location)
async def cmd_travel_location(message: Message, state: FSMContext):
    data = await state.get_data()
    lat, lon = message.location.latitude, message.location.longitude
    user_location = await LocationMethods.get_location_with_lat_lon(lat, lon)
    await state.update_data(
        {
            'country': user_location[0],
            'city': user_location[-1]
        }
    )
    await state.set_state(AddTravelFSM.check_address)
    address = data['address']
    await message.answer(
        text=messages.add_travel_texts['set_address'].format(address),
        reply_markup=Keyboards.yes_no_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(AddTravelFSM.check_address, F.data == 'yes')
async def cmd_travel_start_date(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(AddTravelFSM.start_date)
    await callback.message.edit_text(
        text=messages.add_travel_texts['start_date'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(AddTravelFSM.start_date, filters.ValidStartDate())
async def cmd_travel_end_date(message: Message, state: FSMContext):
    start_date = datetime.strptime(message.text, '%d.%m.%Y %H.%M')
    await state.update_data(start_date=start_date)
    await state.set_state(AddTravelFSM.end_date)
    await message.answer(
        text=messages.add_travel_texts['end_date'],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(AddTravelFSM.end_date, filters.ValidEndDate())
async def cmd_travel_end_date(message: Message, state: FSMContext):
    end_date = datetime.strptime(message.text, '%d.%m.%Y %H.%M')
    await state.update_data(end_date=end_date)
    await state.set_state(AddTravelFSM.check_data)
    data = await state.get_data()
    user = data['user']
    await Database.create_travel(data, user_id=message.from_user.id)
    await message.answer(
        text=messages.add_travel_texts['create_travel'].format(
            user.full_address,
            data['start_date'],
            data['end_date'],
            data['address']
        ),
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True),
        parse_mode=ParseMode.HTML
    )


@router.message(AddTravelFSM.start_date, AddTravelFSM.end_date)
async def cmd_travel_start_date_error(message: Message):
    await message.answer(
        text=messages.errors['incorrect_date'],
        reply_markup=Keyboards.back_keyboard()
    )



