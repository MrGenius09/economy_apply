from aiogram import Dispatcher

from loader import dp
# from .is_admin import AdminFilter


if __name__ == "filters":
    #dp.filters_factory.bind(is_admin)
    pass

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

class IsAdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        chat_id = message.chat.id
        user_id = message.from_user.id
        chat_member = await message.bot.get_chat_member(chat_id, user_id)
        return chat_member.status == types.ChatMemberStatus.ADMINISTRATOR

is_admin = IsAdminFilter()