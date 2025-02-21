from typing import List, Optional, Dict, Any
from ..character.character import Character


class ChatSession:
    """聊天会话类,用于管理单个会话的状态和配置
    
    Attributes:
        character (Character): 角色对象
        session_id (str): 会话标识符
        user_id (str): 用户ID
        nick_name (str): 用户昵称
        preset_name (str): 预设配置名称
        preset_order_prompts (List[Dict[str, Any]]): 预设提示词顺序列表
        preset_regex (List[Dict[str, Any]]): 预设正则表达式列表
    """

    def __init__(self, character: Character, session_id: str) -> None:
        """初始化聊天会话
        
        Args:
            character: 角色对象
            session_id: 会话标识符
        """
        self.character: Character = character
        self.session_id: str = session_id
        self.user_id: str = ""
        self.nick_name: str = ""
        self.preset_name: str = ""
        self.preset_order_prompts: List[Dict[str, Any]] = []
        self.preset_regex: List[Dict[str, Any]] = []

    def set_character(self, character: Character) -> None:
        """设置角色
        
        Args:
            character: 新的角色对象
        """
        self.character = character

    def set_session_id(self, session_id: str) -> None:
        """设置会话标识符
        
        Args:
            session_id: 新的会话标识符
        """
        self.session_id = session_id

    def set_user_id(self, user_id: str) -> None:
        """设置用户ID
        
        Args:
            user_id: 新的用户ID
        """
        self.user_id = user_id

    def set_preset_order_prompts(self, preset_order_prompts: List[Dict[str, Any]]) -> None:
        """设置预设提示词顺序
        
        Args:
            preset_order_prompts: 新的预设提示词顺序列表
        """
        self.preset_order_prompts = preset_order_prompts

    def set_preset_regex(self, preset_regex: List[Dict[str, Any]]) -> None:
        """设置预设正则表达式
        
        Args:
            preset_regex: 新的预设正则表达式列表
        """
        self.preset_regex = preset_regex

    def set_nick_name(self, nick_name: str) -> None:
        """设置用户昵称
        
        Args:
            nick_name: 新的用户昵称
        """
        self.nick_name = nick_name

    def get_character_name(self) -> str:
        """获取角色名称
        
        Returns:
            str: 角色名称
        """
        return self.character.get_name()

    def get_character(self) -> Character:
        """获取角色对象
        
        Returns:
            Character: 角色对象
        """
        return self.character

    def get_session_id(self) -> str:
        """获取会话标识符
        
        Returns:
            str: 会话标识符
        """
        return self.session_id

    def get_user_id(self) -> str:
        """获取用户ID
        
        Returns:
            str: 用户ID
        """
        return self.user_id

    def get_preset_order_prompts(self) -> List[Dict[str, Any]]:
        """获取预设提示词顺序
        
        Returns:
            List[Dict[str, Any]]: 预设提示词顺序列表
        """
        return self.preset_order_prompts

    def get_preset_regex(self) -> List[Dict[str, Any]]:
        """获取预设正则表达式
        
        Returns:
            List[Dict[str, Any]]: 预设正则表达式列表
        """
        return self.preset_regex

    def get_nick_name(self) -> str:
        """获取用户昵称
        
        Returns:
            str: 用户昵称
        """
        return self.nick_name

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息摘要
        
        Returns:
            Dict[str, Any]: 包含会话主要信息的字典
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "nick_name": self.nick_name,
            "character_name": self.get_character_name(),
            "preset_name": self.preset_name
        }

    def update_session(self, **kwargs: Any) -> None:
        """更新会话属性
        
        Args:
            **kwargs: 要更新的属性键值对
            
        Raises:
            AttributeError: 属性不存在
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"ChatSession没有属性: {key}")

    def clear_session(self) -> None:
        """清空会话数据"""
        self.user_id = ""
        self.nick_name = ""
        self.preset_name = ""
        self.preset_order_prompts = []
        self.preset_regex = []