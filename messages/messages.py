import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from pprint import pprint

from ..chat.chat_session import ChatSession


class Messages:
    """消息构造器类,用于构建和管理聊天消息
    
    Attributes:
        user_message (str): 用户消息
        nickname (str): 用户昵称
        character_name (str): 角色名称
        message_type (str): 消息类型
    """

    def __init__(self) -> None:
        """初始化消息构造器"""
        self.user_message: str = ""
        self.nickname: str = ""
        self.character_name: str = ""
        self.message_type: str = ""

    # 文件地址
    script_dir = os.path.dirname(__file__)

    async def construct_messages(
        self,
        message: str,
        chat_session: ChatSession,
        chat_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """构造消息列表
        
        Args:
            message: 当前消息
            chat_session: 聊天会话对象
            chat_history: 聊天历史记录
            
        Returns:
            List[Dict[str, Any]]: 构造的消息列表
        """
        messages = []
        character = chat_session.get_character()
        nickname = chat_session.get_nick_name()
        character_name = character.get_name()
         #description=character.get_description().replace("{{user}}",nickname).replace("{{char}}",character_name)

        order_prompts = chat_session.get_preset_order_prompts()
        chatHistory_id = order_prompts.index("chatHistory")
        order_prompts0 = order_prompts[0:chatHistory_id]
        order_prompts1 = order_prompts[chatHistory_id+1:]
        #['worldInfoBefore', 'personaDescription', 'charDescription', 'charPersonality',
        # 'scenario', 'worldInfoAfter', 'dialogueExamples', 'chatHistory']
        replace_prompt_list = {
            'worldInfoBefore': "",
            'personaDescription': "",
            'charDescription': character.get_description().replace(
                "{{user}}", nickname
            ).replace(
                "{{char}}", character_name
            ),
            'charPersonality': character.get_personality().replace(
                "{{user}}", nickname
            ).replace(
                "{{char}}", character_name
            ),
            'scenario': character.get_scenario().replace(
                "{{user}}", nickname
            ).replace(
                "{{char}}", character_name
            ),
            'worldInfoAfter': "",
            'dialogueExamples': character.get_mes_example().replace(
                "{{user}}", nickname
            ).replace(
                "{{char}}", character_name
            ),
            'chatHistory': ""
        }
        for i, prompt in enumerate(order_prompts0):
            if isinstance(prompt, str):
                if replace_prompt_list[prompt]:
                    order_prompts0[i] = {
                        'role': 'system',
                        'content': replace_prompt_list[prompt]
                    }
                else:
                    order_prompts0[i] = None
            else:
                prompt["content"] = str(prompt["content"]).replace(
                    "{{user}}", nickname
                ).replace(
                    "{{char}}", character_name
                )

        for i, prompt in enumerate(order_prompts1):
            if isinstance(prompt, str):
                if replace_prompt_list[prompt]:
                    order_prompts1[i] = {
                        'role': 'system',
                        'content': replace_prompt_list[prompt]
                    }
                else:
                    order_prompts1[i] = None
            else:
                prompt["content"] = str(prompt["content"]).replace(
                    "{{user}}", nickname
                ).replace(
                    "{{char}}", character_name
                )
    #将历史记录添加为user消息
        first_message = {
                    "role": "assistant",
                    "content": character.get_first_message().replace(
                        "{{user}}", nickname
                    ).replace(
                        "{{char}}", character_name
                    )
                }
        messages.append(first_message)
        for history_message in chat_history:
            messages.append({
                "role": "user" if history_message["is_user"] else "assistant",
                "content": history_message["msg"]
            })

        user_message = {
            "role": "user",
            "content": message
        }
        messages.append(user_message)

        messages = order_prompts0 + messages + order_prompts1
        messages = [item for item in messages if item is not None]
        pprint(messages,indent=2)
        return messages






if __name__=="__main__":
    messages=Messages()
