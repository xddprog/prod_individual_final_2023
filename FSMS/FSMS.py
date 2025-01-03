from aiogram.fsm.state import State, StatesGroup


class RegistrationFSM(StatesGroup):
    nickname = State()
    age = State()
    description = State()
    country = State()
    city = State()
    check_data = State()
    edit = State()


class RegistrationEditFSM(StatesGroup):
    country_edit = State()
    city_edit_with_country = State()
    only_city_edit = State()
    age_edit = State()
    nickname_edit = State()
    set_edit_value = State()


class ProfileEditFSM(StatesGroup):
    choose_edit_param = State()
    country_edit = State()
    city_edit_with_country = State()
    only_city_edit = State()
    age_edit = State()
    nickname_edit = State()
    set_edit_value = State()


class AddTravelFSM(StatesGroup):
    mode = State()
    start_travel_date = State()
    name = State()
    description = State()
    address = State()
    check_address = State()
    start_date = State()
    end_date = State()
    check_data = State()


class CheckTravelsFSM(StatesGroup):
    choose_travel = State()
    travel_info = State()
    delete_or_not = State()
    check_map = State()


class CreateNoteFSM(StatesGroup):
    is_private = State()
    name = State()
    description = State()
    file = State()
    check_note_info = State()


class NotesFSM(StatesGroup):
    check_all_notes = State()
    check_note = State()
    delete_note = State()


class NoteEditFSM(StatesGroup):
    choose_edit_param = State()
    edit_name = State()
    edit_privacy = State()
    edit_file = State()
    edit_description = State()
    accept_edit = State()