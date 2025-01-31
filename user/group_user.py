import json

from nonebot.adapters.onebot.v11.bot import Bot

from ..character.character import Character
from .user import User


class GroupUser(User):
    def __init__(self):
        self.message_type = 'group'
        self.chat_user_id = ''
        self.user_id = ''
        self.nickname = ''
        self.message=''
        self.character = Character()
        self.character_name = 'Sakana'



    def set_chat_user(self,group_id:str):
        self.chat_user_id=group_id

    def set_user_id(self,user_id:str):
        self.user_id=user_id

    async def set_nickname(self,bot:Bot):
        self.nickname=await self.get_nickname(bot,self.user_id)

    def set_character_name(self):
        self.character_name= self.character.group_character_list.get(self.chat_user_id, "Sakana")



    # 设置群聊指定角色
    async def appoint_character(self, character_name: str):
        # group_character_list = dict()
        self.character.group_character_list[self.chat_user_id] = character_name
        with open(self.character.config_file_path, 'r', encoding='utf-8') as rf:
            character_list_json = json.load(rf)
            character_list_json["group_character_list"] = self.character.group_character_list
            with open(self.character.config_file_path, 'w', encoding='utf-8') as wf:
                json.dump(character_list_json, wf, ensure_ascii=False, indent=4)
        print(str(self.character.group_character_list))
        return "设置群聊指定角色成功"
