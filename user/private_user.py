import json
import os

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot

from ..character.character import Character
from .user import User


class PrivateUser(User):
    def __init__(self):
        self.message_type = 'private'
        self.chat_user_id= ''
        self.user_id=''
        self.nickname=''
        self.message=''
        self.character=Character()
        self.character_name='Sakana'


    def set_chat_user(self,user_id:str):
        self.chat_user_id=user_id

    def set_user_id(self,user_id:str):
        self.user_id=user_id

    async def set_nickname(self,bot:Bot):
        self.nickname=await self.get_nickname(bot,self.user_id)

    def set_character_name(self):
        self.character_name= self.character.private_character_list.get(self.chat_user_id, "Sakana")





        # 设置私聊指定角色
    async def appoint_character(self,character_name:str ):
        # private_character_list = dict()
        self.character.private_character_list[self.chat_user_id] = character_name
        with open(self.character.config_file_path, 'r', encoding='utf-8') as f:
            character_list_json = json.load(f)
            character_list_json["private_character_list"] = self.character.private_character_list
            with open(self.character.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(character_list_json, f, ensure_ascii=False, indent=4)
        print(str(self.character.private_character_list))
        return "设置私聊指定角色成功"



    # def get_character_name(self, chat_user: str):
    #      return self.character.private_character_list.get(chat_user, None)

    def get_character_card(self):
        pass









    # def __init__(self,event:MessageEvent,bot:Bot):
    #     self.chat_user=str(event.user_id)
    #     self.user_id=str(event.user_id)
    #     self.nickname=self.get_nickname(bot)
    #     self.character=Character()
    #     self.character_name=self.character.get_character_name(self.chat_user)
