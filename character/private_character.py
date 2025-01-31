import json
import os

from .character import Character


class PrivateCharacter(Character):

    def __init__(self):
        Character.__init__(self)

    # 设置私聊指定角色
    async def appoint_character(self, private_id: str, character: str):
        #private_character_list = dict()
        self.private_character_list[private_id] = character
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            character_list_json = json.load(f)
            character_list_json["private_character_list"] = self.private_character_list
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(character_list_json, f, ensure_ascii=False, indent=4)
        print(str(self.private_character_list))
        return "设置私聊指定角色成功"

        # 获取对应角色
    async def get_character_name(self, id: str):
         return self.private_character_list.get(id,"Sakana")


    def to_json(self, character_name):
        config_file_path = os.path.join(self.script_dir, "../config/private_character_config", f"{character_name}.json")
        with open(config_file_path, "w", encoding="utf-8") as file:
            json.dump({
                "spec": self.spec,
                "spec_version": self.spec_version,
                "data": self.data
            }, file, ensure_ascii=False, indent=4)