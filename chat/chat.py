import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

from nonebot.plugin import Plugin

from ..character.character import Character
#from ..user.user import User

# 设置聊天记录文件保存地址

script_dir = os.path.dirname(os.path.realpath(__file__))
group_chatmessage_path = os.path.join(script_dir, "../data/chat_data/group_chat")
private_chatmessage_path = os.path.join(script_dir, "../data/chat_data/private_chat")


class Chat:
    """聊天记录管理类,用于处理和存储聊天记录
    
    Attributes:
        message_type (str): 消息类型(group/private)
        chat_user_id (str): 聊天用户ID
        user_id (str): 用户ID
        character_name (str): 角色名称
        nickname (str): 用户昵称
        message (str): 消息内容
        depth (int): 对话深度
    """

    def __init__(self) -> None:
        """初始化聊天记录管理器"""
        self.message_type: str = ''
        self.chat_user_id: str = ''
        self.user_id: str = ''
        self.character_name: str = ''
        self.nickname: str = ''
        self.message: str = ''
        self.depth: int = 8





    # def from_user(self,user:User):
    #     self.message_type = user.message_type
    #     self.chat_user_id = user.chat_user_id
    #     self.user_id = user.user_id
    #     self.character_name = user.character_name
    #     self.nickname = user.nickname
    #     self.message = user.message



    ###
    #
    #新建聊天记录
    async def new_chat(
        self,
        message_type: str,
        chat_user_id: str,
        character_name: str
    ) -> None:
        """创建新的聊天记录文件
        
        Args:
            message_type: 消息类型(group/private)
            chat_user_id: 聊天用户ID
            character_name: 角色名称
            
        Raises:
            ValueError: 消息类型无效
            IOError: 文件创建失败
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")

        try:
            chat_dir = self._get_chat_dir(message_type)
            filename = f"{message_type}-{chat_user_id}-{character_name}.jsonl"
            
            if filename not in os.listdir(chat_dir):
                filepath = os.path.join(chat_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    print(f"创建新聊天记录文件: {filepath}")
                    
        except IOError as e:
            raise IOError(f"创建聊天记录文件失败: {str(e)}") from e






    #保存聊天记录
    async def save_chat_message(
        self,
        message_type: str,
        chat_user_id: str,
        nickname: str,
        character_name: str,
        message: str,
        assistant_reply: str
    ) -> None:
        """保存聊天消息
        
        Args:
            message_type: 消息类型
            chat_user_id: 聊天用户ID
            nickname: 用户昵称
            character_name: 角色名称
            message: 用户消息
            assistant_reply: 助手回复
            
        Raises:
            ValueError: 消息类型无效
            IOError: 保存失败
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")

        try:
            chat_dir = self._get_chat_dir(message_type)
            filename = f"{message_type}-{chat_user_id}-{character_name}.jsonl"
            
            if filename in os.listdir(chat_dir):
                filepath = os.path.join(chat_dir, filename)
                with open(filepath, 'a+', encoding='utf-8') as f:
                    now = datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
                    
                    # 保存用户消息
                    user_msg = {
                        "name": nickname,
                        "is_user": True,
                        "user_id": chat_user_id,
                        "is_system": False,
                        "msg": message,
                        "create_date": now
                    }
                    f.write(json.dumps(user_msg, ensure_ascii=False) + '\n')
                    
                    # 保存助手回复
                    assistant_msg = {
                        "name": character_name,
                        "is_user": False,
                        "user_id": chat_user_id,
                        "msg": assistant_reply,
                        "create_date": now
                    }
                    f.write(json.dumps(assistant_msg, ensure_ascii=False) + '\n')
                    
        except IOError as e:
            raise IOError(f"保存聊天记录失败: {str(e)}") from e





    #获取上下文
    async def get_context(
        self,
        message_type: str,
        chat_user_id: str,
        character_name: str
    ) -> List[Dict[str, Union[str, bool]]]:
        """获取聊天上下文
        
        Args:
            message_type: 消息类型
            chat_user_id: 聊天用户ID
            character_name: 角色名称
            
        Returns:
            List[Dict[str, Union[str, bool]]]: 聊天上下文列表
            
        Raises:
            ValueError: 消息类型无效
            IOError: 读取失败
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")

        context = []
        try:
            chat_dir = self._get_chat_dir(message_type)
            filename = f"{message_type}-{chat_user_id}-{character_name}.jsonl"
            filepath = os.path.join(chat_dir, filename)
            
            if not os.path.exists(filepath):
                await self.new_chat(message_type, chat_user_id, character_name)
                return context
                
            if os.path.getsize(filepath) == 0:
                return context
                
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-self.depth:]  # 获取最近的depth条记录
                for line in lines:
                    chat_note = json.loads(line)
                    context.append({
                        "name": chat_note["name"],
                        "is_user": chat_note["is_user"],
                        "msg": chat_note["msg"]
                    })
                    
            return context
            
        except IOError as e:
            raise IOError(f"读取聊天记录失败: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"聊天记录格式错误: {str(e)}") from e



    #清空聊天记录
    async def clear_chat_message(
        self,
        message_type: str,
        chat_user_id: str,
        character_name: str
    ) -> None:
        """清空聊天记录
        
        Args:
            message_type: 消息类型
            chat_user_id: 聊天用户ID
            character_name: 角色名称
            
        Raises:
            ValueError: 消息类型无效
            IOError: 操作失败
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")

        try:
            chat_dir = self._get_chat_dir(message_type)
            filename = f"{message_type}-{chat_user_id}-{character_name}.jsonl"
            filepath = os.path.join(chat_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                print("聊天记录已清除")
                
        except IOError as e:
            raise IOError(f"清除聊天记录失败: {str(e)}") from e

    def _get_chat_dir(self, message_type: str) -> str:
        """获取聊天记录目录路径
        
        Args:
            message_type: 消息类型
            
        Returns:
            str: 目录路径
            
        Raises:
            ValueError: 消息类型无效
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return os.path.join(
            base_dir,
            "data/chat_data",
            f"{message_type}_chat"
        )


