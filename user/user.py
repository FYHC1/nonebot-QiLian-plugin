from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot

from ..character.character import Character


class User:
    def __init__(self):
        self.message_type=''
        self.chat_user_id = ''
        self.user_id = ''
        self.nickname = ''
        self.message = ''
        self.character = Character()
        self.character_name = 'Sakana'

    def get_character_card(self):
        pass

    def set_nickname(self,bot:Bot):
        pass

    def set_character_name(self):
       pass


    async def get_nickname(self,bot:Bot,user_id):
        user_info = await bot.call_api("get_stranger_info", user_id=user_id)
        nickname = user_info.get('nickname', '未知昵称')
        return nickname

    async def appoint_character(self, character_name: str):
        pass