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

