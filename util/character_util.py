import json
from pathlib import Path
from typing import Dict, List, Optional
from ..character.character import Character

class CharacterUtil:
    """角色工具类,用于管理角色卡和角色配置
    
    Attributes:
        character_card_path (Dict[str, Path]): 角色卡文件路径字典
        character_cards (List[str]): 角色卡名称列表
        character_list (List[str]): 角色列表
        group_character_list (Dict[str, str]): 群聊角色映射
        private_character_list (Dict[str, str]): 私聊角色映射
    """

    def __init__(self) -> None:
        """初始化角色工具"""
        self.base_path = Path(__file__).parent
        self.config_file = self.base_path / "../config/characters.json"
        self.card_folder = self.base_path / "../data/character_cards/json"
        
        self.character_card_path: Dict[str, Path] = {}
        self.character_cards = self.get_character_card_list()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.character_list = config['character_list']
                self.group_character_list = dict(config['group_character_list'])
                self.private_character_list = dict(config['private_character_list'])
        except FileNotFoundError:
            raise FileNotFoundError(f"角色配置文件不存在: {self.config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"角色配置文件格式错误: {str(e)}")

    def set_init(self) -> None:
        """重新初始化角色配置"""
        self.get_character_list()
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.character_list = config['character_list']
                self.group_character_list = dict(config['group_character_list'])
                self.private_character_list = dict(config['private_character_list'])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"重新初始化角色配置失败: {str(e)}")

    def get_character_card_list(self) -> List[str]:
        """获取角色卡列表
        
        Returns:
            List[str]: 角色卡名称列表
            
        Raises:
            IOError: 读写文件失败
        """
        try:
            character_list = []
            
            for file_path in self.card_folder.glob("*.json"):
                character_name = file_path.stem
                character_list.append(character_name)
                self.character_card_path[character_name] = file_path
                
            with open(self.config_file, 'r+', encoding='utf-8') as f:
                config = json.load(f)
                config["character_list"] = character_list
                f.seek(0)
                json.dump(config, f, ensure_ascii=False, indent=4)
                f.truncate()
                
            return character_list
            
        except IOError as e:
            raise IOError(f"读写角色卡文件失败: {str(e)}") from e

    def get_character_list(self) -> Dict[str, Character]:
        """获取角色列表
        
        Returns:
            Dict[str, Character]: 角色名称到角色对象的映射
        """
        character_list = {}
        for name, path in self.character_card_path.items():
            character_list[name] = Character(str(path))
        return character_list

    async def appoint_character(
        self,
        message_type: str,
        character_name: str,
        chat_session_id: str
    ) -> str:
        """设置指定角色
        
        Args:
            message_type: 消息类型(group/private)
            character_name: 角色名称
            chat_session_id: 会话ID
            
        Returns:
            str: 设置结果消息
            
        Raises:
            IOError: 保存配置失败
        """
        try:
            with open(self.config_file, 'r+', encoding='utf-8') as f:
                config = json.load(f)
                
                if message_type == "group":
                    self.group_character_list[chat_session_id] = character_name
                    config["group_character_list"] = self.group_character_list
                elif message_type == "private":
                    self.private_character_list[chat_session_id] = character_name
                    config["private_character_list"] = self.private_character_list
                    
                f.seek(0)
                json.dump(config, f, ensure_ascii=False, indent=4)
                f.truncate()
                
            return "指定角色成功"
            
        except IOError as e:
            raise IOError(f"保存角色配置失败: {str(e)}") from e

    def get_character_by_id(
        self,
        message_type: str,
        session_id: str
    ) -> Character:
        """通过会话ID获取角色
        
        Args:
            message_type: 消息类型
            session_id: 会话ID
            
        Returns:
            Character: 角色对象
        """
        character_name = (
            self.group_character_list.get(session_id, "Sakana")
            if message_type == "group"
            else self.private_character_list.get(session_id, "Sakana")
        )
        character_card_path = self.character_card_path[character_name]
        return Character(str(character_card_path))

    def get_character_name(
        self,
        message_type: str,
        chat_user_id: str
    ) -> str:
        """获取对应角色名称
        
        Args:
            message_type: 消息类型
            chat_user_id: 用户ID
            
        Returns:
            str: 角色名称
        """
        return (
            self.group_character_list.get(chat_user_id, "Sakana")
            if message_type == "group"
            else self.private_character_list.get(chat_user_id, "Sakana")
        )


if __name__ == '__main__':
    char_util = CharacterUtil()
    print(char_util.get_character_card_list())
    print(char_util.character_card_path)
