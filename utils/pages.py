from dataclasses import dataclass
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery
from lexicon.messages import my_profile_texts
from lexicon.buttons_texts import profile_buttons
from keyboards.keyboards import Keyboards
from aiogram.fsm.state import default_state


@dataclass
class Page:
    text: str
    reply_markup: InlineKeyboardMarkup
    state: str


class Pages:
    def __init__(self):
        self.pages: list[Page] = []
        self.menu_page = Page(
            text=my_profile_texts['check_profile'],
            reply_markup=Keyboards.base_keyboard(profile_buttons),
            state=default_state
        )

    async def update_states(
        self,
        state: FSMContext,
        message: Message = None,
        callback: CallbackQuery = None,
    ) -> None:
        if message:
            page = Page(
                text=message.text,
                reply_markup=message.reply_markup,
                state=await state.get_state()
            )
        if callback:
            page = Page(
                text=callback.message.text,
                reply_markup=callback.message.reply_markup,
                state=await state.get_state()
            )
        self.pages.append(page)

    async def get_prev_page(self) -> Page:
        return self.pages.pop(-1)

    async def get_menu_page(self) -> Page:
        self.pages = []
        return self.menu_page
