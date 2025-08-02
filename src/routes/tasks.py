from datetime import datetime, timezone

from aiogram import Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from src.api.db.database import get_session
from src.objects.tasks import TaskService
from src.objects.users import UserService


# FSM states for task creation
class TaskStates(StatesGroup):
    title: State = State()
    deadline: State = State()
    assign: State = State()
    confirm: State = State()


async def start_task_menu(message: types.Message) -> None:
    """Показать подменю для задач"""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="➕ Создать задачу"),
                types.KeyboardButton(text="📄 Мои задачи"),
                types.KeyboardButton(text="🔎 Все задачи"),
            ],
            [types.KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел «Задачи»:", reply_markup=keyboard)


async def cmd_task_create(message: types.Message, state: FSMContext) -> None:
    """Начало диалога создания задачи"""
    await message.answer("Шаг 1/4. Введите название задачи:")
    await state.set_state(TaskStates.title)


async def process_title(message: types.Message, state: FSMContext) -> None:
    """Обработка названия задачи и запрос дедлайна"""
    await state.update_data(title=message.text)
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Указать дату", callback_data="task_deadline_date"),
                InlineKeyboardButton(text="🛑 Без дедлайна", callback_data="task_deadline_none"),
            ]
        ]
    )
    await message.answer("Шаг 2/4. Указать дедлайн?", reply_markup=keyboard)
    await state.set_state(TaskStates.deadline)


async def process_deadline(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора опции дедлайна или переход к текстовому вводу"""
    await callback.answer()
    data: dict = await state.get_data()
    if callback.data == "task_deadline_none":
        data["deadline"] = None
        await callback.message.edit_text("Дедлайн не указан.")
    else:
        await callback.message.edit_text(
            "Введите дату в формате ДД.ММ.ГГГГ (например, 25.05.2023):",
        )
        await state.set_state(TaskStates.deadline)
        return

    await state.update_data(data)
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ввести @username", callback_data="task_assign_manual")],
        ]
    )
    await callback.message.answer("Шаг 3/4. Кому назначить?", reply_markup=keyboard)
    await state.set_state(TaskStates.assign)


async def process_deadline_text(message: types.Message, state: FSMContext) -> None:
    """Обработка текстового ввода дедлайна"""
    text: str = message.text.strip()
    try:
        # ожидаем формат "DD.MM.YYYY HH:MM"
        deadline = datetime.strptime(text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer(
            "Неверный формат. Введите ДД.MM.YYYY HH:MM (например, 25.05.2025 14:30)"
        )
        return
    await state.update_data(deadline=deadline)

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ввести @username", callback_data="task_assign_manual")]
        ]
    )
    await message.answer("Шаг 3/4. Кому назначить?", reply_markup=keyboard)
    await state.set_state(TaskStates.assign)


async def process_assign_manual(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запрос ручного ввода username для назначения"""
    await callback.message.answer("Введите @username исполнителя:", reply_markup=ForceReply())


async def process_assign_text(message: types.Message, state: FSMContext) -> None:
    """Обработка текстового ввода username и подготовка подтверждения"""
    match = message.text.strip().split()
    if len(match) != 2 or not match[1].isdigit():
        await message.answer("Неверный формат. Используйте подсказки при вводе пользователя.")
        return

    user_id = int(match[1])

    async for session in get_session():
        user = await UserService.get(session, user_id)
    if not user:
        await message.answer("Пользователь не найден.")
        return

    data = await state.get_data()
    assigned_to_ids = data.get("assigned_to_ids")
    if user.id != assigned_to_ids:
        await state.update_data(assigned_to_ids=user.id)
        await message.answer(f"✅ Добавлен: @{user.username}")
    else:
        await message.answer(f"@{user.username} уже назначен.")

    # Повторим кнопку "Готово"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Готово", callback_data="task_assign_done")]]
    )
    await message.answer("Добавьте ещё пользователя или нажмите «Готово»", reply_markup=keyboard)


async def process_confirm(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработка подтверждения создания задачи"""
    await callback.answer()
    data = await state.get_data()

    if callback.data == "task_assign_done":
        assigned_to_ids = data.get("assigned_to_ids")
        if not assigned_to_ids:
            await callback.message.answer("Вы не выбрали ни одного исполнителя.")
            return

        async for session in get_session():
            user = await UserService.get(session, assigned_to_ids)

        text = (
            f"<b>Название:</b> {data['title']}\n"
            f"<b>Дедлайн:</b> {data.get('deadline') or '—'}\n"
            f"<b>Исполнители:</b> {user.username}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Сохранить", callback_data="task_confirm_save")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="task_confirm_cancel")],
            ]
        )
        await callback.message.answer(text, reply_markup=keyboard)
        await state.set_state(TaskStates.confirm)
        return

    if callback.data == "task_confirm_cancel":
        await callback.message.answer("Создание задачи отменено ❌")
        await state.clear()
        return

    if callback.data == "task_confirm_save":
        async for session in get_session():
            task = await TaskService.create(
                session=session,
                title=data["title"],
                deadline=data.get("deadline"),
                assigned_to=data.get("assigned_to_ids"),
            )
        await callback.message.answer(f"Задача '{task.title}' создана ✅")
        await state.clear()


async def user_inline_search(inline_query: InlineQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state != TaskStates.assign.state:
        return  # Не обрабатываем inline-запрос, если не на шаге assign

    query = inline_query.query.lower()
    if not query:
        return

    async for session in get_session():
        users = await UserService.list(session)
    matched = [u for u in users if u.username and query in u.username.lower()]

    results = [
        InlineQueryResultArticle(
            id=str(user.id),
            title=f"@{user.username}",
            input_message_content=InputTextMessageContent(message_text=f"👤 {user.id}"),
            description=f"{user.full_name or ''}",
        )
        for user in matched[:20]
    ]

    await inline_query.answer(results, cache_time=1)


def register_task_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров для работы с задачами"""
    dp.message.register(start_task_menu, F.text == "📋 Задачи")

    dp.message.register(cmd_task_create, Command(commands=["task_create"]))
    dp.message.register(start_task_menu, F.text == "➕ Создать задачу")

    dp.message.register(process_title, StateFilter(TaskStates.title))

    dp.callback_query.register(process_deadline, StateFilter(TaskStates.deadline))

    dp.message.register(process_deadline_text, StateFilter(TaskStates.deadline))
    dp.callback_query.register(
        process_assign_manual,
        lambda c: c.data == "task_assign_manual",
        StateFilter(TaskStates.assign),
    )
    dp.message.register(process_assign_text, StateFilter(TaskStates.assign))

    dp.callback_query.register(process_confirm, StateFilter(TaskStates.assign))
    dp.callback_query.register(process_confirm, StateFilter(TaskStates.confirm))

    dp.inline_query.register(user_inline_search)
