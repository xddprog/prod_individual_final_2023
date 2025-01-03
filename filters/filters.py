from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import BaseFilter
from utils.location import LocationMethods
from utils.routing import RoutingMethods
from lexicon import messages
from database.methods import Database


class CheckCityWithCountry(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        country = (await state.get_data())['country']
        await state.update_data(country=country)
        return await LocationMethods.get_city(message.text.title(), country)


class CheckCountry(BaseFilter):
    async def __call__(self, message: Message):
        print(message)
        return await LocationMethods.get_country(message.text.title())


class CheckUpdateData(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        data = await state.get_data()
        update_value = data['update_value']
        if update_value == 'age':
            check = message.text.isdigit()
            if not check:
                return False
            else:
                data[update_value] = int(message.text)
        elif update_value == 'city':
            check = await LocationMethods.get_city(message.text.title(), data['country'])
            if not check:
                return False
        elif update_value == 'country':
            check = await LocationMethods.get_country(message.text)
            if not check:
                return False
        return True


class CheckExistsUser(BaseFilter):
    async def __call__(self, message: Message):
        return not await Database.get_user(message.from_user.id)


class AgeValid(BaseFilter):
    async def __call__(self, message: Message):
        return message.text.isdigit() and 14 <= int(message.text) <= 100


class NicknameValid(BaseFilter):
    async def __call__(self, message: Message):
        return 2 <= len(message.text) <= 50


class CheckEditCityWithoutCountry(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        country = await LocationMethods.get_country_with_city(message.text.title())
        if not country:
            return False
        await state.update_data(country=country)
        return True


class CheckAddress(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        if message.location:
            address = await LocationMethods.get_location_with_lat_lon(
                message.location.latitude,
                message.location.latitude
            )
            if isinstance(address, str):
                return False
            await state.update_data(address=address[-1])
            return True
        address = await RoutingMethods.get_lat_lon_with_address(message.text.title())
        if not address:
            return False
        address = await LocationMethods.get_location_with_lat_lon(address[0], address[-1])
        if isinstance(address, str):
            return False
        await state.update_data(address=address[-1])
        return True


class ValidStartDate(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return True


class ValidEndDate(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return True
