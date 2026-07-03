import hashlib
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def callback_id(value: str) -> str:
    """
    Telegram callback_data limit is 64 bytes.
    Armenian/Russian text can exceed the limit, so we use a short stable ID.
    """
    return "v_" + hashlib.sha1(value.encode("utf-8")).hexdigest()[:20]


def inline_keyboard(options: list[str], row_width: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.button(text=option, callback_data=callback_id(option))
    builder.adjust(row_width)
    return builder.as_markup()


def selected_option(callback_data: str, options: list[str]) -> str | None:
    for option in options:
        if callback_id(option) == callback_data:
            return option
    return None
