from aiogram import executor

from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)
    await db.create_table_users()
    await db.create_table_anonymous()
    await db.create_table_students()
    await db.create_table_teachers()
    await db.create_table_groups()
    await db.create_table_departments()
    await db.create_table_statistics()
    await db.create_language()

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
