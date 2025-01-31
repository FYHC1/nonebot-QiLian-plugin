import json
import os

from ..user.user import User


class Messages:
    def __init__(self):
        self.user_message=""
        self.nickname=""
        self.character_name=""
        self.message_type=""
        self.preset_list=self.get_preset_list()
        self.private_preset_list=self.preset_list["private"]
        self.group_preset_list=self.preset_list["group"]



    def from_user(self, user:User):
        self.user_message = user.message
        self.nickname = user.nickname
        self.character_name = user.character_name
        self.message_type = user.message_type

    # 文件地址
    script_dir = os.path.dirname(__file__)


    def get_preset_list(self)->dict:
        preset_list = {}
        prompts_list = {}

        for message_type in ["private","group"]:
            preset_path = os.path.join(self.script_dir, f"../config/preset/{message_type}_preset.json")
            f = open(preset_path, "r", encoding="utf-8")
            preset = json.load(f)
            preset_prompts=preset["prompts"]

            preset_prompt_names=["new_chat_prompt","scenario_format","personality_format"]
            for preset_name in preset_prompt_names:
                prompts_list[preset_name]=preset[preset_name]
            for prompt in preset_prompts:
                prompts_list[f"{prompt["identifier"]}_prompt"]=prompt["content"]

            preset_list[message_type] = prompts_list



        return preset_list







    # 定义消息构造函数
    def construct_messages(self,preset_list,prompts_list,chat_history):

        # 消息队列
        messages = []
        preset=preset_list[self.message_type]
        prompts = list(prompts_list[self.character_name][self.message_type])


        character_prompts=[]
        prompt_name_list=["description","personality","scenario",\
                         "preset_enhance","prompt_newchat","first_msg"]

        for prompt in prompts:
            prompt=str(prompt).replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
            if prompt:
                character_prompts.append(prompt)


        # 添加角色卡描述为 system 消息
        for prompt in character_prompts[0:-1]:
            prompt = prompt.replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
            message = {
                "role": "system",
                "content": prompt
            }
            messages.append(message)

        character_prompts[-1] = character_prompts[-1].replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
        assistant_message = {
            "role": "assistant",
            "content": character_prompts[-1]
        }
        messages.append(assistant_message)

        #将历史记录添加为user消息
        for history_message in chat_history:
            if history_message["is_user"] == True:
                recent_message = {
                    "role": "user",
                    "content": history_message["msg"]
                }
                messages.append(recent_message)
            else:
                system_message = {
                    "role": "assistant",
                    "content": history_message["msg"]
                }
                messages.append(system_message)

        # 添加用户当前输入
        user_message = {"role": "user",
                        "content": self.user_message+preset["preset_first_person_prompt"]+preset["preset_absolute_rule_prompt"]
                        #"content": self.user_message
                        }

        # 构造完整消息队列
        messages += [user_message]
        print(messages)

        return messages


if __name__=="__main__":
    messages=Messages()
