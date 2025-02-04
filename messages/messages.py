import json
import os
from idlelib.replace import replace
from pprint import pprint

from plugins.nonebot_sillytavern_plugin import character
from ..user.user import User


class Messages:
    def __init__(self):
        self.user_message=""
        self.nickname=""
        self.character_name=""
        self.message_type=""
        #self.preset_list=self.get_preset_list()
        #self.private_preset_list=self.preset_list["private"]
        #self.group_preset_list=self.preset_list["group"]



    def from_user(self, user:User):
        self.user_message = user.message
        self.nickname = user.nickname
        self.character_name = user.character_name
        self.message_type = user.message_type

    # 文件地址
    script_dir = os.path.dirname(__file__)

    # 定义消息构造函数
    # def construct_messages(self,preset_list,prompts_list,chat_history):
    #
    #     # 消息队列
    #     messages = []
    #     preset=preset_list[self.message_type]
    #     prompts = list(prompts_list[self.character_name][self.message_type])
    #
    #
    #     character_prompts=[]
    #     prompt_name_list=["description","personality","scenario",\
    #                      "preset_enhance","prompt_newchat","first_msg"]
    #
    #     for prompt in prompts:
    #         prompt=str(prompt).replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
    #         if prompt:
    #             character_prompts.append(prompt)
    #
    #
    #     # 添加角色卡描述为 system 消息
    #     for prompt in character_prompts[0:-1]:
    #         prompt = prompt.replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
    #         message = {
    #             "role": "system",
    #             "content": prompt
    #         }
    #         messages.append(message)
    #
    #     character_prompts[-1] = character_prompts[-1].replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
    #     assistant_message = {
    #         "role": "assistant",
    #         "content": character_prompts[-1]
    #     }
    #     messages.append(assistant_message)
    #
    #     #将历史记录添加为user消息
    #     for history_message in chat_history:
    #         if history_message["is_user"] == True:
    #             recent_message = {
    #                 "role": "user",
    #                 "content": history_message["msg"]
    #             }
    #             messages.append(recent_message)
    #         else:
    #             system_message = {
    #                 "role": "assistant",
    #                 "content": history_message["msg"]
    #             }
    #             messages.append(system_message)
    #
    #     # 添加用户当前输入
    #     user_message = {"role": "user",
    #                     "content": self.user_message+preset["preset_first_person_prompt"]+preset["preset_absolute_rule_prompt"]
    #                     #"content": self.user_message
    #                     }
    #
    #     # 构造完整消息队列
    #     messages += [user_message]
    #     print(messages)
    #
    #     return messages


 # 定义消息构造函数
    def construct_messages(self,order_prompts:list,prompts_list:dict,chat_history):
        messages=[]
        character_prompts:dict=prompts_list[self.character_name]
        for prompt_name,prompt_content in character_prompts.items():
            prompt_content=str(prompt_content).replace("{{user}}", self.nickname).replace("{{char}}", self.character_name)
            character_prompts[prompt_name]=prompt_content
        chatHistory_id=order_prompts.index("chatHistory")
        order_prompts0=order_prompts[0:chatHistory_id]
        order_prompts1=order_prompts[chatHistory_id+1::]
        #['worldInfoBefore', 'personaDescription', 'charDescription', 'charPersonality',
        # 'scenario', 'worldInfoAfter', 'dialogueExamples', 'chatHistory']
        replace_prompt_list={
            'worldInfoBefore':  "",
            'personaDescription':"",
            'charDescription':character_prompts.get('description',''),
            'charPersonality':character_prompts.get('personality',''),
            'scenario':character_prompts.get('scenario',''),
            'worldInfoAfter':"",
            'dialogueExamples':"",
            'chatHistory':""
        }
        for prompt in order_prompts0:
            if isinstance(prompt, str):
                index=order_prompts0.index(prompt)
                if replace_prompt_list[prompt]!="":
                    order_prompts0[index] = {'role': 'system', 'content': replace_prompt_list[prompt]}
                else:
                    order_prompts0[index] = None
            else:
                prompt["content"] = str(prompt["content"]).replace("{{user}}", self.nickname).replace("{{char}}",
                                                                                                  self.character_name)

        for prompt in order_prompts1:
            if isinstance(prompt, str):
                index = order_prompts1.index(prompt)
                if replace_prompt_list[prompt] != "":
                    order_prompts1[index] = {'role': 'system', 'content': replace_prompt_list[prompt]}
                else:
                    order_prompts1[index] = None
            else:
                prompt["content"] = str(prompt["content"]).replace("{{user}}", self.nickname).replace("{{char}}",
                                                                                                      self.character_name)
    #将历史记录添加为user消息
        first_message = {
                    "role": "assistant",
                    "content": character_prompts['first_mes'],
                }
        messages.append(first_message)
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

        user_message = {
            "role": "user",
            "content": self.user_message
        }
        messages.append(user_message)

        messages=order_prompts0+messages+order_prompts1
        messages=[item for item in messages if item is not None]
        pprint(messages,indent=2)
        return messages






if __name__=="__main__":
    messages=Messages()
