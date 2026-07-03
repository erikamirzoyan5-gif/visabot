import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeChat,
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import settings
from database import init_db, upsert_user, save_assessment, save_lead, get_stats, export_leads_csv
from keyboards import inline_keyboard, selected_option
from translations import tr, LANG_BUTTONS, LANG_BY_BUTTON
from questions import COUNTRIES, VISA_TYPES, get_questions
from scoring import calculate_score


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    language = State()
    country = State()
    visa_type = State()
    answering = State()
    consultation = State()
    name = State()
    phone = State()
    email = State()
    preferred_time = State()
    comment = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


async def safe_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()

    upsert_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
    )

    await message.answer(
        tr("hy", "choose_language"),
        reply_markup=inline_keyboard(list(LANG_BUTTONS.values())),
    )
    await state.set_state(Form.language)


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")
    await state.clear()
    await message.answer(tr(lang, "cancelled"))


@dp.message(Command("admin"))
async def admin(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.")
        return

    stats = get_stats()
    top = "\n".join([f"• {country}: {count}" for country, count in stats["top_countries"]]) or "No data"

    await message.answer(
        "<b>Greenwich Visa Bot Admin</b>\n\n"
        f"Users: {stats['users']}\n"
        f"Assessments: {stats['assessments']}\n"
        f"Leads: {stats['leads']}\n"
        f"Average score: {stats['avg_score']}%\n"
        f"Conversion: {stats['conversion']}%\n\n"
        f"<b>Top countries</b>\n{top}\n\n"
        "Use /export to download leads CSV."
    )


@dp.message(Command("export"))
async def export(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.")
        return

    path = export_leads_csv()
    await message.answer_document(FSInputFile(path))


@dp.callback_query(Form.language)
async def choose_language(callback: CallbackQuery, state: FSMContext) -> None:
    selected = selected_option(callback.data, list(LANG_BUTTONS.values()))
    if not selected:
        await callback.message.answer(tr("hy", "invalid"))
        await safe_answer(callback)
        return
    lang = LANG_BY_BUTTON.get(selected, "hy")
    await state.update_data(
        lang=lang,
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
    )
    upsert_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        first_name=callback.from_user.first_name or "",
        language=lang,
    )

    await callback.message.answer(tr(lang, "welcome"))
    await callback.message.answer(tr(lang, "country"), reply_markup=inline_keyboard(COUNTRIES[lang]))
    await state.set_state(Form.country)
    await safe_answer(callback)


@dp.callback_query(Form.country)
async def choose_country(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    selected = selected_option(callback.data, COUNTRIES[lang])
    if not selected:
        await callback.message.answer(tr(lang, "invalid"))
        await safe_answer(callback)
        return

    await state.update_data(country=selected)
    await callback.message.answer(tr(lang, "visa_type"), reply_markup=inline_keyboard(VISA_TYPES[lang]))
    await state.set_state(Form.visa_type)
    await safe_answer(callback)


@dp.callback_query(Form.visa_type)
async def choose_visa_type(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    selected = selected_option(callback.data, VISA_TYPES[lang])
    if not selected:
        await callback.message.answer(tr(lang, "invalid"))
        await safe_answer(callback)
        return

    await state.update_data(visa_type=selected, question_index=0, answers={})
    await state.set_state(Form.answering)
    await ask_next_question(callback.message, state)
    await safe_answer(callback)


async def ask_next_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")
    country = data.get("country", "")
    index = int(data.get("question_index", 0))

    questions = get_questions(lang, country)

    if index >= len(questions):
        await show_result(message, state)
        return

    question = questions[index]
    progress = f"{tr(lang, 'progress')} {index + 1}/{len(questions)}"
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await message.answer(
        f"<b>{progress}</b>\n\n{question.text}",
        reply_markup=inline_keyboard(question.options),
    )


@dp.callback_query(Form.answering)
async def process_answer(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")
    country = data.get("country", "")
    index = int(data.get("question_index", 0))

    questions = get_questions(lang, country)
    if index >= len(questions):
        await show_result(callback.message, state)
        await safe_answer(callback)
        return

    question = questions[index]
    selected = selected_option(callback.data, question.options)
    if not selected:
        await callback.message.answer(tr(lang, "invalid"))
        await safe_answer(callback)
        return

    answers = data.get("answers", {})
    answers[question.key] = selected

    await state.update_data(answers=answers, question_index=index + 1)
    await ask_next_question(callback.message, state)
    await safe_answer(callback)


async def show_result(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    result = calculate_score(data)

    await state.update_data(
        score=result.score,
        strengths=result.strengths,
        risks=result.risks,
        recommendations=result.recommendations,
    )

    data = await state.get_data()
    save_assessment(data)

    text = (
        f"<b>{tr(lang, 'result')}: {result.score}%</b>\n\n"
        f"<b>{tr(lang, 'strengths')}</b>\n"
        + "\n".join(f"• {x}" for x in result.strengths)
        + f"\n\n<b>{tr(lang, 'risks')}</b>\n"
        + "\n".join(f"• {x}" for x in result.risks)
        + f"\n\n<b>{tr(lang, 'recommendations')}</b>\n"
        + "\n".join(f"• {x}" for x in result.recommendations)
        + f"\n\n⚠️ {tr(lang, 'disclaimer')}\n\n"
        + tr(lang, "cta")
    )

    await message.answer(
        text,
        reply_markup=inline_keyboard([tr(lang, "yes"), tr(lang, "contact"), tr(lang, "no")]),
    )
    await state.set_state(Form.consultation)


@dp.callback_query(Form.consultation)
async def consultation(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    selected = selected_option(callback.data, [tr(lang, "yes"), tr(lang, "contact"), tr(lang, "no")])
    if selected == tr(lang, "no"):
        await callback.message.answer(tr(lang, "cancelled"))
        await state.clear()
        await safe_answer(callback)
        return

    if selected not in [tr(lang, "yes"), tr(lang, "contact")]:
        await callback.message.answer(tr(lang, "invalid"))
        await safe_answer(callback)
        return

    await state.update_data(consultation_choice=selected)
    await callback.message.answer(tr(lang, "name"))
    await state.set_state(Form.name)
    await safe_answer(callback)


@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2:
        data = await state.get_data()
        await message.answer(tr(data.get("lang", "hy"), "name"))
        return

    await state.update_data(name=name)
    data = await state.get_data()
    await message.answer(tr(data.get("lang", "hy"), "phone"))
    await state.set_state(Form.phone)


@dp.message(Form.phone)
async def get_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    await state.update_data(phone=phone)
    data = await state.get_data()
    lang = data.get("lang", "hy")
    await message.answer(tr(lang, "email"), reply_markup=inline_keyboard([tr(lang, "skip")]))
    await state.set_state(Form.email)


@dp.callback_query(Form.email)
async def skip_email(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    selected = selected_option(callback.data, [tr(lang, "skip")])
    if selected != tr(lang, "skip"):
        await callback.message.answer(tr(lang, "invalid"))
        await safe_answer(callback)
        return

    await state.update_data(email="")
    await callback.message.answer(tr(lang, "time"))
    await state.set_state(Form.preferred_time)
    await safe_answer(callback)


@dp.message(Form.email)
async def get_email(message: Message, state: FSMContext) -> None:
    await state.update_data(email=message.text.strip())
    data = await state.get_data()
    await message.answer(tr(data.get("lang", "hy"), "time"))
    await state.set_state(Form.preferred_time)


@dp.message(Form.preferred_time)
async def get_time(message: Message, state: FSMContext) -> None:
    await state.update_data(preferred_time=message.text.strip())
    data = await state.get_data()
    lang = data.get("lang", "hy")
    await message.answer(tr(lang, "comment"), reply_markup=inline_keyboard([tr(lang, "skip")]))
    await state.set_state(Form.comment)


@dp.callback_query(Form.comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    selected = selected_option(callback.data, [tr(lang, "skip")])
    if selected != tr(lang, "skip"):
        await callback.message.answer(tr(lang, "invalid"))
        await safe_answer(callback)
        return

    await state.update_data(comment="")
    await finish_lead(callback.message, state)
    await safe_answer(callback)


@dp.message(Form.comment)
async def get_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=message.text.strip())
    await finish_lead(message, state)


async def finish_lead(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "hy")

    lead_id = save_lead(data)

    if settings.manager_chat_id:
        try:
            await bot.send_message(settings.manager_chat_id, format_manager_message(data, lead_id))
        except Exception as exc:
            logging.exception("Failed to notify manager: %s", exc)

    await message.answer(tr(lang, "sent"))
    await state.clear()


def format_manager_message(data: dict, lead_id: int) -> str:
    username = data.get("username")
    username_text = f"@{username}" if username else "No username"
    answers = data.get("answers", {})
    answers_text = "\n".join(f"• <b>{key}</b>: {value}" for key, value in answers.items())

    return (
        f"🟢 <b>New Greenwich Visa Lead #{lead_id}</b>\n\n"
        f"<b>Name:</b> {data.get('name')}\n"
        f"<b>Phone/Telegram:</b> {data.get('phone')}\n"
        f"<b>Email:</b> {data.get('email') or '-'}\n"
        f"<b>Preferred time:</b> {data.get('preferred_time')}\n"
        f"<b>Comment:</b> {data.get('comment') or '-'}\n\n"
        f"<b>Telegram ID:</b> {data.get('telegram_id')}\n"
        f"<b>Username:</b> {username_text}\n"
        f"<b>Language:</b> {data.get('lang')}\n\n"
        f"<b>Country:</b> {data.get('country')}\n"
        f"<b>Visa type:</b> {data.get('visa_type')}\n"
        f"<b>Score:</b> {data.get('score')}%\n\n"
        f"<b>Answers:</b>\n{answers_text}"
    )

async def setup_bot_commands() -> None:
    user_commands = [
        BotCommand(command="start", description="Սկսել"),
        BotCommand(command="cancel", description="Չեղարկել ընթացիկ գործողությունը"),
    ]

    admin_commands = [
        BotCommand(command="start", description="Սկսել"),
        BotCommand(command="cancel", description="Չեղարկել ընթացիկ գործողությունը"),
        BotCommand(command="admin", description="Ադմին վիճակագրություն"),
        BotCommand(command="export", description="Ներբեռնել լիդերի CSV ֆայլը"),
        BotCommand(command="results", description="Տեսնել վերջին թեստի արդյունքները"),
        BotCommand(command="export_results", description="Ներբեռնել բոլոր թեստերի արդյունքները"),
    ]

    await bot.set_my_commands(
        user_commands,
        scope=BotCommandScopeDefault()
    )

    for admin_id in settings.admin_ids:
        await bot.set_my_commands(
            admin_commands,
            scope=BotCommandScopeChat(chat_id=admin_id)
        )

async def main() -> None:
    init_db()
    await setup_bot_commands()
    logging.info("Greenwich Visa Bot Pro is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
