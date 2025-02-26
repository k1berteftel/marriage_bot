from aiogram.fsm.state import State, StatesGroup


class subSG(StatesGroup):
    start = State()


class languagesSG(StatesGroup):
    start = State()
    start_form = State()


class helpSG(StatesGroup):
    start = State()


class infoSG(StatesGroup):
    start = State()
    rules = State()
    info = State()


class requestsSG(StatesGroup):
    start = State()
    my_requests = State()
    alien_requests = State()
    my_request_complain = State()
    alien_request_complain = State()


class searchSG(StatesGroup):
    start = State()
    filter_menu = State()
    get_city = State()
    get_age= State()
    get_family = State()
    get_children = State()
    get_religion = State()
    search_menu = State()
    get_complain = State()


class balanceSG(StatesGroup):
    start = State()
    payment_menu = State()
    tokens_confirm = State()
    balance_menu = State()
    balance_fill = State()
    balance_derive = State()
    choose_payment_menu = State()
    card_payment = State()
    crypto_payment = State()
    vip_menu = State()
    vip_choose = State()
    history_menu = State()


class profileSG(StatesGroup):
    start = State()
    ref_menu = State()
    ref_static = State()
    form_menu = State()
    redact_menu = State()
    get_name = State()
    get_age = State()
    get_male = State()
    get_city = State()
    get_profession = State()
    get_education = State()
    get_income = State()
    get_description = State()
    get_religion = State()
    get_second_wife = State()
    get_family = State()
    get_children_count = State()
    get_children = State()
    get_photo_1 = State()
    get_photo_2 = State()
    get_photo_3 = State()
    get_leave = State()
    language_menu = State()


class formSG(StatesGroup):
    get_name = State()
    get_age = State()
    get_male = State()
    get_city = State()
    get_profession = State()
    get_education = State()
    get_income = State()
    get_description = State()
    get_religion = State()
    get_second_wife = State()
    get_family = State()
    get_children_count = State()
    get_children = State()
    get_leave = State()
    get_photo_1 = State()
    get_photo_2 = State()
    get_photo_3 = State()
    check_form = State()


class adminSG(StatesGroup):
    op_menu = State()
    get_button_link = State()
    button_menu = State()
    change_button_text = State()
    change_button_link = State()
    start = State()
    get_keyboard = State()
    get_mail = State()
    get_time = State()
    confirm_mail = State()
    deeplink_menu = State()
    deeplink_del = State()
    admin_menu = State()
    admin_del = State()
    admin_add = State()
    check_photos = State()
    complain_menu = State()
    get_warning = State()
    target_menu = State()
    create_impression_menu = State()
    mailing_menu = State()
    get_male = State()
    get_age_range = State()
    get_city = State()
    get_profession = State()
    get_education = State()
    get_income = State()
    get_religion = State()
    get_family = State()
    get_children_count = State()
    get_children = State()
    get_message_id = State()
    get_impression_keyboard = State()
    choose_impression = State()
    impression_menu = State()
    rate_menu = State()
    add_rate_amount = State()
    add_rate_price = State()
    choose_rate = State()
    change_rate_menu = State()
    change_rate_amount = State()
    change_rate_price = State()
    set_vip = State()
    block_user = State()


class targetingSG(StatesGroup):
    menu = State()
    get_male = State()
    get_age_range = State()
    get_city = State()
    get_profession = State()
    get_education = State()
    get_income = State()
    get_religion = State()
    get_family = State()
    get_children_count = State()
    get_children = State()
    get_keyboard = State()
    get_mail = State()
    get_time = State()
    confirm_mail = State()


class women_verificationSG(StatesGroup):
    get_video_note = State()