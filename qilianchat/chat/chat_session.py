from ..character.character import Character


class ChatSession:
    def __init__(self, character,session_id):
        self.character:Character=character
        self.session_id:str=session_id
        self.user_id:str=""
        self.nick_name:str=""
        self.preset_name:str=""
        self.preset_order_prompts:list=[]
        self.preset_regex:list=[]



    def set_character(self,character:Character):
        self.character = character

    def set_session_id(self,session_id:str):
        self.session_id = session_id

    def set_user_id(self,user_id:str):
        self.user_id = user_id

    def set_preset_order_prompts(self,preset_order_prompts:list):
        self.preset_order_prompts =  preset_order_prompts

    def set_preset_regex(self,preset_regex:list):
        self.preset_regex = preset_regex

    def set_nick_name(self,nick_name:str):
        self.nick_name = nick_name

    def get_character_name(self):
        return self.character.get_name()

    def get_character(self):
        return self.character

    def get_session_id(self):
        return self.session_id

    def get_user_id(self):
        return self.user_id

    def get_preset_order_prompts(self):
        return self.preset_order_prompts

    def get_preset_regex(self):
        return self.preset_regex

    def get_nick_name(self):
        return self.nick_name