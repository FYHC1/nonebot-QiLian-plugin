import json
import os

from .character import Character


class GroupCharacter(Character):

    def __init__(self):
        Character.__init__(self)

    # 设置群聊指定角色
    async def appoint_character(self, group_id: str, character: str):
        #group_character_list = dict()
        self.group_character_list[group_id] = character
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            character_list_json = json.load(f)
            character_list_json["group_character_list"] = self.group_character_list
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(character_list_json, f, ensure_ascii=False, indent=4)
        print(str(self.group_character_list))
        return "设置群聊指定角色成功"

    # 获取对应角色
    async def get_character(self, id: str):
        return self.group_character_list[id]


    def to_json(self, character_name:str):
        config_file_path = os.path.join(self.script_dir, "../config/group_character_config", f"{character_name}.json")
        with open(config_file_path, "w", encoding="utf-8") as file:
            json.dump({
                "spec": self.spec,
                "spec_version": self.spec_version,
                "data": self.data
            }, file, ensure_ascii=False, indent=4)