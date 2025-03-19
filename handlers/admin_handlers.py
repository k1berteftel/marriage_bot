from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter, and_f
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from aiogram_dialog import DialogManager, StartMode
from cachetools import TTLCache

from keyboard.keyboards import get_search_keyboard
from utils.text_utils import get_age_text
from database.action_data_class import DataInteraction
from config_data.config import Config, load_config
from states.state_groups import adminSG, warningSG
from utils.translator.translator import Translator
from utils.translator import Translator as create_translator


config: Config = load_config()
admin_router = Router()


@admin_router.callback_query(F.data.startswith('photos'))
async def confirm_photo(clb: CallbackQuery, session: DataInteraction, translator: Translator):
    user_id = int(clb.data.split('|')[1])
    application = await session.get_application(user_id)
    await session.update_photos(
        user_id=application.user_id,
        photos=application.photos
    )
    await session.del_application(user_id)
    await clb.message.delete()
    try:
        for msg_id in application.message_ids:
            await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=msg_id)
    except Exception as err:
        ...


@admin_router.callback_query(F.data.startswith('revoke'))
async def revoke_messages(clb: CallbackQuery, session: DataInteraction, translator: Translator):
    user_id = int(clb.data.split('|')[1])
    application = await session.get_application(user_id)
    await session.del_application(user_id)
    await clb.message.delete()
    try:
        for msg_id in application.message_ids:
            await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=msg_id)
    except Exception as err:
        ...
    await clb.bot.send_message(
        chat_id=user_id,
        text=translator['photos_warning_message']
    )


@admin_router.callback_query(F.data.startswith('send_warning'))
async def send_warning(clb: CallbackQuery, session: DataInteraction, translator: Translator, state: FSMContext):
    user_id = int(clb.data.split('|')[1])
    await state.set_state(warningSG.get_warning)
    await state.update_data(user_id=user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='close_get_warning')]])
    await clb.message.answer('Отправьте сообщение которое отобразиться пользователю', reply_markup=keyboard)


@admin_router.message(and_f(F.text, StateFilter(warningSG.get_warning)))
async def get_warning(msg: Message, session: DataInteraction, translator: Translator, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    application = await session.get_application(user_id)
    await session.del_application(user_id)
    try:
        for msg_id in application.message_ids:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg_id)
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=application.message_ids[-1] + 1)
    except Exception as err:
        ...
    await session.del_form(user_id)
    try:
        await msg.bot.send_message(chat_id=user_id, text=translator['again_create_warning'] + msg.text)
    except Exception:
        await session.set_active(user_id, 0)
    await state.clear()


@admin_router.callback_query(F.data.startswith('derive'))
async def derive_user_balance(clb: CallbackQuery, session: DataInteraction):
    data = clb.data.split('_')
    user_id = int(data[1])
    amount = int(data[2])
    await session.update_balance(user_id, -amount)
    await session.add_transaction(user_id, -amount, 'Вывод средств с баланса')
    await clb.answer('Баланс пользователя был успешно понижен')
    await clb.message.delete()


#  Добавление каналов на ОП


def get_chat_add_keyboard(chat_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить', callback_data=f'add_opchannel_{chat_id}')],
            [InlineKeyboardButton(text='Игнорировать', callback_data='decline')]
        ]
    )
    return keyboard


@admin_router.my_chat_member()
async def new_chat_member(req: ChatMemberUpdated, session: DataInteraction, dialog_manager: DialogManager):
    if req.chat.type not in ['group', 'supergroup', 'channel'] or not req.new_chat_member.can_invite_users:
        return
    admins = [i.user_id for i in await session.get_admins()]
    admins.extend(config.bot.admin_ids)
    if req.from_user.id not in admins:
        return
    text = f'Добавить канал|чат {req.chat.title} в ОП?'
    await req.bot.send_message(
        chat_id=req.from_user.id,
        text=text,
        reply_markup=get_chat_add_keyboard(req.chat.id)
    )


@admin_router.callback_query(F.data.startswith('add_opchannel_'))
async def send_op_request(clb: CallbackQuery, session: DataInteraction, dialog_manager: DialogManager):
    chat_id = int(clb.data.split('_')[2])
    await dialog_manager.start(state=adminSG.get_button_link, data={'chat_id': chat_id},mode=StartMode.RESET_STACK)


@admin_router.callback_query(F.data == 'decline')
async def del_op_request(clb: CallbackQuery, dialog_manager: DialogManager):
    await clb.answer('Заявка была отклонена')
    await clb.message.delete()


@admin_router.callback_query(F.data.startswith('verification'))
async def success_verification(clb: CallbackQuery, session: DataInteraction):
    user_id = int(clb.data.split('_')[1])
    await session.update_vip(user_id, vip=True)
    user = await session.get_user(user_id)
    translator: Translator = create_translator(user.locale)
    await clb.bot.send_message(
        chat_id=user_id,
        text=translator['success_vip_verification']
    )
    await clb.answer('Заявка была успешно одобрена')
    try:
        await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=clb.message.message_id - 1)
    except Exception:
        ...
    await clb.message.delete()


@admin_router.callback_query(F.data == 'cancel_verification')
async def cancel_verification(clb: CallbackQuery):
    await clb.answer('Заявка была отклонена')
    try:
        await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=clb.message.message_id - 1)
    except Exception:
        ...
    await clb.message.delete()


@admin_router.callback_query(F.data.startswith('block_user'))
async def block_user(clb: CallbackQuery, session: DataInteraction, cache: TTLCache):
    user_id = int(clb.data.split('|')[1])
    application = await session.get_application(user_id)
    await session.del_application(user_id)
    await clb.message.delete()
    try:
        for msg_id in application.message_ids:
            await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=msg_id)
    except Exception as err:
        ...
    user = await session.get_user(user_id)
    translator: Translator = create_translator(user.locale)
    try:
        await clb.bot.send_message(
            chat_id=user.user_id,
            text=translator['block_message']
        )
    except Exception:
        await session.set_active(user.user_id, 0)

    await session.set_block(user.user_id)
    await session.del_form(user.user_id)
    user = await session.get_user(user_id)
    cache[user.user_id] = user

