import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI, RateLimitError, APIError


##
#chat_completion_type:{
#OpenAI
#Claude
#Google AI Studio
#}

class OpenAi:
    """OpenAI API客户端类,用于管理API配置和调用
    
    Attributes:
        chat_completion_source (str): 聊天补全来源
        api_url (str): API基础URL
        api_keys (List[str]): API密钥列表
        module (str): 模型名称
        max_tokens (int): 最大生成token数
        temperature (float): 采样温度
        current_key_index (int): 当前API密钥索引
        max_retries (int): 最大重试次数
        retry_delay (int): 重试延迟秒数
    """

    def __init__(self) -> None:
        """初始化OpenAI客户端"""
        self.config_path = Path(__file__).parent / "../config/completion_configs"
        
        # 默认配置
        self.chat_completion_source = "Google AI Studio"
        self.api_url = ""
        self.api_keys: List[str] = []
        self.module = ""
        self.max_tokens = 1000
        self.temperature = 0.8
        self.current_key_index = 0
        self.max_retries = 10
        self.retry_delay = 3

        # 加载配置
        self.from_json()

    def set_chat_completion_source(self, source: str) -> None:
        """设置聊天补全来源
        
        Args:
            source: 补全来源名称
        """
        self.chat_completion_source = source
        self.to_json("chat_completion_source", source)
        self.from_json()

    def set_api_url(self, url: str) -> None:
        """设置API URL
        
        Args:
            url: API基础URL
        """
        self.api_url = url
        self.to_json("api_url", url)

    def set_api_key(self, key: str) -> None:
        """设置单个API密钥
        
        Args:
            key: API密钥
        """
        self.api_keys = [key]
        self.to_json("api_keys", self.api_keys)

    def set_api_keys(self, keys: List[str]) -> None:
        """设置多个API密钥
        
        Args:
            keys: API密钥列表
        """
        self.api_keys = keys
        self.to_json("api_keys", keys)

    def set_module(self, module: str) -> None:
        """设置模型名称
        
        Args:
            module: 模型名称
        """
        self.module = module
        self.to_json("module", module)

    def set_max_tokens(self, max_tokens: int) -> None:
        """设置最大生成token数
        
        Args:
            max_tokens: 最大token数
        """
        self.max_tokens = max_tokens
        self.to_json("max_tokens", max_tokens)

    def set_temperature(self, temperature: float) -> None:
        """设置采样温度
        
        Args:
            temperature: 温度值
        """
        self.temperature = temperature
        self.to_json("temperature", temperature)

    def to_json(self, config_name: str, config: Any) -> None:
        """保存配置到JSON文件
        
        Args:
            config_name: 配置项名称
            config: 配置值
            
        Raises:
            IOError: 保存失败
        """
        try:
            config_file = (
                self.config_path / 
                f"chat_completion_{self.chat_completion_source}.json"
            )
            
            try:
                with open(config_file, "r", encoding='utf-8') as f:
                    completion_config = json.load(f)
            except FileNotFoundError:
                completion_config = {}
                
            completion_config[config_name] = config
            
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding='utf-8') as f:
                json.dump(
                    completion_config,
                    f,
                    ensure_ascii=False,
                    indent=4
                )
                
        except IOError as e:
            raise IOError(f"保存配置失败: {str(e)}") from e

    def from_json(self) -> Dict[str, Any]:
        """从JSON文件加载配置
        
        Returns:
            Dict[str, Any]: 加载的配置数据
            
        Raises:
            json.JSONDecodeError: JSON格式错误
        """
        try:
            config_file = (
                self.config_path / 
                f"chat_completion_{self.chat_completion_source}.json"
            )
            
            if not config_file.exists():
                print(f"警告: 未找到配置文件 '{self.chat_completion_source}',使用默认配置")
                return {}
                
            with open(config_file, "r", encoding='utf-8') as f:
                config = json.load(f)
                
            # 更新配置
            self.chat_completion_source = config.get(
                "chat_completion_source",
                self.chat_completion_source
            )
            self.api_url = config.get("api_url", "")
            self.api_keys = config.get("api_keys", [])
            if not self.api_keys and config.get("api_key"):
                self.api_keys = [config["api_key"]]
            self.module = config.get("module", "")
            self.max_tokens = config.get("max_tokens", 1000)
            self.temperature = config.get("temperature", 0.8)
            self.max_retries = config.get("max_retries", 10)
            self.retry_delay = config.get("retry_delay", 5)
            
            return config
            
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件 '{self.chat_completion_source}' 格式错误,请检查JSON格式")
            return {}

    async def start_chat(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """启动聊天会话
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 回复消息
        """
        match self.chat_completion_source.lower():
            case "openai":
                return await self.chat_with_openai(messages)
            case "claude":
                return await self.chat_with_claude(messages)
            case "google ai studio":
                return await self.chat_with_gemini(messages)
            case "deepseek":
                return await self.chat_with_openai(messages)
            case _:
                print(f"警告: 未知的聊天补全来源 '{self.chat_completion_source}',默认使用OpenAI")
                return await self.chat_with_openai(messages)

    async def chat_with_openai(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """使用OpenAI API进行聊天
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 回复消息
            
        Raises:
            RateLimitError: 达到速率限制
            APIError: API调用错误
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                client = OpenAI(
                    api_key=self.api_keys[0] if self.api_keys else None,
                    base_url=self.api_url or "https://api.openai.com/v1"
                )

                response = client.chat.completions.create(
                    model=self.module,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    extra_headers={"Content-Type": "application/json"}
                )

                msg = response.choices[0].message.content
                #print(msg)
                print_usage_info(response.usage)
                return msg

            except RateLimitError as e:
                retries += 1
                if retries > self.max_retries:
                    print(f"OpenAI速率限制错误: 达到最大重试次数。错误: {e}")
                    return f"错误: OpenAI速率限制 - 超过最大重试次数。最后错误: {e}"
                    
                print(f"OpenAI速率限制错误: {self.retry_delay}秒后重试... (重试 {retries}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                continue

            except APIError as e:
                print(f"OpenAI API错误: {e}")
                return f"错误: OpenAI API - {e}"
            except Exception as e:
                print(f"OpenAI聊天时发生意外错误: {e}")
                return f"错误: 意外 - {e}"

    async def chat_with_gemini(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """使用Google AI Studio (Gemini) API进行聊天
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 回复消息
            
        Raises:
            RateLimitError: 达到速率限制
            APIError: API调用错误
        """
        if not self.api_keys:
            return "错误: 未提供Google AI Studio的API密钥"

        for index in range(len(self.api_keys)):
            api_key = self.api_keys[
                (self.current_key_index + index) % len(self.api_keys)
            ]
            retries = 0
            
            while retries <= self.max_retries:
                try:
                    client = OpenAI(
                        api_key=api_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                    )

                    response = client.chat.completions.create(
                        model=self.module,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        extra_headers={"Content-Type": "application/json"}
                    )

                    msg = response.choices[0].message.content
                    print_usage_info(response.usage)
                    self.current_key_index = (
                        self.current_key_index + index
                    ) % len(self.api_keys)
                    return msg

                except RateLimitError as e:
                    retries += 1
                    if retries > self.max_retries:
                        print(
                            f"Gemini速率限制错误(密钥索引 {(self.current_key_index + index) % len(self.api_keys)}): "
                            f"达到最大重试次数。错误: {e}"
                        )
                        break
                        
                    print(
                        f"Gemini速率限制错误(密钥索引 {(self.current_key_index + index) % len(self.api_keys)}): "
                        f"{self.retry_delay}秒后重试... (重试 {retries}/{self.max_retries})"
                    )
                    await asyncio.sleep(self.retry_delay)
                    continue

                except APIError as e:
                    print(
                        f"Gemini API错误(密钥索引 {(self.current_key_index + index) % len(self.api_keys)}): {e}"
                    )
                    if index == len(self.api_keys) - 1:
                        return f"错误: Gemini API - 所有API密钥都失败。最后错误: {e}"
                    print("尝试下一个API密钥...")
                    break
                    
                except Exception as e:
                    print(f"Gemini聊天时发生意外错误: {e}")
                    return f"错误: 意外 - {e}"
            else:
                continue
                
            if index == len(self.api_keys) - 1:
                return "错误: Gemini API - 所有API密钥在多次重试后都失败"

    async def chat_with_claude(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """使用Claude API进行聊天(占位)
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 回复消息
        """
        print("警告: Claude集成是占位符,可能需要进一步实现才能完全功能")
        return "此版本未完全实现Claude集成"

def print_usage_info(usage: Any) -> None:
    """打印token使用信息
    
    Args:
        usage: 使用量信息对象
    """
    print("使用量信息:")
    print(f"  补全tokens: {usage.completion_tokens}")
    print(f"  提示tokens: {usage.prompt_tokens}")
    print(f"  总tokens: {usage.total_tokens}")


if __name__=="__main__":
    # Example Usage and Testing

    async def main():
        open_ai = OpenAi()
        open_ai.set_chat_completion_source("OpenAI") # Or "OpenAI", "Claude", "Others", "Google AI Studio"
        # For Google AI Studio, set multiple API keys if you want to test polling:
        # open_ai.set_api_keys(["YOUR_GEMINI_API_KEY_1", "YOUR_GEMINI_API_KEY_2", "YOUR_GEMINI_API_KEY_3"])
        open_ai.set_api_key("YOUR_OPENAI_API_KEY") # Or set a single key, or Gemini key if testing Gemini
        open_ai.set_module("gpt-3.5-turbo") # Or "gemini-1.5-flash", "gpt-4" etc.
        open_ai.set_max_tokens(1000)
        open_ai.set_temperature(0.5)

        print("Current Config:", open_ai.from_json())

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ]

        response_message = await open_ai.start_chat(messages)
        print("\nResponse Message:\n", response_message)


    asyncio.run(main())