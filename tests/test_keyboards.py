from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.keyboards import site_item_kb, DELETE_PREFIX


def test_site_item_kb_creates_markup():
    site_id = 123
    kb: InlineKeyboardMarkup = site_item_kb(site_id)

    # проверяем, что это действительно клавиатура
    assert isinstance(kb, InlineKeyboardMarkup)

    # проверяем, что есть хотя бы одна кнопка
    assert len(kb.inline_keyboard) == 1
    assert len(kb.inline_keyboard[0]) == 1

    button: InlineKeyboardButton = kb.inline_keyboard[0][0]

    # проверяем текст кнопки
    assert button.text == "Удалить"

    # проверяем callback_data
    assert button.callback_data == f"{DELETE_PREFIX}:{site_id}"
