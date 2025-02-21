import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from click import prompt


class QLPresetManager():
    """预设管理器类,用于管理聊天预设配置
    
    Attributes:
        config_path (Path): 预设配置文件路径
        preset_config (Dict[str, Dict[str, str]]): 预设配置数据
        default_preset_name (str): 默认预设名称
        script_dir (Path): 脚本所在目录
        preset_folder_path (Path): 预设文件夹路径
    """

    def __init__(self) -> None:
        """初始化预设管理器"""
        self.script_dir = Path(__file__).parent
        self.config_path = self.script_dir / "preset_config" / "preset_config.json"
        self.preset_folder_path = self.script_dir / "../config/preset/QL_preset"
        self.preset_config = self._load_preset_config()
        self.default_preset_name = "default"
        self.preset_name: str =""
        self.preset: dict = {}

    def _load_preset_config(self) -> Dict[str, Dict[str, str]]:
        """加载预设配置文件
        
        Returns:
            Dict[str, Dict[str, str]]: 预设配置数据
            
        Raises:
            json.JSONDecodeError: 配置文件格式错误
        """
        try:
            if not self.config_path.exists():
                return {"private": {}, "group": {}}
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"预设配置文件格式错误: {str(e)}", 
                e.doc, 
                e.pos
            )

    def _save_preset_config(self) -> None:
        """保存预设配置到文件
        
        Raises:
            IOError: 保存失败
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.preset_config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"保存预设配置失败: {str(e)}") from e

    def get_preset_name(self, message_type: str, chat_id: str) -> str:
        """获取指定会话的预设名称
        
        Args:
            message_type: 消息类型(group/private)
            chat_id: 会话ID
            
        Returns:
            str: 预设名称
            
        Raises:
            ValueError: 消息类型无效
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        return self.preset_config.get(message_type, {}).get(
            chat_id, 
            self.default_preset_name
        )

    def set_preset_name(
        self, 
        message_type: str, 
        chat_id: str, 
        preset_name: str
    ) -> None:
        """设置指定会话的预设名称
        
        Args:
            message_type: 消息类型
            chat_id: 会话ID
            preset_name: 预设名称
            
        Raises:
            ValueError: 消息类型无效
            FileNotFoundError: 预设文件不存在
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        preset_path = (
            Path(__file__).parent / 
            "preset_prompt_orders" / 
            preset_name
        )
        if not preset_path.exists():
            raise FileNotFoundError(f"预设 {preset_name} 不存在")
            
        if message_type not in self.preset_config:
            self.preset_config[message_type] = {}
            
        self.preset_config[message_type][chat_id] = preset_name
        self._save_preset_config()

    # def get_order_prompts(
    #     self,
    #     message_type: str,
    #     chat_id: str
    # ) -> List[Dict[str, Any]]:
    #     """获取指定会话的提示词顺序配置
    #
    #     Args:
    #         message_type: 消息类型
    #         chat_id: 会话ID
    #
    #     Returns:
    #         List[Dict[str, Any]]: 提示词顺序配置列表
    #
    #     Raises:
    #         ValueError: 消息类型无效
    #         FileNotFoundError: 配置文件不存在
    #         json.JSONDecodeError: 配置文件格式错误
    #     """
    #     if message_type not in ["group", "private"]:
    #         raise ValueError(f"无效的消息类型: {message_type}")
    #
    #     preset_name = self.get_preset_name(message_type, chat_id)
    #     config_path = (
    #         Path(__file__).parent /
    #         "preset_prompt_orders" /
    #         preset_name /
    #         f"{message_type}_prompt_order.json"
    #     )
    #
    #     try:
    #         if not config_path.exists():
    #             config_path = (
    #                 Path(__file__).parent /
    #                 "preset_prompt_orders" /
    #                 "default_prompt_orders.json"
    #             )
    #
    #         with open(config_path, 'r', encoding='utf-8') as f:
    #             config = json.load(f)
    #             return config.get("order", [])
    #
    #     except json.JSONDecodeError as e:
    #         raise json.JSONDecodeError(
    #             f"提示词顺序配置文件格式错误: {str(e)}",
    #             e.doc,
    #             e.pos
    #         )

    def get_regex_config(
        self, 
        message_type: str, 
        chat_id: str
    ) -> List[Dict[str, Any]]:
        """获取指定会话的正则表达式配置
        
        Args:
            message_type: 消息类型
            chat_id: 会话ID
            
        Returns:
            List[Dict[str, Any]]: 正则表达式配置列表
            
        Raises:
            ValueError: 消息类型无效
            FileNotFoundError: 配置文件不存在
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        preset_name = self.get_preset_name(message_type, chat_id)
        regex_dir = (
            Path(__file__).parent / 
            "preset_regex" / 
            preset_name
        )
        
        if not regex_dir.exists():
            return []
            
        regex_configs = []
        try:
            for file in regex_dir.glob("*.json"):
                with open(file, 'r', encoding='utf-8') as f:
                    regex_configs.append(json.load(f))
            return regex_configs
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"正则表达式配置文件格式错误: {str(e)}", 
                e.doc, 
                e.pos
            )

    def list_presets(self) -> List[str]:
        """获取所有可用的预设名称列表
        
        Returns:
            List[str]: 预设名称列表
        """
        return [
            f.stem for f in self.preset_folder_path.glob("*.json")
            if f.is_file()
        ]

    def remove_preset(self, message_type: str, chat_id: str) -> bool:
        """移除指定会话的预设配置
        
        Args:
            message_type: 消息类型
            chat_id: 会话ID
            
        Returns:
            bool: 是否成功移除
            
        Raises:
            ValueError: 消息类型无效
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        if (message_type in self.preset_config and 
            chat_id in self.preset_config[message_type]):
            del self.preset_config[message_type][chat_id]
            self._save_preset_config()
            return True
        return False

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

    def set_preset_config(self, message_type: str, session_id: str, preset_name: str) -> None:
        """设置会话的预设配置
        
        Args:
            message_type: 消息类型
            session_id: 会话ID
            preset_name: 预设名称
            
        Raises:
            ValueError: 消息类型无效
            FileNotFoundError: 预设不存在
        """
        if message_type not in ["group", "private"]:
            raise ValueError(f"无效的消息类型: {message_type}")
            
        if preset_name not in self.list_presets():
            raise FileNotFoundError(f"预设不存在: {preset_name}")
            
        if message_type not in self.preset_config:
            self.preset_config[message_type] = {}
            
        self.preset_config[message_type][session_id] = preset_name
        self._save_preset_config()

    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """获取预设配置内容
        
        Args:
            preset_name: 预设名称
            
        Returns:
            Dict[str, Any]: 预设配置内容
            
        Raises:
            FileNotFoundError: 预设文件不存在
            json.JSONDecodeError: 预设文件格式错误
        """
        preset_path = self.preset_folder_path / f"{preset_name}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"预设文件不存在: {preset_name}")
            
        try:
            with open(preset_path, "r", encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"预设文件格式错误: {str(e)}", 
                e.doc, 
                e.pos
            )

    def get_prompt_order(self, message_type: str, session_id: str) -> List[Dict[str, Any]]:
        """获取提示词顺序配置
        
        Args:
            message_type: 消息类型
            session_id: 会话ID
            
        Returns:
            List[Dict[str, Any]]: 提示词顺序配置
            
        Raises:
            ValueError: 消息类型无效
            FileNotFoundError: 配置文件不存在
        """
        preset_name = self.get_preset_name(message_type, session_id)
        order_path = (
            self.script_dir / 
            f"../config/preset/preset_prompt_orders/{preset_name}/{message_type}_prompt_order.json"
        )
        
        if not order_path.exists():
            raise FileNotFoundError(f"提示词顺序配置文件不存在: {preset_name}")
            
        try:
            with open(order_path, "r", encoding='utf-8') as f:
                return json.load(f)["order"]
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"提示词顺序配置文件格式错误: {str(e)}", 
                e.doc, 
                e.pos
            )

    def get_order_prompts(self, message_type: str, session_id: str) -> List[Dict[str, Any]]:
        """获取排序后的提示词列表
        
        Args:
            message_type: 消息类型
            session_id: 会话ID
            
        Returns:
            List[Dict[str, Any]]: 排序后的提示词列表
        """
        preset_name = self.get_preset_name(message_type, session_id)
        preset = self.get_preset(preset_name)
        prompt_order = self.get_prompt_order(message_type, session_id)
        
        order_prompts = []
        for item in prompt_order:
            if item["enabled"]:
                prompt = preset["prompts"].get(item["name"])
                if prompt and item["identifier"] == prompt["identifier"]:
                    if not prompt.get("marker"):
                        order_prompts.append({
                            "role": prompt["role"],
                            "content": prompt["content"]
                        })
                    else:
                        order_prompts.append(prompt["identifier"])
                        
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
     preset = QLPresetManager()
    # print(preset.get_preset_name())
    # # print(preset.get_preset())
    # print(preset.get_preset_list())
    # print(preset.get_prompt_order())
    # print(preset.get_order_prompts())
    # print(preset.get_order_prompts().index("chatHistory"))
    # print(preset.get_order_prompts()[0:12])
    # print(preset.get_order_prompts()[12+1::])
