from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject, and_f, StateFilter, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, StartMode
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from custom_filters.filters import StartDialogFilter
from keyboard.keyboards import get_start_keyboard, get_check_note_keyboard
from database.action_data_class import DataInteraction
from states import state_groups as states
from utils.build_ids import get_random_id
from utils.schedulers import del_message
from utils.text_utils import get_age_text
from utils.translator.translator import Translator
from config_data.config import load_config, Config


config: Config = load_config()
user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, command: CommandObject, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    args = command.args
    referral = None
    if args:
        link_ids = await session.get_links()
        ids = [i.link for i in link_ids]
        if args in ids:
            await session.add_admin(msg.from_user.id, msg.from_user.full_name)
            await session.del_link(args)
        if not await session.check_user(msg.from_user.id):
            deeplinks = await session.get_deeplinks()
            deep_list = [i.link for i in deeplinks]
            if args in deep_list:
                await session.add_entry(args)
            try:
                args = int(args)
                users = [user.user_id for user in await session.get_users()]
                if args in users:
                    referral = args
                    await session.add_refs(args)
            except Exception as err:
                print(err)

    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 2)
        except Exception:
            ...
    else:
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await msg.delete()
    if not await session.check_user(msg.from_user.id) or not await session.check_language(msg.from_user.id):
        await session.add_user(user_id=msg.from_user.id,
                               username=msg.from_user.username if msg.from_user.username else '-',
                               name=msg.from_user.full_name, referral=referral)
        await dialog_manager.start(states.languagesSG.start, mode=StartMode.RESET_STACK, data={'start': True})
        return
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(
            text=translator['hello'],
            reply_markup=keyboard
        )
        return
    admin = False
    admins = [user.user_id for user in await session.get_admins()]
    admins.extend(config.bot.admin_ids)
    if msg.from_user.id in admins:
        admin = True
    await msg.answer(
        text=translator['hello'],
        reply_markup=get_start_keyboard(translator, admin)
    )


@user_router.message(StartDialogFilter('profile_button'))
async def start_profile_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.profileSG.start, mode=StartMode.RESET_STACK)


@user_router.message(StartDialogFilter('search_partner_button'))
async def start_search_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.searchSG.start, mode=StartMode.RESET_STACK)


@user_router.message(StartDialogFilter('requests_button'))
async def start_requests_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    print(dialog_manager.has_context())
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception as err:
            print(err)
            ...
    await dialog_manager.start(states.requestsSG.start, mode=StartMode.RESET_STACK)


@user_router.message(StartDialogFilter('balance_button'))
async def start_balance_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.balanceSG.start, mode=StartMode.RESET_STACK)


@user_router.message(StartDialogFilter('info_button'))
async def start_favorites_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.infoSG.start, mode=StartMode.RESET_STACK)


@user_router.message(StartDialogFilter('help_button'))
async def start_help_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.helpSG.start, mode=StartMode.RESET_STACK)


@user_router.message(StartDialogFilter('filter_button'))
async def start_filter_menu_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    user = await session.get_user(msg.from_user.id)
    if not user.vip:
        message = await msg.answer(translator['vip_filter_only_warning'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    await dialog_manager.start(states.searchSG.filter_menu, mode=StartMode.RESET_STACK)



@user_router.message(Command('help'))
async def start_help_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    if not await session.check_form(msg.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await msg.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await msg.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.helpSG.start, mode=StartMode.RESET_STACK)


@user_router.message(F.text == 'Админ панель')
async def start_admin_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction):
    if msg.from_user.id in [user.user_id for user in await session.get_admins()] or msg.from_user.id in config.bot.admin_ids:
        await msg.delete()
        await dialog_manager.start(states.adminSG.start, mode=StartMode.RESET_STACK)


@user_router.callback_query(F.data == 'registration')
async def start_form_dialog(clb: CallbackQuery, dialog_manager: DialogManager, translator: Translator):
    await clb.message.delete()
    await clb.message.answer(
        text=translator['hello']
    )
    await dialog_manager.start(states.formSG.get_name, mode=StartMode.RESET_STACK)


@user_router.callback_query(F.data == 'women_verification')
async def start_women_verification(clb: CallbackQuery, state: FSMContext, translator: Translator):
    await clb.message.delete()
    await state.set_state(states.women_verificationSG.get_video_note)
    await clb.message.answer(translator['women_verification_note'])


@user_router.message(and_f(F.video_note, StateFilter(states.women_verificationSG.get_video_note)))
async def get_verification_note(msg: Message, state: FSMContext, session: DataInteraction, translator: Translator):
    for admin in [6336087289]:
        await msg.bot.copy_message(
            chat_id=admin,
            message_id=msg.message_id,
            from_chat_id=msg.from_user.id
        )
        keyboard = get_check_note_keyboard(msg.from_user.id)
        form = await session.get_form(msg.from_user.id)
        user = await session.get_user(msg.from_user.id)
        text = translator['form'].format(
            name=form.name,
            male=form.male,
            age=form.age,
            age_text=get_age_text(form.age),
            city=form.city,
            profession=form.profession,
            education=form.education,
            income=form.income,
            description=form.description,
            religion=form.religion,
            family=form.family,
            second_wife=translator['second_wife_form_widget'].format(
                second_wife=translator['add_second_wife_yes_button'] if form.second_wife else translator['add_second_wife_no_button']
            ) if isinstance(form.second_wife, int) else '',
            children_count=form.children_count,
            children=form.children,
            leave=form.leave,
            vip='✅' if user.vip else '❌'
        ) + f'\n\nЗаявка на проверку видео сообщения для получения VIP-статуса от пользователя @{msg.from_user.username if msg.from_user.username else "-"}'
        await msg.bot.send_message(
            text=text,
            chat_id=admin,
            reply_markup=keyboard
        )
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.clear()
    await msg.answer(translator['success_get_video_note'])
    admin = False
    admins = [user.user_id for user in await session.get_admins()]
    admins.extend(config.bot.admin_ids)
    if msg.from_user.id in admins:
        admin = True
    await msg.answer(
        text=translator['hello'],
        reply_markup=get_start_keyboard(translator, admin)
    )


@user_router.message(StateFilter(states.women_verificationSG.get_video_note))
async def wrong_verification_message(msg: Message, translator: Translator):
    await msg.answer(translator['wrong_verification_message'])
    await msg.delete()


@user_router.callback_query(F.data == 'confirm_terms')
async def confirm_terms(clb: CallbackQuery, translator: Translator):
    await clb.message.delete()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
    )
    await clb.message.answer(
        text=translator['hello'],
        reply_markup=keyboard
    )


@user_router.callback_query(F.data == 'close_vip_window')
async def close_vip_window(clb: CallbackQuery, session: DataInteraction, translator: Translator):
    await clb.message.delete()
    admin = False
    admins = [user.user_id for user in await session.get_admins()]
    admins.extend(config.bot.admin_ids)
    if clb.from_user.id in admins:
        admin = True
    await clb.message.answer(
        text=translator['hello'],
        reply_markup=get_start_keyboard(translator, admin)
    )


@user_router.callback_query(F.data == 'open_ref_menu')
async def open_ref_menu(clb: CallbackQuery, dialog_manager: DialogManager, session: DataInteraction, translator: Translator):
    if not await session.check_form(clb.from_user.id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['registration_button'], callback_data='registration')]]
        )
        await clb.message.answer(translator['no_form_warning'], reply_markup=keyboard)
        return
    await clb.message.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=clb.message.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(states.profileSG.ref_menu, mode=StartMode.RESET_STACK)
