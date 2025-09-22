from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DELETE_PREFIX = "del"

def site_item_kb(site_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"{DELETE_PREFIX}:{site_id}"
                )
            ]
        ]
    )
