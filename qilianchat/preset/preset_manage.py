import json
import os
from idlelib.iomenu import encoding

from click import prompt


class PresetManage():
    script_dir = os.path.dirname(__file__)
    QL_preset_floder_path = os.path.join(script_dir, "../config/preset/QL_preset")

    def __init__(self):
        self.preset_name: str =""
        self.preset: dict = {}
        self.preset_config = {}

    @staticmethod
    def get_preset_list():
        script_dir = os.path.dirname(__file__)
        QL_preset_floder_path = os.path.join(script_dir, "../config/preset/QL_preset")
        preset_folder = os.listdir(QL_preset_floder_path)
        preset_list = []
        for preset in preset_folder:
            if os.path.isfile(os.path.join(QL_preset_floder_path, preset)):
                preset_name = preset.split(".json")[0]
                preset_list.append(preset_name)
        return preset_list

    # def set_init(self,message_type):
    #     self.preset_name: str = self.get_preset_name(message_type)
    #     self.preset: dict = self.get_preset(message_type)
    #     self.preset_config = self.config_from_json()

    def set_preset_config(self, message_type:str,session_id:str,preset_name:str):
        preset_config_path = os.path.join(self.script_dir, f'../config/preset/preset_config/preset_config.json')
        with open(preset_config_path, 'r+', encoding='utf-8') as f:
            preset_config: dict = json.load(f)
        with open(preset_config_path, 'w+', encoding='utf-8') as wf:
            preset_config[message_type][session_id] = preset_name
            json.dump(preset_config, wf,ensure_ascii=False, indent=4)


    def get_preset_name(self,message_type,session_id):
        preset_config_path = os.path.join(self.script_dir, "../config/preset/preset_config/preset_config.json")
        preset_config: dict = {}
        with open(preset_config_path, "r", encoding='utf-8') as f:
            preset_config:dict= json.load(f)[message_type]
            return preset_config.get(session_id,"Gemini!_It's_MyGO!!!!!_1.9.2版")

    def get_preset(self,preset_name) -> dict:
        preset_path = os.path.join(self.QL_preset_floder_path, f"{preset_name}.json")
        with open(preset_path, "r", encoding='utf-8') as f:
            preset: dict = json.load(f)
        return preset

    def get_prompt_order(self,message_type,session_id):
        preset_name = self.get_preset_name(message_type,session_id)
        prompt_orders_path = os.path.join(self.script_dir,
                                          f"../config/preset/preset_prompt_orders/{preset_name}/{message_type}_prompt_order.json")
        with open(prompt_orders_path, "r", encoding='utf-8') as f:
            prompt_order = json.load(f)["order"]
            return prompt_order

    def get_order_prompts(self, message_type,session_id)->list:
        preset_name = self.get_preset_name(message_type,session_id)
        preset_prompts: dict = self.get_preset(preset_name).get("prompts")
        prompt_order = self.get_prompt_order(message_type,session_id)
        order_prompts = []
        marker_list=[]
        for item in prompt_order:
            if item["enabled"] == True:
                prompt = preset_prompts.get(item["name"])
                if prompt["marker"] != True:
                    if item["identifier"] == prompt["identifier"]:
                        order_prompts.append({"role": prompt["role"], "content": prompt["content"]})
                else:
                    if item["identifier"] == prompt["identifier"]:
                        order_prompts.append(prompt["identifier"])
                        marker_list.append(prompt["identifier"])

        #return marker_list
        #print(order_prompts)
        return order_prompts

    def config_from_json(self):
        preset_config_path = os.path.join(self.script_dir, "../config/preset/preset_config/preset_config.json")
        with open(preset_config_path, "r", encoding='utf-8') as f:
            preset_config: dict = json.load(f)
            return preset_config

    def config_to_json(self):
        preset_config_path = os.path.join(self.script_dir, "../config/preset/preset_config/preset_config.json")
        with open(preset_config_path, "w", encoding='utf-8') as f:
            json.dump(self.preset_config, f)


if __name__ == "__main__":
     preset = PresetManage()
    # print(preset.get_preset_name())
    # # print(preset.get_preset())
    # print(preset.get_preset_list())
    # print(preset.get_prompt_order())
    # print(preset.get_order_prompts())
    # print(preset.get_order_prompts().index("chatHistory"))
    # print(preset.get_order_prompts()[0:12])
    # print(preset.get_order_prompts()[12+1::])
