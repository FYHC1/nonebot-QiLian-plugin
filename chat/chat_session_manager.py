from typing import Dict, List, Optional, Any
from nonebot.adapters.onebot.v11 import Bot

from ..character.character import Character
from .chat_session import ChatSession
from ..preset.QLPreset_manage import QLPresetManager

class ChatSessionManager:
    """聊天会话管理器类,用于管理所有会话
    
    Attributes:
        group_session_list (Dict[str, ChatSession]): 群聊会话字典
        private_session_list (Dict[str, ChatSession]): 私聊会话字典
        session_keys (List[str]): 活跃会话ID列表
        preset_manage (QLPresetManager): 预设管理器实例
    """

    def __init__(self) -> None:
        """初始化会话管理器"""
        self.group_session_list: Dict[str, ChatSession] = {}
        self.private_session_list: Dict[str, ChatSession] = {}
        self.session_keys: List[str] = []
        self.preset_manage = QLPresetManager()

    def get_session(self, message_type: str, session_id: str) -> Optional[ChatSession]:
        """获取指定会话
        
        Args:
            message_type: 消息类型(group/private)
            session_id: 会话ID
            
        Returns:
            Optional[ChatSession]: 会话对象,不存在则返回None
            
        Raises:
            ValueError: 消息类型无效
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        session_list = (
            self.group_session_list if message_type == "group" 
            else self.private_session_list
        )
        return session_list.get(session_id)

    def create_session(
        self,
        message_type: str,
        character: Character,
        session_id: str,
    ) -> ChatSession:
        """创建新会话
        
        Args:
            message_type: 消息类型
            character: 角色对象
            session_id: 会话ID
            user_id: 用户ID
            nickname: 用户昵称
            
        Returns:
            ChatSession: 新创建的会话对象
            
        Raises:
            ValueError: 消息类型无效
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        session = ChatSession(
            character=character,
            session_id=session_id
        )
        session.update_session(
            # user_id=user_id,
            # nick_name=nickname,
            preset_order_prompts=self.preset_manage.get_order_prompts(
                message_type, 
                session_id
            ),
            preset_name=self.preset_manage.get_preset_name(
                message_type,
                session_id
            )
        )
        
        if message_type == "group":
            self.group_session_list[session_id] = session
        else:
            self.private_session_list[session_id] = session
            
        if session_id not in self.session_keys:
            self.session_keys.append(session_id)
            
        return session

    async def get_nick_name(self, bot: Bot, user_id: str) -> str:
        """获取用户昵称
        
        Args:
            bot: Bot实例
            user_id: 用户ID
            
        Returns:
            str: 用户昵称
            
        Raises:
            RuntimeError: 获取用户信息失败
        """
        try:
            user_info = await bot.call_api(
                "get_stranger_info",
                user_id=user_id
            )
            return user_info.get('nickname', '未知昵称')
        except Exception as e:
            raise RuntimeError(f"获取用户昵称失败: {str(e)}") from e

    def remove_session(self, message_type: str, session_id: str) -> bool:
        """移除指定会话
        
        Args:
            message_type: 消息类型
            session_id: 会话ID
            
        Returns:
            bool: 是否成功移除
            
        Raises:
            ValueError: 消息类型无效
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        session_list = (
            self.group_session_list if message_type == "group"
            else self.private_session_list
        )
        
        if session_id in session_list:
            del session_list[session_id]
            if session_id in self.session_keys:
                self.session_keys.remove(session_id)
            return True
        return False

    def clear_sessions(self) -> None:
        """清空所有会话"""
        self.group_session_list.clear()
        self.private_session_list.clear()
        self.session_keys.clear()

    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计信息
        
        Returns:
            Dict[str, Any]: 会话统计信息
        """
        return {
            "total_sessions": len(self.session_keys),
            "group_sessions": len(self.group_session_list),
            "private_sessions": len(self.private_session_list),
            "active_sessions": self.session_keys
        }

    def set_group_session(self, group_id, chat_session):
        self.group_session_list[group_id] = chat_session

    def set_private_session(self, user_id, chat_session):
        self.private_session_list[user_id] = chat_session

