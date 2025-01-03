from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from lexicon import messages, buttons_texts
from FSMS.FSMS import RegistrationFSM, RegistrationEditFSM
from keyboards.keyboards import Keyboards
from utils.location import LocationMethods
from database.methods import Database
from filters import filters


router = Router()


@router.message(RegistrationFSM.nickname, F.text)
async def cmd_set_age(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await state.set_state(RegistrationFSM.age)
    await message.answer(
        text=messages.registration_texts['age']
    )


@router.message(RegistrationFSM.age, F.text, filters.AgeValid())
async def cmd_set_country_or_get_location(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await state.set_state(RegistrationFSM.description)
    await message.answer(
        text=messages.registration_texts['description']
    )


@router.message(RegistrationFSM.age)
async def error_set_country_or_get_location(message: Message, state: FSMContext):
    await message.answer(
        text=messages.errors['incorrect_age']
    )


@router.message(RegistrationFSM.description, F.text)
async def cmd_set_age(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(RegistrationFSM.country)
    await message.answer(
        text=messages.registration_texts['country_or_location'],
        reply_markup=Keyboards.location_keyboard()
    )


@router.message(RegistrationFSM.description)
async def cmd_set_age(message: Message, state: FSMContext):
    await message.answer(
        text=messages.registration_texts['incorrect_message_type']
    )


@router.message(RegistrationFSM.country, F.location)
async def cmd_set_location(message: Message, state: FSMContext):
    lat, lon = message.location.latitude, message.location.longitude
    user_location = await LocationMethods.get_location_with_lat_lon(lat, lon)
    if isinstance(user_location, str):
        await message.answer(
            text=user_location
        )
    else:
        await state.update_data(
            {
                'country': user_location[0],
                'city': user_location[1],
                'full_address':  user_location[-1]
            }
        )
        await state.set_state(RegistrationFSM.check_data)
        data = await state.get_data()
        await message.answer(
            text=messages.registration_texts['check_data'].format(
                data['nickname'],
                data['age'],
                data['description'],
                data['country'],
                data['city'],
                data['full_address']
        ),
            reply_markup=Keyboards.base_keyboard(buttons_texts.edit_create_profile_data),
            parse_mode=ParseMode.HTML
        )


@router.message(RegistrationFSM.country, F.text, filters.CheckCountry())
async def set_country_with_name(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(RegistrationFSM.city)
    await message.answer(
        text=messages.registration_texts['city'],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(RegistrationFSM.country)
async def error_set_city(message: Message):
    await message.answer(
        text=messages.errors['incorrect_country']
    )


@router.message(RegistrationFSM.city, F.text, filters.CheckCityWithCountry())
async def set_city_with_name(message: Message, state: FSMContext):
    await state.update_data(city=message.text.title())
    data = await state.get_data()
    await state.set_state(RegistrationFSM.check_data)
    await message.answer(
        text=messages.registration_texts['check_data'].format(
            data['nickname'],
            data['age'],
            data['description'],
            data['country'],
            data['city'],
            f"{data['country']}, {data['city']}"
        ),
        reply_markup=Keyboards.base_keyboard(buttons_texts.edit_create_profile_data),
        parse_mode=ParseMode.HTML
    )


@router.message(RegistrationFSM.city)
async def error_set_city(message: Message):
    await message.answer(
        text=messages.errors['incorrect_city']
    )


@router.callback_query(RegistrationFSM.check_data, F.data == 'create')
async def cmd_create_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('update_value'):
        data.pop('update_value')
    if not data.get('full_address'):
        data['full_address'] = f"{data['country']}, {data['city']}"
    await state.clear()
    await Database.create_user(data)
    await callback.message.edit_text(
        text=messages.registration_texts['create_user']
    )


@router.callback_query(RegistrationFSM.check_data, F.data == 'country')
async def cmd_choose_edit_profile_param(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationEditFSM.country_edit)
    await callback.message.answer(
        text=messages.registration_texts['country'],
        reply_markup=Keyboards.location_keyboard()
    )


@router.message(RegistrationEditFSM.country_edit, F.text, filters.CheckCountry())
async def cmd_edit_user_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(RegistrationEditFSM.city_edit_with_country)
    await message.answer(
        text=messages.registration_texts['city']
    )


@router.message(RegistrationEditFSM.country_edit)
async def error_edit_country(message: Message):
    await message.answer(
        text=messages.errors['incorrect_country']
    )


@router.message(RegistrationEditFSM.city_edit_with_country, F.text, filters.CheckCityWithCountry())
async def cmd_edit_user_country_and_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    await state.update_data(full_address=f"{data['country']}, {data['city']}")
    await state.set_state(RegistrationFSM.check_data)
    await message.answer(
        text=messages.registration_texts['check_data'].format(
            data['nickname'],
            data['age'],
            data['description'],
            data['country'],
            data['city'],
            f"{data['country']}, {data['city']}"
        ),
        reply_markup=Keyboards.base_keyboard(buttons_texts.edit_create_profile_data),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(RegistrationFSM.check_data, F.data == 'city')
async def edit_user_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationEditFSM.only_city_edit)
    await callback.message.answer(
        text=messages.my_profile_texts['city'],
        reply_markup=Keyboards.location_keyboard()
    )


@router.message(RegistrationEditFSM.only_city_edit, F.text, filters.CheckEditCityWithoutCountry())
async def edit_user_city(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(full_address=f"{data['country']}, {data['city']}")
    await state.set_state(RegistrationFSM.check_data)
    await message.answer(
        text=messages.registration_texts['check_data'].format(
            data['nickname'],
            data['age'],
            data['description'],
            data['country'],
            data['city'],
            f"{data['country']}, {data['city']}"
        ),
        reply_markup=Keyboards.base_keyboard(buttons_texts.edit_create_profile_data),
        parse_mode=ParseMode.HTML
    )


@router.message(StateFilter(RegistrationEditFSM.only_city_edit, RegistrationEditFSM.city_edit_with_country))
async def error_edit_country(message: Message):
    await message.answer(
        text=messages.errors['incorrect_city']
    )


@router.callback_query(RegistrationFSM.check_data, F.text)
async def cmd_start_edit_data(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationFSM.edit)
    await state.update_data(update_value=callback.data)
    await callback.message.edit_text(
        text=messages.registration_texts[callback.data]
    )


@router.message(RegistrationFSM.edit, F.text, filters.CheckUpdateData())
async def cmd_edit_create_profile_data(message: Message, state: FSMContext):
    data = await state.get_data()
    update_value = data['update_value']
    full_address = data.get('full_address')
    if update_value == 'age':
        data[update_value] = int(message.text)
    else:
        data[update_value] = message.text
    await state.set_state(RegistrationFSM.check_data)
    await message.answer(
        text=messages.registration_texts['check_data'].format(
            data['nickname'],
            data['age'],
            data['description'],
            data['country'],
            data['city'],
            full_address
        ),
        reply_markup=Keyboards.base_keyboard(buttons_texts.edit_create_profile_data),
        parse_mode=ParseMode.HTML
    )


@router.message(RegistrationFSM.edit)
async def error_edit_create_profile_data(message: Message, state: FSMContext):
    update_value = (await state.get_data())['update_value']
    await message.answer(
        text=messages.errors[f'incorrect_{update_value}']
    )
