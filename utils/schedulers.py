import random

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.model import UsersTable
from database.action_data_class import DataInteraction
from utils.translator.translator import Translator
from utils.build_ids import get_random_id
from utils.translator import Translator as load_Translator
from dateutil.relativedelta import relativedelta
from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse


async def check_form_boost(bot: Bot, user_id: int, session: DataInteraction, scheduler: AsyncIOScheduler, translator: Translator):
    form = await session.get_form(user_id)
    if datetime.today().timestamp() > form.boost.timestamp():
        await bot.send_message(
            chat_id=user_id,
            text=translator['boost_off']
        )
        await session.set_form_boost(user_id, None)
        await scheduler.remove_job(job_id=f'form_boost_{user_id}')


async def check_super_vip(bot: Bot, user_id: int, session: DataInteraction, scheduler: AsyncIOScheduler, translator: Translator):
    user = await session.get_user(user_id)
    if datetime.today().timestamp() > user.super_vip.timestamp():
        await bot.send_message(
            chat_id=user_id,
            text=translator['super_vip_off']
        )
        await session.set_super_vip(user_id, None)
        await scheduler.remove_job(job_id=f'super_vip_{user_id}')


async def check_vip(bot: Bot, user_id: int, session: DataInteraction, translator: Translator,  scheduler: AsyncIOScheduler):
    user = await session.get_user(user_id)
    print(user.vip_end)
    if user.vip_end.timestamp() < datetime.today().timestamp():
        job = scheduler.get_job(job_id=str(user_id))
        if job:
            job.remove()
        await bot.send_message(
            chat_id=user_id,
            text=translator['not_enough_tokens']
        )
        await session.update_vip(user_id, False, vip_end=None)
        return False
    else:
        if (user.vip_end - datetime.today()).days == 1:
            await bot.send_message(
                chat_id=user_id,
                text=translator['alert_about_vip_end']
            )


async def send_messages(bot: Bot, session: DataInteraction, keyboard: InlineKeyboardMarkup|None, message: list[int]):
    users = await session.get_users()
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.user_id,
                from_chat_id=message[1],
                message_id=message[0],
                reply_markup=keyboard
            )
            if user.active == 0:
                await session.set_active(user.user_id, 1)
        except Exception as err:
            print(err)
            await session.set_active(user.user_id, 0)


async def send_messages_targeting(users: list[UsersTable], bot: Bot, session: DataInteraction, keyboard: InlineKeyboardMarkup|None, message: list[int]):
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.user_id,
                from_chat_id=message[1],
                message_id=message[0],
                reply_markup=keyboard
            )
            if user.active == 0:
                await session.set_active(user.user_id, 1)
        except Exception as err:
            print(err)
            await session.set_active(user.user_id, 0)


