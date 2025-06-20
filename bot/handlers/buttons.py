from telegram import InlineKeyboardButton, ReplyKeyboardMarkup

from bot.handlers.callback_data import (ACCOUNT_SETTINGS, ADD_TRACK, BOT_INFO,
                                        CANCEL_DELETE, CHECK_HISTORY,
                                        CONFIRM_DELETE, MENU, OZON,
                                        SHOW_ALL_TRACK, START_AUTHORIZATION,
                                        START_NOTIFICATIONS,
                                        START_REGISTRATION, WILDBERRIES)

MAIN_REPLY_BUTTONS = ['Меню 🔥', 'Авторизация 🔐', 'Ваш аккаунт 📱']

REPLY_KEYBOARD = ReplyKeyboardMarkup(
    [MAIN_REPLY_BUTTONS],
    resize_keyboard=True
)

# buttons
GO_TO_TRACK_LIST_BUTTON = InlineKeyboardButton(
    'Вернуться к списку товаров ⬅️',
    callback_data=SHOW_ALL_TRACK
)
MENU_BUTTON = InlineKeyboardButton(
    'Меню 📦', callback_data=MENU
)
AUTHORIZATION_BUTTON = InlineKeyboardButton(
    '🔐 Авторизация', callback_data='authorization'
)
ACCOUNT_SETTINS_BUTTON = InlineKeyboardButton(
    text='⚙️ Настройки аккаунта',
    callback_data=ACCOUNT_SETTINGS
)

# handlers.base buttons
MENU_BUTTONS = [
    [
        InlineKeyboardButton(
            text='📦 Мои товары',
            callback_data=SHOW_ALL_TRACK
        )
    ],
    [
        InlineKeyboardButton(
            text='➕ Добавить товар',
            callback_data=ADD_TRACK
        )
    ],
    [
        InlineKeyboardButton(
            text='🔔 Включить оповещения',
            callback_data=START_NOTIFICATIONS
        )
    ],
    [
        ACCOUNT_SETTINS_BUTTON
    ],
    [
        InlineKeyboardButton(
            text='ℹ️ О боте',
            callback_data=BOT_INFO
        )
    ],
]
REGISTER_USER_BUTTONS = [
    [
        MENU_BUTTON,
        ACCOUNT_SETTINS_BUTTON
    ]
]
NOT_REGISTER_USER_BUTTONS = [
    [AUTHORIZATION_BUTTON]
]
START_REGISTRATION_BUTTONS = [
    [
        InlineKeyboardButton(
            'Начать регистрацию 🔥',
            callback_data=START_REGISTRATION
        )
    ]
]
# handlers.track
def get_track_keyboard(track_id: int) -> list[InlineKeyboardButton]:
    """Собирает кнопки для экземпляра Track."""
    return [
        [
            InlineKeyboardButton(
                'Изменить ⚡',
                callback_data=f'track_refresh_target_price_{track_id}'
            ),
            InlineKeyboardButton(
                'Удалить ❌',
                callback_data=f'track_delete_{track_id}'
            )
        ],
        [
            InlineKeyboardButton(
                'Посмотреть историю 🛍️',
                callback_data=f'{CHECK_HISTORY}_{track_id}'
            )
        ]
    ]

SHOW_ALL_BUTTONS = [
    [
        InlineKeyboardButton(
            'Отследить товар 🔍',
            callback_data=ADD_TRACK
        )
    ],
    [
        MENU_BUTTON
    ]
]
GO_BACK_NEW_TARGET_PRICE_BUTTONS = [
    [
        GO_TO_TRACK_LIST_BUTTON,
        MENU_BUTTON
    ]
]
SELECT_MARKETPLACE_BUTTONS = [
    [
        InlineKeyboardButton(
            'WB 🟣',
            callback_data=f'track_{WILDBERRIES}'
        ),
        InlineKeyboardButton(
            'OZON (WB)🔵',
            callback_data=f'track_{WILDBERRIES}'
        )
    ]
]

def get_create_track_buttons(
    track_id: int
):
    return (
        get_track_keyboard(track_id)
        + [[
            GO_TO_TRACK_LIST_BUTTON
        ]]
    )

CHECK_HISTORY_BUTTONS = [
    [GO_TO_TRACK_LIST_BUTTON]
]
CONFIRM_TRACK_DELETE_BUTTONS = [
    [
        InlineKeyboardButton(
            'Подтвердить 🖱️',
            callback_data=CONFIRM_DELETE
        ),
        InlineKeyboardButton(
            'Назад ⬅️',
            callback_data=CANCEL_DELETE
        )
    ]
]
FINISH_DELETE_TRACK_BUTTONS = [
    [GO_TO_TRACK_LIST_BUTTON]
]

# handlers.user
ACCOUNT_SETTINGS_BUTTONS = [
    [MENU_BUTTON]
]
LOAD_ACCOUNT_DATA = [
    [MENU_BUTTON]
]
CHECK_ACCOUNT_DATA_BUTTONS = [
    [
        MENU_BUTTON,
        InlineKeyboardButton('Назад ⬅️', callback_data=ACCOUNT_SETTINGS)
    ]
]
FINISH_REGISTRATION_BUTTONS = [
    [AUTHORIZATION_BUTTON]
]
FINISH_AUTHORIZATION_BUTTONS = [
    [MENU_BUTTON],
    [ACCOUNT_SETTINS_BUTTON]
]