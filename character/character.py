import json
import os

from websockets import connect

from .character_card import CharacterCard


class Character(CharacterCard):
    #文件地址
    script_dir = os.path.dirname(__file__)
    config_file_path = os.path.join(script_dir, "../config", "characters.json")
    folder_path = os.path.join(script_dir, "../data/character_cards/json")
    card_json_dir = os.path.join(script_dir, '../data/character_cards/json')

    def __init__(self):
        self.character_card_path = {}
        self.character_list = []
        self.group_character_list = {}
        self.private_character_list = {}
        self.preset_list={}
        self.prompts_list = {}
        self.set_init()

    def set_init(self):
        self.get_character_list()
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            character_config = json.load(f)
            self.character_list = character_config['character_list']
            self.group_character_list = dict(character_config['group_character_list'])
            self.private_character_list = dict(character_config['private_character_list'])
            self.preset_list = self.get_preset_list()
            self.prompts_list = self.get_prompts_list()

    # 获取角色卡列表

    def get_character_list(self):
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

    #获取对应角色
    def get_charactername(self, message_type: str, chat_user_id: str):
        if message_type == "group":
            return self.group_character_list.get(chat_user_id, "Sakana")
        else:
            return self.private_character_list.get(chat_user_id, "Sakana")

    #设置世界书
    def set_world_book(self):
        pass

    def to_json(self, character_name):
        config_file_path = os.path.join(self.script_dir, "../config/private_character_config", f"{character_name}.json")
        with open(config_file_path, "w", encoding="utf-8") as file:
            json.dump({
                "spec": self.spec,
                "spec_version": self.spec_version,
                "data": self.data
            }, file, ensure_ascii=False, indent=4)

    def get_preset_list(self) -> dict:
        preset_list = {}
        for message_type in ["private", "group"]:
            prompts_list = {}
            preset_prompts_list = {}
            preset_path = os.path.join(self.script_dir, f"../config/preset/{message_type}_preset.json")
            f = open(preset_path, "r", encoding="utf-8")
            preset = json.load(f)
            preset_prompts = preset["prompts"]
            preset_prompt_names = ["description_format", "new_chat_prompt", "scenario_format", "personality_format"]
            for preset_name in preset_prompt_names:
                prompts_list[preset_name] = preset.get(preset_name, "")
            for prompt in preset_prompts:
                prompts_list[f"preset_{prompt["identifier"]}_prompt"] = prompt["content"]
            preset_list[message_type] = prompts_list
            #print(prompts_list)
            # print(message_type)
            #print(preset_list)
        return preset_list

    def get_prompts_list(self):
        list_dir = os.listdir(self.card_json_dir)
        prompts = {}

        for character_name in self.character_list:
            if f"{character_name}.json" in list_dir:
                character_card = CharacterCard.from_json(os.path.join(self.card_json_dir, f"{character_name}.json"))
                preset_list = self.get_preset_list()
                prompt_name_list = ["preset_main_prompt", "description", "personality", \
                                    "scenario", "preset_other_prompt","new_chat", "first_mes"]
                summary = dict(character_card.display_summary())
                character_prompts = {}
                for message_type in ["private", "group"]:
                    character_prompt = []
                    preset = dict(preset_list.get(message_type, {}))
                    summary["preset_main_prompt"] = preset["preset_main_prompt"]
                    summary["description"] = preset["description_format"] + summary["description"]
                    if summary["personality"]:
                        summary["personality"] = preset["personality_format"] + summary["personality"]
                    if summary["scenario"]:
                        summary["scenario"] = preset["scenario_format"] + summary["scenario"]
                    summary["preset_other_prompt"]=preset["preset_nsfw_prompt"]+ preset["preset_enhance_prompt"]
                    summary["new_chat"] = preset["new_chat_prompt"]
                    for prompt_name in prompt_name_list:
                        character_prompt.append(summary[prompt_name])
                    character_prompts[message_type] =character_prompt

                prompts[character_name] = character_prompts
                #print(prompts)

        return prompts


if __name__ == '__main__':
    character = Character()
    # print(character.character_list)
    # print(character.group_character_list)
    # print(character.private_character_list)
    # print(character.get_prompts_list())
    #character.get_prompts_list()