async def check_payment(payment_id: any, user_id: int, bot: Bot, scheduler: AsyncIOScheduler,
                        session: DataInteraction, translator: Translator, **kwargs):
    payment: PaymentResponse = await Payment.find_one(payment_id)
    if payment.paid:
        amount = kwargs.get('amount')
        user = await session.get_user(user_id)
        if kwargs.get('type') == 'rate':
            tokens = kwargs.get('tokens')
            await session.update_tokens(user.user_id, tokens)
            await session.add_transaction(user_id, tokens, 'Покупка токенов')
        elif kwargs.get('type') == 'super_vip':
            hours = kwargs.get('hours')
            if user.super_vip:
                job = scheduler.get_job(job_id=f'super_vip_{user_id}')
                job.remove()
                date = user.super_vip + relativedelta(hours=hours)
                await session.set_super_vip(user_id, date)
                scheduler.add_job(
                    check_super_vip,
                    trigger='interval',
                    args=[bot, user_id, session, scheduler, translator],
                    id=f'super_vip_{user_id}',
                    minutes=30
                )
            else:
                date = datetime.today() + relativedelta(hours=hours)
                await session.set_super_vip(user_id, date)
                scheduler.add_job(
                    check_super_vip,
                    trigger='interval',
                    args=[bot, user_id, session, scheduler, translator],
                    id=f'super_vip_{user_id}',
                    hours=1
                )
            message = await bot.send_message(chat_id=user_id, text=translator['super_vip_status'])
            job_id = get_random_id()
            scheduler.add_job(
                del_message,
                'interval',
                args=[message, scheduler, job_id],
                seconds=7,
                id=job_id
            )
        elif kwargs.get('type') == 'boost':
            hours = kwargs.get('hours')
            form = await session.get_form(user_id)
            if form.boost:
                job = scheduler.get_job(job_id=f'form_boost_{user_id}')
                job.remove()
                date = form.boost + relativedelta(hours=hours)
                await session.set_form_boost(user_id, date)
                scheduler.add_job(
                    check_form_boost,
                    trigger='interval',
                    args=[bot, user_id, session, scheduler, translator],
                    id=f'form_boost_{user_id}',
                    minutes=30
                )
            else:
                await session.set_form_boost(user_id, datetime.today() + relativedelta(hours=hours))
                scheduler.add_job(
                    check_form_boost,
                    trigger='interval',
                    args=[bot, user_id, session, scheduler, translator],
                    id=f'form_boost_{user_id}',
                    hours=1
                )
            message = await bot.send_message(chat_id=user_id, text=translator['boost_on'])
            job_id = get_random_id()
            scheduler.add_job(
                del_message,
                'interval',
                args=[message, scheduler, job_id],
                seconds=7,
                id=job_id
            )
        else:
            date = kwargs.get('date')
            if not user.vip:
                await session.update_vip(user_id, True, vip_end=datetime.today() + date)
                if not scheduler.get_job(str(user_id)):
                    scheduler.add_job(
                        check_vip,
                        'interval',
                        args=[bot, user_id, session, translator, scheduler],
                        id=str(user_id),
                        days=1
                    )
                message = await bot.send_message(chat_id=user_id, text=translator['on_vip_success'])
                job_id = get_random_id()
                scheduler.add_job(
                    del_message,
                    'interval',
                    args=[message, scheduler, job_id],
                    seconds=7,
                    id=job_id
                )
            else:
                await session.update_vip(user_id, True, vip_end=user.vip_end + date)
                message = await bot.send_message(chat_id=user_id, text=translator['vip_extension'])
                job_id = get_random_id()
                scheduler.add_job(
                    del_message,
                    'interval',
                    args=[message, scheduler, job_id],
                    seconds=7,
                    id=job_id
                )
        if user.referral:
            referral = await session.get_user(user.referral)
            translator = load_Translator(referral.locale)
            await bot.send_message(chat_id=referral.user_id, text=translator['referral_payment'])
            await session.update_balance(user.user_id, int(round(amount * 0.5)))
            await session.add_transaction(referral.user_id, int(round(amount * 0.5)), 'Реферальные зачисления')
            await session.update_income(referral.user_id, int(round(amount * 0.5)))
        await bot.send_message(chat_id=user_id, text=translator['success_payment'])
        job = scheduler.get_job(job_id=f'payment_{user_id}')
        if job:
            scheduler.remove_job(job_id=f'payment_{user_id}')
    if kwargs.get('last'):
        scheduler.remove_job(job_id=f'last_payment_{user_id}')
    return


async def del_message(msg: Message, scheduler: AsyncIOScheduler, job_id: str):
    try:
        await msg.delete()
    except Exception:
        ...
    scheduler.remove_job(job_id=job_id)


async def send_notification(user_id: int, session: DataInteraction, translator: Translator, bot: Bot):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=translator['notification_button'], callback_data='open_ref_menu')]
        ]
    )
    user = await session.get_user(user_id)
    count = random.randint(5, 20)
    await bot.send_message(
        chat_id=user_id,
        text=translator['notification_message'].format(count=count, name=user.name),
        reply_markup=keyboard
    )


async def start_schedulers(session: DataInteraction, scheduler: AsyncIOScheduler, bot: Bot):
    users: list[UsersTable] = await session.get_vip_users()
    print(len(users))
    for user in users:
        translator: Translator = load_Translator(user.locale)
        if user.vip_end and user.vip_end.timestamp() < datetime.today().timestamp():
            await session.update_vip(user.user_id, vip=False, vip_end=None)
            continue
        if user.vip and user.vip_end.timestamp() > datetime.today().timestamp():
            scheduler.add_job(
                check_vip,
                'interval',
                args=[bot, user.user_id, session, translator, scheduler],
                id=str(user.user_id),
                days=1
            )

