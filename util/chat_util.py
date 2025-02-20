from nonebot.adapters.onebot.v11 import Bot

from ..character.character import Character
from ..chat.chat_session import ChatSession
from ..preset.preset_manage import PresetManage


class ChatUtil(object):
    def __init__(self):
        self.group_session_list:dict={}
        self.private_session_list:dict={}
        self.session_keys:list=[]
        self.preset_manage=PresetManage()


    def set_group_session(self,session_id,session:ChatSession):
        self.group_session_list[session_id] = session

    def set_private_session(self,session_id,session:ChatSession):
        self.private_session_list[session_id] = session

    def get_group_session(self,session_id:str):
        if session_id in self.session_keys:
            return self.group_session_list.get(session_id,False)

    def get_private_session(self, session_id: str):
        if session_id in self.session_keys:
            return self.group_session_list.get(session_id, False)

    def assign_session(self,message_type:str,character:Character,session_id:str):
        chat_session=ChatSession(character,session_id)
        chat_session.set_preset_order_prompts(self.preset_manage.get_order_prompts(message_type,session_id))
        chat_session.preset_name=self.preset_manage.get_preset_name(message_type,session_id)
        return chat_session

    async def get_nick_name(self,bot:Bot,user_id):
        user_info = await bot.call_api("get_stranger_info", user_id=user_id)
        nickname = user_info.get('nickname', '未知昵称')
        return nickname

    def set_preset(self,preset_name:str):
        pass

