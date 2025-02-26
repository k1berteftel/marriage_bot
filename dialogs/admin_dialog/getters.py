import datetime
import os

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cachetools import TTLCache

from utils.build_ids import get_random_id
from utils.text_utils import get_age_text
from utils.tables import get_table
from utils.schedulers import send_messages
from utils.translator import Translator as create_translator
from utils.translator.translator import Translator
from database.action_data_class import DataInteraction
from database.model import DeeplinksTable, AdminsTable
from config_data.config import load_config, Config
from states.state_groups import adminSG


invite_params = 'restrict_members+promote_members+manage_chat+invite_users'


async def get_block_user(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        user_data = int(text)
    except Exception:
        if not text.startswith('@'):
            await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте еще раз')
            return
        user_data = text[1::]
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(user_data) if isinstance(user_data, int) else await session.get_user_by_username(user_data)
    if not user:
        await msg.answer('Такого пользователя нет в базе данных, пожалуйста попробуйте еще раз')
        return
    cache: TTLCache = dialog_manager.middleware_data.get('cache')
    translator: Translator = create_translator(user.locale)
    await msg.bot.send_message(
        chat_id=user.user_id,
        text=translator['block_message']
    )
    await session.set_block(user.user_id)
    await session.del_form(user.user_id)
    user = await session.get_user(user.user_id)
    cache[user.user_id] = user
    await dialog_manager.switch_to(adminSG.start)


async def get_users_txt(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    with open('users.txt', 'a+') as file:
        for user in users:
            file.write(f'{user.user_id}\n')
    await clb.message.answer_document(
        document=FSInputFile(path='users.txt')
    )
    try:
        os.remove('users.txt')
    except Exception:
        ...


async def set_vip(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        user_id = int(text)
    except Exception:
        await msg.answer('ID должно быть числом, пожалуйста попробуйте еще раз')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_vip(user_id, vip=True)
    await msg.answer('Вип статус был успешно выдан')


async def del_impression(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    impression_id = dialog_manager.dialog_data.get('impression_id')
    await session.del_impression(impression_id)
    await clb.answer('Модель показов была успешно удаленна')
    await dialog_manager.switch_to(adminSG.choose_impression)


async def impression_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = create_translator('ru')
    impression_id = dialog_manager.dialog_data.get('impression_id')
    impression = await session.get_impression(impression_id)
    users = impression.users
    params = ''
    if impression.male is not None:
        params += f'Пол: '
        for male in impression.male:
            params += f'{translator[male]} '
        params += '\n'
    if impression.min_age is not None:
        params += f'Возраст: {impression.min_age} до {impression.max_age}\n'
    if impression.city is not None:
        params += f'Город: '
        for city in impression.city:
            params += f'{city} '
        params += '\n'
    if impression.profession is not None:
        params += f'Профессия: '
        for profession in impression.profession:
            params += f'{profession} '
        params += '\n'
    if impression.education is not None:
        params += f'Образование: '
        for education in impression.education:
            params += f'{translator[education]} '
        params += '\n'
    if impression.income is not None:
        params += f'Доход: '
        for income in impression.income:
            params += f'{translator[income]} '
        params += '\n'
    if impression.religion is not None:
        params += f'Религия: '
        for religion in impression.religion:
            params += f'{translator[religion]} '
        params += '\n'
    if impression.family is not None:
        params += f'Семейное положение: '
        for family in impression.family:
            params += f'{translator[family]} '
        params += '\n'
    if impression.children_count is not None:
        params += f'Кол-во детей: {impression.children_count if isinstance(impression.children_count, int) else translator[impression.children_count]}\n'
    if impression.children is not None:
        params += f'Отношение по детям: '
        for children in impression.children:
            params += f'{translator[children]} '
        params += '\n'

    shown = 0
    not_shown = 0
    for user in users:
        if user.shown:
            shown += 1
        if not user.shown:
            not_shown += 1
    text = (f'Всего попыток показа: {len(users)}\nИз них прошло фильтрацию и получили сообщение: {shown}\n'
            f'Не получили сообщение: {not_shown}')
    return {
        'params': params,
        'static': text
    }


async def impression_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['impression_id'] = int(item_id)
    await dialog_manager.switch_to(adminSG.impression_menu)


async def choose_impression_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = create_translator('ru')
    impressions = await session.get_impressions()
    buttons = []
    for impression in impressions:
        params = ''
        if impression.male is not None:
            for male in [translator[male] for male in impression.male]:
                params += f'{male}'
            params += '|'
        if impression.min_age is not None:
            params += f'{impression.min_age} до {impression.max_age}|'
        if impression.city is not None:
            for count in range(0, len(impression.city)):
                if count <= 1:
                    params += f'{impression.city[count]}'
                    break

        buttons.append((params[:20:] if params else 'Параметры не определенны', impression.id))
    print(buttons)
    return {'items': buttons}


async def get_impression_keyboard(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        buttons = text.split('\n')
        keyboard: list[list] = [[i.split('-')[0], i.split('-')[1]] for i in buttons]
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['impression_keyboard'] = keyboard

    session: DataInteraction = dialog_manager.middleware_data.get('session')
    male = dialog_manager.dialog_data.get('male')
    age = dialog_manager.dialog_data.get('age')
    city = dialog_manager.dialog_data.get('city')
    profession = dialog_manager.dialog_data.get('profession')
    education = dialog_manager.dialog_data.get('education')
    income = dialog_manager.dialog_data.get('income')
    religion = dialog_manager.dialog_data.get('religion')
    family = dialog_manager.dialog_data.get('family')
    children_count = dialog_manager.dialog_data.get('children_count')
    children = dialog_manager.dialog_data.get('children')
    message = dialog_manager.dialog_data.get('message')
    keyboard = dialog_manager.dialog_data.get('impression_keyboard')
    if male:
        male = [v for i, v in male.items()]
    if city:
        city = [city for city in city]
    if profession:
        profession = [city for city in profession]
    if education:
        education = [v for i, v in education.items()]
    if income:
        income = [v for i, v in income.items()]
    if religion:
        religion = [v for i, v in religion.items()]
    if family:
        family = [v for i, v in family.items()]
    if children:
        children = [v for i, v in children.items()]
    await session.add_impressions_model(
        male=male,
        min_age=age[0] if age else None,
        max_age=age[1] if age else None,
        city=city,
        profession=profession,
        education=education,
        income=income,
        religion=religion,
        family=family,
        children_count=children_count,
        children=children,
        message_id=message[0],
        from_chat_id=message[1],
        keyboard=keyboard
    )
    await msg.answer('Система показов была запущенна')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def get_message(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['message'] = [msg.message_id, msg.chat.id]
    await dialog_manager.switch_to(adminSG.get_impression_keyboard)
    
    
async def get_message_id_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    users = dialog_manager.dialog_data.get('users')
    if not users:
        await clb.answer('К сожалению по таким фильтрам юзеров не найдено, '
                         'чтобы продолжить пожалуйста подберите те фильтры под которые подберется хотя бы пару человек')
        return
    await dialog_manager.switch_to(adminSG.get_message_id)


async def create_impression_model(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    male = dialog_manager.dialog_data.get('male')
    age = dialog_manager.dialog_data.get('age')
    city = dialog_manager.dialog_data.get('city')
    profession = dialog_manager.dialog_data.get('profession')
    education = dialog_manager.dialog_data.get('education')
    income = dialog_manager.dialog_data.get('income')
    religion = dialog_manager.dialog_data.get('religion')
    family = dialog_manager.dialog_data.get('family')
    children_count = dialog_manager.dialog_data.get('children_count')
    children = dialog_manager.dialog_data.get('children')
    message = dialog_manager.dialog_data.get('message')
    if male:
        male = [v for i, v in male.items()]
    if city:
        city = [city for city in city]
    if profession:
        profession = [city for city in profession]
    if education:
        education = [v for i, v in education.items()]
    if income:
        income = [v for i, v in income.items()]
    if religion:
        religion = [v for i, v in religion.items()]
    if family:
        family = [v for i, v in family.items()]
    if children:
        children = [v for i, v in children.items()]
    await session.add_impressions_model(
        male=male,
        min_age=age[0] if age else None,
        max_age=age[1] if age else None,
        city=city,
        profession=profession,
        education=education,
        income=income,
        religion=religion,
        family=family,
        children_count=children_count,
        children=children,
        message_id=message[0],
        from_chat_id=message[1],
        keyboard=None
    )
    await clb.answer('Система показов была запущенна')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def create_impression_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = create_translator('ru')
    male: dict = dialog_manager.dialog_data.get('male')
    age = dialog_manager.dialog_data.get('age')
    city = dialog_manager.dialog_data.get('city')
    profession = dialog_manager.dialog_data.get('profession')
    education = dialog_manager.dialog_data.get('education')
    income = dialog_manager.dialog_data.get('income')
    religion = dialog_manager.dialog_data.get('religion')
    family = dialog_manager.dialog_data.get('family')
    children_count = dialog_manager.dialog_data.get('children_count')
    children = dialog_manager.dialog_data.get('children')

    users = await session.targeting_filter(
        male=male,
        age=age,
        city=city,
        profession=profession,
        education=education,
        income=income,
        religion=religion,
        family=family,
        children_count=children_count,
        children=children
    )
    dialog_manager.dialog_data['users'] = users

    params = ''
    if male is not None:
        params += 'Пол: '
        for i, v in male.items():
            params += f'{translator[v]}, ' if male[i] != v else translator[v]
        params += '\n'
    if age is not None:
        params += f'Возраст: {age[0]} до {age[1]}\n'
    if city is not None:
        params += f'Город: {"".join(f"{i}, " if i != city[-1] else f"{i}" for i in city)}\n'
    if profession is not None:
        params += f'Профессия: {"".join(f"{i}, " if i != profession[-1] else f"{i}" for i in profession)}\n'
    if education is not None:
        params += 'Образование: '
        for i, v in education.items():
            params += f'{translator[v]}, ' if education[i] != v else translator[v]
        params += '\n'
    if income is not None:
        params += 'Доход: '
        for i, v in income.items():
            params += f'{translator[v]}, ' if income[i] != v else translator[v]
        params += '\n'
    if religion is not None:
        params += 'Религия: '
        for i, v in religion.items():
            params += f'{translator[v]}, ' if religion[i] != v else translator[v]
        params += '\n'
    if family is not None:
        params += 'Семейное положение: '
        for i, v in family.items():
            params += f'{translator[v]}, ' if family[i] != v else translator[v]
        params += '\n'
    if children_count is not None:
        params += f'Кол-во детей: {children_count if isinstance(children_count, int) else translator[children_count]}\n'
    if children is not None:
        params += f'Отношение по детям: '
        for i, v in children.items():
            params += f'{translator[v]}, ' if children[i] != v else translator[v]
        params += '\n'

    return {
        'params': params,
        'count': len(users)
    }


async def get_age_range(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await msg.delete()
    try:
        age = [int(i) for i in text.split('-')]
    except Exception:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    if len(age) != 2:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['age'] = age
    await dialog_manager.switch_to(adminSG.create_impression_menu)


async def choose_male(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    males: dict= dialog_manager.dialog_data.get('male')
    gender = clb.data.split('_')[0]
    if not males:
        males = {}
        males[gender] = gender + '_button'
    elif males.get(gender):
        del males[gender]
    else:
        males[gender] = gender + '_button'
    dialog_manager.dialog_data['male'] = males


async def get_male_getter(dialog_manager: DialogManager, **kwargs):
    males = dialog_manager.dialog_data.get('male')
    return {
        'men': '✅' if males and males.get('men') else '❌',
        'women': '✅' if males and males.get('women') else '❌'
    }


async def get_city(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    cities = dialog_manager.dialog_data.get('cities')
    if not cities:
        cities = text.split('\n')
    else:
        cities = cities.extend(text.split('\n'))
    dialog_manager.dialog_data['city'] = cities
    await dialog_manager.switch_to(adminSG.create_impression_menu)


async def get_profession(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    profession = dialog_manager.dialog_data.get('profession')
    if not profession:
        profession = text.split('\n')
    else:
        profession = profession.extend(text.split('\n'))
    dialog_manager.dialog_data['profession'] = profession
    await dialog_manager.switch_to(adminSG.create_impression_menu)


async def choose_education(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    education = dialog_manager.dialog_data.get('education')
    program = clb.data.split('_')[0]
    if not education:
        education = {}
        education[program] = 'add_education_' + clb.data.split('_')[0] + '_button'
    elif education.get(program):
        del education[program]
    else:
        education[program] = 'add_education_' + clb.data.split('_')[0] + '_button'
    dialog_manager.dialog_data['education'] = education


async def get_education_getter(dialog_manager: DialogManager, **kwargs):
    education = dialog_manager.dialog_data.get('education')
    return {
        'leaning': '✅' if education and education.get('leaning') else '❌',
        'eleven': '✅' if education and education.get('eleven') else '❌',
        'average': '✅' if education and education.get('average') else '❌',
        'higher': '✅' if education and education.get('higher') else '❌',
    }


async def choose_income(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    incomes = dialog_manager.dialog_data.get('income')
    income = clb.data.split('_')[0]
    if not incomes:
        incomes = {}
        incomes[income] = 'add_income_' + clb.data.split('_')[0] + '_button'
    elif incomes.get(income):
        del incomes[income]
    else:
        incomes[income] = 'add_income_' + clb.data.split('_')[0] + '_button'
    dialog_manager.dialog_data['income'] = incomes


async def get_income_getter(dialog_manager: DialogManager, **kwargs):
    income = dialog_manager.dialog_data.get('income')
    return {
        'no': '✅' if income and income.get('no') else '❌',
        'low': '✅' if income and income.get('low') else '❌',
        'average': '✅' if income and income.get('average') else '❌',
        'high': '✅' if income and income.get('high') else '❌',
    }


async def choose_religion(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    religions = dialog_manager.dialog_data.get('religion')
    religion = clb.data.split('_')[0]
    if not religions:
        religions = {}
        religions[religion] = 'add_religion_' + clb.data.split('_')[0] + '_button'
    elif religions.get(religion):
        del religions[religion]
    else:
        religions[religion] = 'add_religion_' + clb.data.split('_')[0] + '_button'
    dialog_manager.dialog_data['religion'] = religions


async def get_religion_getter(dialog_manager: DialogManager, **kwargs):
    religion = dialog_manager.dialog_data.get('religion')
    return {
        'christian': '✅' if religion and religion.get('christian') else '❌',
        'islam': '✅' if religion and religion.get('islam') else '❌',
        'another': '✅' if religion and religion.get('another') else '❌',
    }


async def choose_family(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    families = dialog_manager.dialog_data.get('family')
    family = clb.data.split('_')[0]
    if not families:
        families = {}
        families[family] = clb.data.split('_')[0] + '_family_button'
    elif families.get(family):
        del families[family]
    else:
        families[family] = clb.data.split('_')[0] + '_family_button'
    dialog_manager.dialog_data['family'] = families


async def get_family_getter(dialog_manager: DialogManager, **kwargs):
    family = dialog_manager.dialog_data.get('family')
    return {
        'no': '✅' if family and family.get('no') else '❌',
        'divorce': '✅' if family and family.get('divorce') else '❌',
        'widow': '✅' if family and family.get('widow') else '❌',
    }


async def get_children_count(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        children_count = int(text)
    except Exception:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['children_count'] = children_count
    await dialog_manager.switch_to(adminSG.create_impression_menu)


async def choose_children_count(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['children_count'] = 'add_children_count_no_button'
    await dialog_manager.switch_to(adminSG.create_impression_menu)


async def choose_children(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    children = dialog_manager.dialog_data.get('children')
    mode = clb.data.split('_')[0]
    if not children:
        children = {}
        children[mode] = 'add_children_' + mode + '_button'
    elif children.get(mode):
        del children[mode]
    else:
        children[mode] = 'add_children_' + mode + '_button'
    dialog_manager.dialog_data['children'] = children


async def get_children_getter(dialog_manager: DialogManager, **kwargs):
    children = dialog_manager.dialog_data.get('children')
    return {
        'yes': '✅' if children and children.get('yes') else '❌',
        'no': '✅' if children and children.get('no') else '❌',
        'maybe': '✅' if children and children.get('maybe') else '❌',
        'not': '✅' if children and children.get('not') else '❌',
    }


async def throw_off(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    datas = clb.data.split('_')
    if datas[0] == 'children' and datas[1] == 'count':
        dialog_manager.dialog_data['children_count'] = None
        await dialog_manager.switch_to(adminSG.create_impression_menu)
        return
    dialog_manager.dialog_data[datas[0]] = None
    await dialog_manager.switch_to(adminSG.create_impression_menu)


async def block_user(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    cache: TTLCache = dialog_manager.middleware_data.get('cache')
    complains = await session.get_complains()
    page = dialog_manager.dialog_data.get('page')
    complain = complains[page]
    user = await session.get_user(complain.form_user_id)
    translator: Translator = create_translator(user.locale)
    await clb.bot.send_message(
        chat_id=user.user_id,
        text=translator['block_message']
    )

    await session.set_block(user.user_id)
    await session.del_form(user.user_id)
    await session.del_complain(complain.id)
    user = await session.get_user(complain.form_user_id)
    cache[user.user_id] = user


async def del_complain(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    complains = await session.get_complains()
    page = dialog_manager.dialog_data.get('page')
    complain = complains[page]
    await session.del_complain(complain.id)
    await clb.answer('Жалоба была успешно удаленна')


async def get_warning(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    complains = await session.get_complains()
    page = dialog_manager.dialog_data.get('page')
    complain = complains[page]
    user = await session.get_user(complain.form_user_id)
    translator: Translator = create_translator(user.locale)
    await msg.bot.send_message(
        chat_id=user.user_id,
        text=translator['warning_message'] + text
    )
    await msg.answer('Предупреждение было успешно отправленно')
    await session.del_complain(complain.id)
    await dialog_manager.switch_to(adminSG.complain_menu)


async def complain_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    complains = await session.get_complains()
    page = dialog_manager.dialog_data.get('page')
    if page is None:
        page = 0
        dialog_manager.dialog_data['page'] = page
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if len(complains) - 1 <= page:
        not_last = False
    complain = True
    if complains:
        form = await session.get_form(complains[page].form_user_id)
        user = await session.get_user(form.user_id)
        media = None
        if form.photos:
            photo = MediaId(file_id=form.photos.split(' ')[0])
            media = MediaAttachment(file_id=photo, type=ContentType.PHOTO)
        text = translator['form'].format(
                name=form.name,
                age=form.age,
                male=form.male,
                age_text=get_age_text(form.age),
                city=form.city,
                profession=form.profession,
                education=form.education,
                income=form.income,
                description=form.description,
                religion=form.religion,
                family=form.family,
                children_count=form.children_count,
                children=form.children,
                leave=form.leave,
                vip='✅' if user.vip else '❌'
            )
    else:
        complain = False
        media = None
        text = 'Пока жалоб не поступало'
    return {
        'media': media,
        'text': text,
        'complain_text': complains[page].complain if complain else '',
        'not_first': not_first,
        'not_last': not_last,
        'complain': complain
    }


async def complain_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(adminSG.complain_menu)


async def get_refs_static(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_best_refs()
    refs = []
    for user in users:
        refs.append(
            [
                user.user_id,
                user.username,
                user.refs,
                user.income
            ]
        )
    refs.insert(0, ['ID', 'Юзернейм', 'Рефералов', 'Доход'])
    table = get_table(refs)
    await clb.message.answer_document(
        document=FSInputFile(path=table)
    )
    try:
        os.remove(table)
    except Exception as err:
        print(err)


async def get_static(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    transactions = await session.get_all_transactions()
    active = 0
    entry = {
        'today': 0,
        'yesterday': 0,
        '2_day_ago': 0
    }
    activity = 0
    vips = 0
    men = 0
    women = 0
    tokens_on = []
    tokens_sum = 0
    for user in users:
        if user.active:
            active += 1
        for day in range(0, 3):
            if user.entry.date() == (datetime.datetime.today() - datetime.timedelta(days=day)).date():
                if day == 0:
                    entry['today'] = entry.get('today') + 1
                elif day == 1:
                    entry['yesterday'] = entry.get('yesterday') + 1
                else:
                    entry['2_day_ago'] = entry.get('2_day_ago') + 1
        if user.activity:
            activity += 1
        if user.vip and user.vip_end:
            vips += 1
        form = await session.get_form(user.user_id)
        if form:
            translator: Translator = create_translator(user.locale if user.locale else 'ru')
            if form.male == translator['men_button']:
                men += 1
            if form.male == translator['women_button']:
                women += 1

    sum = 0
    today_sum = 0
    for transaction in transactions:
        if transaction.description == 'Пополнение баланса':
            sum += transaction.sum
            if transaction.create > datetime.datetime.today() - datetime.timedelta(days=1):
                today_sum += transaction.sum
        if transaction.description == 'Покупка токенов':
            tokens_sum += transaction.sum
            if transaction.user_id not in tokens_on:
                tokens_on.append(transaction.user_id)

    forms = await session.get_forms()

    text = (f'<b>Статистика на {datetime.datetime.today().strftime('%d-%m-%Y')}</b>\n\nВсего пользователей: {len(users)}'
            f'\n - Активные пользователи(не заблокировали бота): {active}\n - Пользователей заблокировали '
            f'бота: {len(users) - active}\n - Провзаимодействовали с ботом за последние 24 часа: {activity}\n\n'
            f'<b>Прирост аудитории:</b>\n - За сегодня: +{entry.get("today")}\n - За вчерашний день: +{entry.get("yesterday")}'
            f'\n - Позавчера: + {entry.get("2_day_ago")}\n\n<b>Покупки:</b>\n - Людей купил vip: {vips}\n'
            f' - Сумма пополнений за сегодня: {today_sum}\n - Сумма пополнений за все время: {sum}\n'
            f' - Купили токенов(всего): {tokens_sum}\n - Людей купивших токены: {len(tokens_on)}\n\n'
            f'<b>Анкеты</b>\n - Зарегестрированных анкет: {len(forms)}\n - Мужских анкет: {men}\n - Женских: {women}')
    await clb.message.answer(text=text)


async def deeplink_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links: list[DeeplinksTable] = await session.get_deeplinks()
    text = ''
    for link in links:
        text += f'https://t.me/SR_znakomstva_bot?start={link.link}: {link.entry}\n'  # Получить ссылку на бота и поменять
    return {'links': text}


async def add_deeplink(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_deeplink(get_random_id())
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_deeplink(item_id)
    await clb.answer('Ссылка была успешно удаленна')
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links: list[DeeplinksTable] = await session.get_deeplinks()
    buttons = []
    for link in links:
        buttons.append((f'{link.link}: {link.entry}', link.link))
    return {'items': buttons}


async def del_admin(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_admin(int(item_id))
    await clb.answer('Админ был успешно удален')
    await dialog_manager.switch_to(adminSG.admin_menu)


async def admin_del_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins: list[AdminsTable] = await session.get_admins()
    buttons = []
    for admin in admins:
        buttons.append((admin.name, admin.user_id))
    return {'items': buttons}


async def refresh_url(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id: str = dialog_manager.dialog_data.get('link_id')
    dialog_manager.dialog_data.clear()
    await session.del_link(id)
    await dialog_manager.switch_to(adminSG.admin_add)


async def admin_add_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id = get_random_id()
    dialog_manager.dialog_data['link_id'] = id
    await session.add_link(id)
    return {'id': id}


async def admin_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins: list[AdminsTable] = await session.get_admins()
    text = ''
    for admin in admins:
        text += f'{admin.name}\n'
    return {'admins': text}


async def del_rate(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.del_rate(rate_id)
    await clb.answer('Тариф был успешно удален')
    await dialog_manager.switch_to(adminSG.rate_menu)


async def change_rate_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.set_rate_price(rate_id, int(text))


async def change_rate_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.set_rate_amount(rate_id, int(text))


async def rate_change_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    rate = await session.get_rate(rate_id)
    return {'rate': f'{rate.amount} - {rate.price}'}


async def choose_rate(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['rate_id'] = int(item_id)
    await dialog_manager.switch_to(adminSG.change_rate_menu)


async def rate_choose_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates()
    buttons = []
    for rate in rates:
        buttons.append((f'{rate.amount}-{rate.price}', rate.id))
    return {'items': buttons}


async def get_rate_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        text = int(text)
    except Exception as err:
        await msg.answer('Пожалуйста введите число')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    amount = dialog_manager.dialog_data.get('amount')
    await session.add_rate(amount, int(text))
    dialog_manager.dialog_data.clear()
    await msg.answer('Тариф был успешно добавлен')
    await dialog_manager.switch_to(adminSG.rate_menu)


async def get_rate_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        text = int(text)
    except Exception as err:
        await msg.answer('Пожалуйста введите число')
        return
    dialog_manager.dialog_data['amount'] = int(text)
    await dialog_manager.switch_to(adminSG.add_rate_price)


async def rate_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates()
    text = ''
    count = 0
    for rate in rates:
        text += f'{count}: {rate.amount} - {rate.price}\n'
        count += 1
    return {'rates': text}


async def save_without_link(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.start_data.get('chat_id')
    chat = await bot.get_chat(chat_id)
    await session.add_op(
        chat_id=int(chat_id),
        name=chat.title,
        link=chat.invite_link,
    )
    await clb.answer('Кнопка на ОП была успешно сохранена')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def get_button_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text.split('/')) <= 1:
        await msg.answer('Вы ввели ссылку не в том формате, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    chat_id = dialog_manager.start_data.get('chat_id')
    chat = await bot.get_chat(chat_id)
    await session.add_op(
        chat_id=int(chat_id),
        name=chat.title,
        link=text,
    )
    await msg.answer('Кнопка на ОП была успешно сохранена')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def op_buttons_switcher(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['button'] = int(item_id)
    await dialog_manager.switch_to(adminSG.button_menu)


async def button_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    button = await session.get_op_by_chat_id(chat_id)
    return {
        'channel_name': button.name,
        'channel_link': button.link
    }


async def change_button_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    await session.set_button_link(chat_id, link=text)
    await dialog_manager.switch_to(adminSG.button_menu)


async def op_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channel_link = f't.me/SR_znakomstva_bot?startchannel=works&admin={invite_params}'
    chat_link = f't.me/SR_znakomstva_bot?startgroup=works&admin={invite_params}'
    categories = await session.get_op()
    text = ''
    buttons = []
    count = 1
    for category in categories:
        buttons.append((category.name, category.chat_id))
        text += f'{count}: {category.name} - {category.link}\n'
        count += 1
    return {
        'buttons': text,
        'items': buttons,
        'chat_link': chat_link,
        'channel_link': channel_link
    }


async def get_mail(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['message'] = [msg.message_id, msg.chat.id]
    await dialog_manager.switch_to(adminSG.get_time)


async def get_time(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        times = text.split(':')
        time = datetime.time(hour=int(times[0]), minute=int(times[1]))
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['time'] = [time.hour, time.minute]
    await dialog_manager.switch_to(adminSG.get_keyboard)


async def get_mail_keyboard(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        buttons = text.split('\n')
        keyboard: list[list] = [[i.split('-')[0].strip(), i.split('-')[1].strip()] for i in buttons]
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['keyboard'] = keyboard
    await dialog_manager.switch_to(adminSG.confirm_mail)


async def cancel_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def start_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    time = dialog_manager.dialog_data.get('time')
    message = dialog_manager.dialog_data.get('message')
    keyboard = dialog_manager.dialog_data.get('keyboard')
    if keyboard:
        keyboard = [InlineKeyboardButton(text=i[0], url=i[1]) for i in keyboard]
    users = await session.get_users()
    if not time:
        count = 0
        for user in users:
            try:
                await bot.copy_message(
                    chat_id=user.user_id,
                    from_chat_id=message[1],
                    message_id=message[0],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                )
                if user.active == 0:
                    await session.set_active(user.user_id, 1)
                count += 1
            except Exception as err:
                print(err)
                await session.set_active(user.user_id, 0)
        await clb.answer(f'Рассылка прошла успешно, {count} из {len(users)} получили сообщение')
    else:
        today = datetime.datetime.today()
        date = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=time[0], minute=time[1])
        scheduler.add_job(
            func=send_messages,
            args=[bot, session, InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None, message],
            next_run_time=date
        )
        await clb.answer('Рассылка была успешно отложена')
    await dialog_manager.switch_to(adminSG.start)
