from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (BotCommand, InlineKeyboardMarkup,
                           InlineKeyboardButton,KeyboardButton, ReplyKeyboardMarkup)
from lexicon import buttons_texts
from database.models import User, Travel, Note


def set_commands() -> list[BotCommand]:
    commands = [
        BotCommand(command=key, description=value)
        for key, value in buttons_texts.set_menu_commands.items()
    ]
    return commands


class Keyboards:
    @staticmethod
    def base_keyboard(
        buttons_data: dict[str | int, str],
        back_buttons: bool = False,
        only_back_to_menu: bool = False
    ) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=value, callback_data=key)]
            for key, value in buttons_data.items()
        ]
        if back_buttons:
            back_buttons = [
                InlineKeyboardButton(text=value, callback_data=key)
                for key, value in buttons_texts.back_buttons.items()
            ]
            if only_back_to_menu:
                buttons.append([back_buttons[-1]])
            else:
                buttons.append(back_buttons)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def yes_no_keyboard(only_yes: bool = False) -> InlineKeyboardMarkup:
        keyboard_builder = InlineKeyboardBuilder()
        buttons = [
            InlineKeyboardButton(text=value, callback_data=key)
            for key, value in buttons_texts.yes_no_buttons.items()
        ]
        back_buttons = [
                InlineKeyboardButton(text=value, callback_data=key)
                for key, value in buttons_texts.back_buttons.items()
        ]
        if only_yes:
            keyboard_builder.row(buttons[0])
        else:
            keyboard_builder.row(*buttons, width=2)
        keyboard_builder.row(*back_buttons, width=2)
        return keyboard_builder.as_markup()

    @staticmethod
    def back_keyboard(only_back_to_menu: bool = False, only_back: bool = False) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=value, callback_data=key)]
            for key, value in buttons_texts.back_buttons.items()
        ]
        if only_back:
            return InlineKeyboardMarkup(inline_keyboard=[buttons[0]])
        if only_back_to_menu:
            return InlineKeyboardMarkup(inline_keyboard=[buttons[-1]])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def add_travel_buttons() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=value, callback_data=key)]
            for key, value in buttons_texts.add_travel_buttons()
        ]
        buttons.append(
            [
                InlineKeyboardButton(text=value, callback_data=key)
                for key, value in buttons_texts.back_buttons.items()
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def check_travel_keyboard() -> InlineKeyboardMarkup:
        keyboard_builder = InlineKeyboardBuilder()
        buttons = [
            InlineKeyboardButton(text=value, callback_data=key)
            for key, value in buttons_texts.travel_buttons.items()
        ]
        back_buttons = [
            InlineKeyboardButton(text=value, callback_data=key)
            for key, value in buttons_texts.back_buttons.items()
        ]
        keyboard_builder.row(*buttons[:-1], width=2)
        keyboard_builder.row(*buttons[-1:], width=1)
        keyboard_builder.row(*back_buttons, width=2)
        return keyboard_builder.as_markup()

    @staticmethod
    def location_keyboard() -> ReplyKeyboardMarkup:
        buttons = [
            [KeyboardButton(text=value, callback_data=key, request_location=True)]
            for key, value in buttons_texts.location_button.items()
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def user_travels_keyboard(travels: list[Travel]) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=travel.name, callback_data=f'travel:{travel.travel_id}')]
            for travel in travels
        ]
        buttons.append([InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def travel_notes_keyboard(notes: list[Note]) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=note.name, callback_data=f'note:{note.id}')]
            for note in notes
        ]
        new_note_button = [
            InlineKeyboardButton(text=value, callback_data=key)
            for key, value in buttons_texts.new_note_button.items()
        ]
        back_buttons = [
            InlineKeyboardButton(text=value, callback_data=key)
            for key, value in buttons_texts.back_buttons.items()
        ]
        buttons.append(new_note_button)
        buttons.append(back_buttons)
        return InlineKeyboardMarkup(inline_keyboard=buttons)
