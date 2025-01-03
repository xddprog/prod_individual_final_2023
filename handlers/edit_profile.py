from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from lexicon import messages, buttons_texts
from FSMS.FSMS import RegistrationFSM, ProfileEditFSM
from keyboards.keyboards import Keyboards
from utils.location import LocationMethods
from database.methods import Database
from filters import filters


router = Router()


@router.callback_query(F.data == 'edit_profile')
async def cmd_choose_edit_profile_param(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(ProfileEditFSM.choose_edit_param)
    await callback.message.edit_text(
        text=messages.my_profile_texts['edit'],
        reply_markup=Keyboards.base_keyboard(
            buttons_data=buttons_texts.edit_profile_data,
            back_buttons=True,
            only_back_to_menu=True
        )
    )


@router.callback_query(ProfileEditFSM.choose_edit_param, F.data == 'country')
async def cmd_choose_edit_profile_param(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(ProfileEditFSM.country_edit)
    await callback.message.edit_text(
        text=messages.my_profile_texts['country'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(ProfileEditFSM.country_edit, filters.CheckCountry())
async def cmd_edit_user_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text.title())
    await state.set_state(ProfileEditFSM.city_edit_with_country)
    await message.answer(
        text=messages.my_profile_texts['city'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(ProfileEditFSM.country_edit)
async def error_edit_country(message: Message):
    await message.answer(
        text=messages.errors['incorrect_country'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(ProfileEditFSM.city_edit_with_country, filters.CheckCityWithCountry())
async def cmd_edit_user_country_and_city(message: Message, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(message=message, state=state)
    data = await state.get_data()
    await Database.update_user_profile(
        message.from_user.id,
        country=data['country'],
        city=message.text,
        full_address=f"{data['country']}, {message.text}"
    )
    await message.answer(
        text=messages.my_profile_texts['edit_successfully'].format(
            'город и страну',
            f'{message.text} и {data["country"]}'
        ),
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )


@router.callback_query(ProfileEditFSM.choose_edit_param, F.data == 'city')
async def edit_user_city(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(ProfileEditFSM.only_city_edit)
    await callback.message.edit_text(
        text=messages.my_profile_texts['city'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(ProfileEditFSM.only_city_edit, filters.CheckEditCityWithoutCountry())
async def edit_user_city(message: Message, state: FSMContext):
    data = await state.get_data()
    country = data['country']
    full_address = data.get('full_address')
    await Database.update_user_profile(
        message.from_user.id,
        country=country,
        city=message.text,
        full_address=full_address if full_address else f"{data['country']}, {message.text}"
    )
    await message.answer(
        text=messages.my_profile_texts['edit_successfully'].format(
            'город и страну',
            f'"{message.text}" и "{country}"'
        ),
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )


@router.message(StateFilter(ProfileEditFSM.country_edit, ProfileEditFSM.city_edit_with_country), F.location)
async def cmd_edit_user_location(message: Message, state: FSMContext):
    lat, lon = message.location.latitude, message.location.longitude
    user_location = await LocationMethods.get_location_with_lat_lon(lat, lon)
    if isinstance(user_location, str):
        await message.answer(
            text=user_location
        )
    else:
        await Database.update_user_profile(
            message.from_user.id,
            country=user_location[0],
            city=user_location[1],
            full_address=user_location[-1]
        )
        await message.answer(
            text=messages.my_profile_texts['edit_successfully'].format(
                'город и страну',
                f'{user_location[-1]} и {user_location[0]}'
            ),
            reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
        )


@router.message(StateFilter(ProfileEditFSM.only_city_edit, ProfileEditFSM.city_edit_with_country))
async def error_edit_country(message: Message):
    await message.answer(
        text=messages.errors['incorrect_city'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.callback_query(ProfileEditFSM.choose_edit_param, F.data == 'age')
async def cmd_set_edit_user_age(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(ProfileEditFSM.age_edit)
    await callback.message.edit_text(
        text=messages.my_profile_texts['age'],
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )


@router.message(ProfileEditFSM.age_edit, filters.AgeValid())
async def cmd_edit_user_age(message: Message, state: FSMContext):
    await Database.update_user_profile(message.from_user.id, age=int(message.text))
    await message.answer(
        text=messages.my_profile_texts['edit_successfully'].format(
            'возраст',
            message.text
        ),
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )


@router.message(ProfileEditFSM.age_edit)
async def cmd_edit_user_age_error(message: Message):
    await message.answer(
        text=messages.errors['incorrect_age'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.callback_query(ProfileEditFSM.choose_edit_param, F.data == 'nickname')
async def cmd_set_edit_user_age(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(ProfileEditFSM.nickname_edit)
    await callback.message.edit_text(
        text=messages.my_profile_texts['nickname'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(ProfileEditFSM.nickname_edit, filters.NicknameValid())
async def cmd_edit_user_age(message: Message, state: FSMContext):
    await Database.update_user_profile(message.from_user.id, nickname=message.text)
    await message.answer(
        text=messages.my_profile_texts['edit_successfully'].format(
            'Имя',
            message.text
        ),
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(ProfileEditFSM.nickname_edit)
async def cmd_edit_user_age_error(message: Message):
    await message.answer(
        text=messages.errors['incorrect_nickname'],
        reply_markup=Keyboards.back_keyboard()
    )


