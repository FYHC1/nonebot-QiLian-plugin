import json
import os

from pprint import pprint

from ..chat.chat_session import ChatSession


class Messages:
    def __init__(self):
        self.user_message=""
        self.nickname=""
        self.character_name=""
        self.message_type=""





    # 文件地址
    script_dir = os.path.dirname(__file__)

     # 定义消息构造函数
    async def construct_messages(self,message:str,chat_session:ChatSession,chat_history):
        messages=[]
        character=chat_session.get_character()
        nickname=chat_session.get_nick_name()
        character_name=character.get_name()
         #description=character.get_description().replace("{{user}}",nickname).replace("{{char}}",character_name)

        order_prompts=chat_session.get_preset_order_prompts()
        chatHistory_id=order_prompts.index("chatHistory")
        order_prompts0=order_prompts[0:chatHistory_id]
        order_prompts1=order_prompts[chatHistory_id+1::]
        #['worldInfoBefore', 'personaDescription', 'charDescription', 'charPersonality',
        # 'scenario', 'worldInfoAfter', 'dialogueExamples', 'chatHistory']
        replace_prompt_list={
            'worldInfoBefore':"",
            'personaDescription':"",
            'charDescription':character.get_description().replace("{{user}}",nickname).replace("{{char}}",character_name),
            'charPersonality':character.get_personality().replace("{{user}}", chat_session.get_nick_name()).replace("{{char}}",character.get_name()),
            'scenario':character.get_scenario().replace("{{user}}", chat_session.get_nick_name()).replace("{{char}}",character.get_name()),
            'worldInfoAfter':"",
            'dialogueExamples':character.get_mes_example().replace("{{user}}", str(chat_session.get_nick_name())).replace("{{char}}",str(character.get_name())),
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
                prompt["content"] = str(prompt["content"]).replace("{{user}}", chat_session.get_nick_name()).replace("{{char}}",
                                                                                                      character.get_name())
    #将历史记录添加为user消息
        first_message = {
                    "role": "assistant",
                    "content": character.get_first_message().replace("{{user}}", chat_session.get_nick_name()).replace("{{char}}",character.get_name())
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
            "content": message
        }
        messages.append(user_message)

        messages=order_prompts0+messages+order_prompts1
        messages=[item for item in messages if item is not None]
        #pprint(messages,indent=2)
        return messages






if __name__=="__main__":
    messages=Messages()
