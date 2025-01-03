from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from datetime import datetime

from lexicon import messages, buttons_texts
from keyboards.keyboards import Keyboards
from utils.routing import RoutingMethods
from database.methods import Database
from filters import filters
from FSMS.FSMS import CheckTravelsFSM, CreateNoteFSM, NotesFSM, NoteEditFSM


router = Router()


@router.callback_query(NotesFSM.check_all_notes, F.data == 'new_note')
async def cmd_create_new_note(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(CreateNoteFSM.is_private)
    await callback.message.edit_text(
        text=messages.create_note_texts['is_private'],
        reply_markup=Keyboards.base_keyboard(buttons_data=buttons_texts.is_private_buttons, back_buttons=True)
    )


@router.callback_query(CreateNoteFSM.is_private)
async def cmd_set_note_privacy(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(is_private=callback.data)
    await state.set_state(CreateNoteFSM.name)
    await callback.message.edit_text(
        text=messages.create_note_texts['name'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(CreateNoteFSM.name, F.text, filters.NicknameValid())
async def cmd_set_note_name(message: Message, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(message=message, state=state)
    await state.set_state(CreateNoteFSM.description)
    await state.update_data(name=message.text)
    await message.answer(
        text=messages.create_note_texts['description'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(CreateNoteFSM.name)
async def cmd_travel_name(message: Message):
    await message.answer(
        text=messages.errors['incorrect_note_name'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(CreateNoteFSM.description, F.text)
async def cmd_set_note_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(message=message, state=state)
    if data.get('file'):
        await state.set_state(CreateNoteFSM.check_note_info)
        await state.update_data(content_type='photo')
        await message.answer_photo(
            photo=data['file'],
            caption=messages.create_note_texts['check_note_info'].format(
                data['name'],
                'нет' if not data['is_private'] == 'not_private' else 'да',
                data['description']
            ),
            reply_markup=Keyboards.base_keyboard(buttons_texts.create_note_button, back_buttons=True),
            parse_mode=ParseMode.HTML
        )
    else:
        await state.set_state(CreateNoteFSM.file)
        await message.answer(
            text=messages.create_note_texts['file'],
            reply_markup=Keyboards.back_keyboard()
        )


@router.message(CreateNoteFSM.file, F.audio | F.photo | F.video | F.document)
async def cmd_get_note_file(message: Message, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(message=message, state=state)
    await state.set_state(CreateNoteFSM.check_note_info)
    if message.audio:
        audio_id = message.audio.file_id
        await message.answer_audio(
            audio_id=audio_id,
            caption=messages.create_note_texts['check_note_info'].format(
                data['name'],
                data['user'].nickname,
                data['description']
            ),
            reply_markup=Keyboards.base_keyboard(buttons_texts.create_note_button, back_buttons=True),
            parse_mode=ParseMode.HTML
        )
        await state.update_data(file=audio_id, content_type='audio')
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await message.answer_photo(
            photo=photo_id,
            caption=messages.create_note_texts['check_note_info'].format(
                data['name'],
                data['user'].nickname,
                data['description']
            ),
            reply_markup=Keyboards.base_keyboard(buttons_texts.create_note_button, back_buttons=True),
            parse_mode=ParseMode.HTML
        )
        await state.update_data(file=photo_id, content_type='photo')
    elif message.video:
        video_id = message.video.file_id
        await message.answer_video(
            video=video_id,
            caption=messages.create_note_texts['check_note_info'].format(
                data['name'],
                data['user'].nickname,
                data['description']
            ),
            reply_markup=Keyboards.base_keyboard(buttons_texts.create_note_button, back_buttons=True),
            parse_mode=ParseMode.HTML
        )
        await state.update_data(file=video_id, content_type='video')
    elif message.document:
        document_id = message.document.file_id
        await message.answer_document(
            document=document_id,
            caption=messages.create_note_texts['check_note_info'].format(
                data['name'],
                data['user'].nickname,
                data['description']
            ),
            reply_markup=Keyboards.base_keyboard(buttons_texts.create_note_button, back_buttons=True),
            parse_mode=ParseMode.HTML
        )
        await state.update_data(file=document_id,content_type='document')


@router.message(CreateNoteFSM.file)
async def cmd_error_file_type(message: Message):
    await message.answer(
        text=messages.errors['incorrect_file_type']
    )


@router.callback_query(CreateNoteFSM.check_note_info, F.data == 'create_note')
async def cmd_create_note(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await Database.create_travel_note(
        data['travel'].travel_id,
        callback.from_user.id,
        data['user'].nickname,
        True if data['is_private'] == 'private' else False,
        data['name'],
        data['description'],
        data['file'],
        data['content_type']
    )
    await callback.message.answer(
        text=messages.create_note_texts['created'],
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(CheckTravelsFSM.travel_info, F.data == 'travel_notes')
async def cmd_check_travel_notes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    travel = data['travel']
    notes = [
        note for note in travel.notes
        if note.is_private or note.author_id == callback.from_user.id
    ]
    await pages.update_states(callback=callback, state=state)
    await state.update_data(notes=notes)
    await state.set_state(NotesFSM.check_all_notes)
    await callback.message.edit_text(
        text=messages.check_travels_texts['check_all_notes'].format(
            len(notes)
        ),
        reply_markup=Keyboards.travel_notes_keyboard(travel.notes),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(NotesFSM.check_all_notes, F.data.startswith('note'))
async def check_note(callback: CallbackQuery, state: FSMContext, bot: Bot):
    note_id = callback.data.split(':')[-1]
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(NotesFSM.check_note)
    note = await Database.get_note(int(note_id))
    await state.update_data(note_id=note_id)
    if note.content_type == 'photo':
        await callback.message.answer_photo(
            photo=note.file_id,
            caption=messages.check_travels_texts['check_note_info'].format(
                note.name,
                note.author_name,
                note.description
            ),
            reply_markup=Keyboards.base_keyboard(
                buttons_texts.check_note_buttons,
                back_buttons=True,
                only_back_to_menu=True
            ),
            parse_mode=ParseMode.HTML
        )
    elif note.content_type == 'audio':
        await callback.message.answer_audio(
            photo=note.file_id,
            caption=messages.check_travels_texts['check_note_info'].format(
                note.name,
                note.author_name,
                note.description
            ),
            reply_markup=Keyboards.base_keyboard(
                buttons_texts.check_note_buttons,
                back_buttons=True,
                only_back_to_menu=True
            ),
            parse_mode=ParseMode.HTML
        )
    elif note.content_type == 'video':
        await callback.message.answer_video(
            photo=note.file_id,
            caption=messages.check_travels_texts['check_note_info'].format(
                note.name,
                note.author_name,
                note.description
            ),
            reply_markup=Keyboards.base_keyboard(
                buttons_texts.check_note_buttons,
                back_buttons=True,
                only_back_to_menu=True
            ),
            parse_mode=ParseMode.HTML
        )
    elif note.content_type == 'document':
        await callback.message.answer_document(
            document=note.file_id,
            caption=messages.check_travels_texts['check_note_info'].format(
                note.name,
                note.author_name,
                note.description
            ),
            reply_markup=Keyboards.base_keyboard(
                buttons_texts.check_note_buttons,
                back_buttons=True,
                only_back_to_menu=True
            ),
            parse_mode=ParseMode.HTML
        )
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(NotesFSM.check_note, F.data == 'delete_note')
async def cmd_delete_note(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(NotesFSM.delete_note)
    await callback.message.answer(
        text=messages.check_note_texts['delete_note'],
        reply_markup=Keyboards.yes_no_keyboard(only_yes=True)
    )
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(NotesFSM.delete_note, F.data == 'yes')
async def cmd_delete_note_successfully(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await Database.delete_note(int(data['note_id']))
    await callback.message.edit_text(
        text=messages.check_note_texts['delete_successfully'],
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )


@router.callback_query(NotesFSM.check_note, F.data == 'edit_note')
async def cmd_delete_note(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.set_state(NoteEditFSM.choose_edit_param)
    await callback.message.answer(
        text=messages.check_note_texts['edit_note_param'],
        reply_markup=Keyboards.base_keyboard(
            buttons_texts.edit_note_texts,
            back_buttons=True,
            only_back_to_menu=True
        )
    )
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(NoteEditFSM.choose_edit_param, F.data == 'is_private')
async def cmd_edit_note_privacy(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(update_param=callback.data)
    await state.set_state(NoteEditFSM.edit_privacy)
    await callback.message.edit_text(
        text=messages.create_note_texts['is_private'],
        reply_markup=Keyboards.base_keyboard(
            buttons_data=buttons_texts.is_private_buttons,
            back_buttons=True
        )
    )


@router.callback_query(NoteEditFSM.edit_privacy)
async def cmd_edit_note_privacy_accept(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(update_value=callback.data)
    await state.set_state(NoteEditFSM.accept_edit)
    await callback.message.edit_text(
        text=messages.check_note_texts['accept_edit'],
        reply_markup=Keyboards.yes_no_keyboard(only_yes=True)
    )


@router.callback_query(NoteEditFSM.choose_edit_param, F.data == 'name')
async def cmd_edit_note_name(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(update_param=callback.data)
    await state.set_state(NoteEditFSM.edit_name)
    await callback.message.edit_text(
        text=messages.create_note_texts[callback.data],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(NoteEditFSM.edit_name, F.text, filters.NicknameValid())
async def cmd_edit_note_name_accept(message: Message, state: FSMContext):
    await state.update_data(update_value=message.text)
    await state.set_state(NoteEditFSM.accept_edit)
    await message.answer(
        text=messages.check_note_texts['accept_edit'],
        reply_markup=Keyboards.yes_no_keyboard(only_yes=True)
    )


@router.message(NoteEditFSM.edit_name)
async def error_edit_name(message: Message):
    await message.answer(
        text=messages.errors['incorrect_note_name']
    )


@router.callback_query(NoteEditFSM.choose_edit_param, F.data == 'description')
async def cmd_edit_note_description(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(update_param=callback.data)
    await state.set_state(NoteEditFSM.edit_description)
    await callback.message.edit_text(
        text=messages.create_note_texts[callback.data],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(NoteEditFSM.edit_description, F.text)
async def cmd_edit_note_description_accept(message: Message, state: FSMContext):
    await state.update_data(update_value=message.text)
    await state.set_state(NoteEditFSM.accept_edit)
    await message.answer(
        text=messages.check_note_texts['accept_edit'],
        reply_markup=Keyboards.yes_no_keyboard(only_yes=True)
    )


@router.message(NoteEditFSM.edit_description)
async def error_edit_name(message: Message):
    await message.answer(
        text=messages.errors['incorrect_description']
    )


@router.callback_query(NoteEditFSM.choose_edit_param, F.data == 'file_id')
async def cmd_edit_note_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data['pages']
    await pages.update_states(callback=callback, state=state)
    await state.update_data(update_param=callback.data)
    await state.set_state(NoteEditFSM.edit_file)
    await callback.message.edit_text(
        text=messages.create_note_texts['file'],
        reply_markup=Keyboards.back_keyboard()
    )


@router.message(NoteEditFSM.edit_file, F.audio | F.photo | F.video | F.document)
async def cmd_edit_note_file_accept(message: Message, state: FSMContext):
    await state.set_state(NoteEditFSM.accept_edit)
    if message.audio:
        audio_id = message.audio.file_id
        await state.update_data(update_value=audio_id, update_param='audio')
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(update_value=photo_id, update_param='photo')
    elif message.video:
        video_id = message.video.file_id
        await state.update_data(update_value=video_id, update_param='video')
    elif message.document:
        document_id = message.document.file_id
        await state.update_data(update_value=document_id, update_param='document')
    await message.answer(
        text=messages.check_note_texts['accept_edit'],
        reply_markup=Keyboards.yes_no_keyboard(only_yes=True)
    )


@router.callback_query(NoteEditFSM.accept_edit, F.data == 'yes')
async def cmd_edit_note_successfully(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    update_param = data['update_param']
    update_value = data['update_value']
    note_id = int(data['note_id'])
    if update_param in ['is_private', 'description', 'name']:
        await Database.update_note(
            note_id,
            update_param=update_param,
            update_value=update_value
        )
    else:
        await Database.update_note(
            note_id,
            content_type=update_param,
            file_id=update_value
        )
    await callback.message.edit_text(
        text=messages.check_note_texts['update_successfully'],
        reply_markup=Keyboards.back_keyboard(only_back_to_menu=True)
    )
