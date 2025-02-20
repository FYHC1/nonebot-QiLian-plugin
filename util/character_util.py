import json
import os

from ..character.character import Character


class CharacterUtil(object):
    # 文件地址
    script_dir = os.path.dirname(__file__)
    config_file_path = os.path.join(script_dir, "../config", "characters.json")
    folder_path = os.path.join(script_dir, "../data/character_cards/json")
    card_json_dir = os.path.join(script_dir, '../data/character_cards/json')

    def __init__(self):
        self.character_card_path = {}
        self.character_cards = self.get_character_card_list()
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            character_config = json.load(f)
            self.character_list = character_config['character_list']
            self.group_character_list = dict(character_config['group_character_list'])
            self.private_character_list = dict(character_config['private_character_list'])

    def set_init(self):
        self.get_character_list()
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            character_config = json.load(f)
            self.character_list = character_config['character_list']
            self.group_character_list = dict(character_config['group_character_list'])
            self.private_character_list = dict(character_config['private_character_list'])

    # 获取角色卡列表
    def get_character_card_list(self):
        list_dir = os.listdir(self.folder_path)
        character_list = []

        for file in list_dir:
            if os.path.isfile(os.path.join(self.folder_path, file)):
                character_name = str(file).split(".json")[0]
                character_list.append(character_name)
                self.character_card_path[character_name] = os.path.join(self.folder_path, file)
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    character_list_json = json.load(f)
                    character_list_json["character_list"] = character_list
                    with open(self.config_file_path, 'w', encoding='utf-8') as f:
                        json.dump(character_list_json, f, ensure_ascii=False, indent=4)
        return character_list

    #获取角色列表
    def get_character_list(self):
        character_list = {}
        for name, path in self.character_card_path.items():
            character_list[name] = Character(path)
        return character_list

    # 设置指定角色
    async def appoint_character(self, message_type: str, character_name: str, chat_session_id: str):
        # self.private_character_list[chat_session_id] = character_name
        # with open(self.config_file_path, 'r', encoding='utf-8') as f:
        #     character_list_json = json.load(f)
        #     character_list_json["private_character_list"] = self.private_character_list
        #     with open(self.config_file_path, 'w', encoding='utf-8') as f:
        #         json.dump(character_list_json, f, ensure_ascii=False, indent=4)
        # print(str(self.private_character_list))
        # return "设置私聊指定角色成功"

        with open(self.config_file_path, 'r+', encoding='utf-8') as f:
            character_list_json = json.load(f)
            if message_type == "group":
                self.group_character_list[chat_session_id] = character_name
                character_list_json["group_character_list"] = self.group_character_list
            elif message_type == "private":
                self.private_character_list[chat_session_id] = character_name
                character_list_json["private_character_list"] = self.private_character_list
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(character_list_json, f, ensure_ascii=False, indent=4)
            return "指定角色成功"

    def get_character_by_id(self, message_type, session_id: str):
        if message_type == "group":
            character_name = self.group_character_list.get(session_id, "Sakana")
        else:
            character_name = self.private_character_list.get(session_id)
        character_card_path = self.character_card_path[character_name]
        character = Character(character_card_path)
        return character

    #获取对应角色
    def get_character_name(self, message_type: str, chat_user_id: str):
        if message_type == "group":
            return self.group_character_list.get(chat_user_id, "Sakana")
        else:
            return self.private_character_list.get(chat_user_id, "Sakana")


if __name__ == '__main__':
    char_util = CharacterUtil()
    print(char_util.get_character_card_list())
    print(char_util.character_card_path)
