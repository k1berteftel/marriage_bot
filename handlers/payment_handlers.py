from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram_dialog import DialogManager, StartMode
from dateutil.relativedelta import relativedelta

from utils.schedulers import check_vip, check_super_vip, check_form_boost, del_message
from utils.build_ids import get_random_id
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.action_data_class import DataInteraction
from utils.translator import Translator as load_translator
from utils.translator.translator import Translator
from states import state_groups as states


payment_router = Router()


@payment_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@payment_router.message(F.successful_payment)
async def success_payment(msg: Message, session: DataInteraction, translator: Translator, scheduler: AsyncIOScheduler, bot: Bot, dialog_manager: DialogManager):
    amount = int(round(msg.successful_payment.total_amount * 1.7))  # перевод обратно в валюту
    print(amount)
    type = msg.successful_payment.invoice_payload
    user = await session.get_user(msg.from_user.id)
    if type.startswith('rate'):
        tokens = int(type.split('_')[-1])
        await session.update_tokens(user.user_id, tokens)
        await session.add_transaction(msg.from_user.id, tokens, 'Покупка токенов')
    elif type.startswith('super_vip'):
        hours = int(type.split('_')[-1])
        if user.super_vip:
            job = scheduler.get_job(job_id=f'super_vip_{msg.from_user.id}')
            if job:
                job.remove()
            date = user.super_vip + relativedelta(hours=hours)
            await session.set_super_vip(msg.from_user.id, date)
            scheduler.add_job(
                check_super_vip,
                trigger='interval',
                args=[bot, msg.from_user.id, session, scheduler, translator],
                id=f'super_vip_{msg.from_user.id}',
                minutes=30
            )
        else:
            date = datetime.now() + relativedelta(hours=hours)
            await session.set_super_vip(msg.from_user.id, date)
            scheduler.add_job(
                check_super_vip,
                trigger='interval',
                args=[bot, msg.from_user.id, session, scheduler, translator],
                id=f'super_vip_{msg.from_user.id}',
                hours=1
            )
        message = await bot.send_message(chat_id=msg.from_user.id, text=translator['super_vip_status'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
    elif type.startswith('boost'):
        hours = int(type.split('_')[-1])
        form = await session.get_form(msg.from_user.id)
        if form.boost:
            job = scheduler.get_job(job_id=f'form_boost_{msg.from_user.id}')
            job.remove()
            date = form.boost + relativedelta(hours=hours)
            await session.set_form_boost(msg.from_user.id, date)
            scheduler.add_job(
                check_form_boost,
                trigger='interval',
                args=[bot, msg.from_user.id, session, scheduler, translator],
                id=f'form_boost_{msg.from_user.id}',
                minutes=30
            )
        else:
            await session.set_form_boost(msg.from_user.id, datetime.now() + relativedelta(hours=hours))
            scheduler.add_job(
                check_form_boost,
                trigger='interval',
                args=[bot, msg.from_user.id, session, scheduler, translator],
                id=f'form_boost_{msg.from_user.id}',
                hours=1
            )
        message = await bot.send_message(chat_id=msg.from_user.id, text=translator['boost_on'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
    else:
        date = relativedelta(days=int(type.split('_')[-1]))
        if not user.vip:
            await session.update_vip(msg.from_user.id, True, vip_end=datetime.now() + date)
            if not scheduler.get_job(str(msg.from_user.id)):
                scheduler.add_job(
                    check_vip,
                    'interval',
                    args=[bot, msg.from_user.id, session, translator, scheduler],
                    id=str(msg.from_user.id),
                    days=1
                )
            message = await bot.send_message(chat_id=msg.from_user.id, text=translator['on_vip_success'])
            job_id = get_random_id()
            scheduler.add_job(
                del_message,
                'interval',
                args=[message, scheduler, job_id],
                seconds=7,
                id=job_id
            )
        else:
            await session.update_vip(msg.from_user.id, True, vip_end=user.vip_end + date)
            message = await bot.send_message(chat_id=msg.from_user.id, text=translator['vip_extension'])
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
        translator = load_translator(referral.locale)
        await bot.send_message(chat_id=referral.user_id, text=translator['referral_payment'])
        await session.update_balance(user.user_id, int(round(amount * 0.5)))
        await session.add_transaction(referral.user_id, int(round(amount * 0.5)), 'Реферальные зачисления')
        await session.update_income(referral.user_id, int(round(amount * 0.5)))


@payment_router.callback_query(F.data == 'back|payment_menu')
async def back_payment_menu(clb: CallbackQuery, dialog_manager: DialogManager, translator: Translator):
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=clb.message.message_id - 1)
        except Exception:
            ...
    await clb.message.delete()
    await dialog_manager.start(states.balanceSG.start, mode=StartMode.RESET_STACK)