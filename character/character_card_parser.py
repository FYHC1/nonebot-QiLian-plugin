import os
import ssl
import struct
import zlib
import base64
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pprint import pprint

import httpx
from nonebot.adapters.onebot.v11 import Bot

script_dir = os.path.dirname(__file__)
relative_json_path="..\\data\\character_cards\\json"
relative_card_path="..\\data\\character_cards\\card"

class CharacterCardParser:
    """角色卡解析器类,用于处理角色卡的导入导出和格式转换
    
    提供PNG图片和角色卡JSON数据之间的互相转换功能
    """

    @staticmethod
    def encode_text_chunk(keyword: str, text: str) -> bytes:
        """创建PNG的tEXt块
        
        Args:
            keyword (str): 关键词
            text (str): 文本数据
            
        Returns:
            bytes: 编码后的tEXt块数据
        """
        chunk_data = keyword.encode('latin1') + b'\x00' + text.encode('latin1')
        return b'tEXt' + chunk_data

    @staticmethod
    def calculate_crc(chunk_type: bytes, data: bytes) -> bytes:
        """计算PNG块的CRC校验值
        
        Args:
            chunk_type (bytes): 块类型
            data (bytes): 块数据
            
        Returns:
            bytes: CRC校验值
        """
        return struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)

    @staticmethod
    def embed_character_card(
        image_path: Union[str, Path], 
        output_path: Union[str, Path],
        character_data: Dict[str, Any],
        format_version: str = "V3"
    ) -> None:
        """将角色卡数据嵌入PNG文件
        
        Args:
            image_path: 输入PNG文件路径
            output_path: 输出PNG文件路径
            character_data: 角色卡JSON数据
            format_version: 数据版本(V3或V2)
            
        Raises:
            ValueError: 输入文件格式错误
            IOError: 文件读写错误
        """
        try:
            with open(image_path, "rb") as img_file:
                png_data = img_file.read()

            if png_data[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("输入文件不是有效的PNG文件")

            character_chunk_keyword = "ccv3" if format_version.upper() == "V3" else "chara"
            encoded_data = base64.b64encode(
                json.dumps(character_data).encode("utf-8")
            ).decode("utf-8")
            text_chunk = CharacterCardParser.encode_text_chunk(
                character_chunk_keyword, 
                encoded_data
            )

            chunks = []
            i = 8
            while i < len(png_data):
                length = struct.unpack(">I", png_data[i:i+4])[0]
                chunk_type = png_data[i+4:i+8]
                chunk_data = png_data[i+8:i+8+length]
                crc = png_data[i+8+length:i+12+length]
                chunks.append((chunk_type, chunk_data, crc))
                i += 12 + length

            new_chunks = []
            for chunk_type, chunk_data, crc in chunks:
                if chunk_type == b"IEND":
                    new_chunks.append((
                        b"tEXt",
                        text_chunk,
                        CharacterCardParser.calculate_crc(b"tEXt", text_chunk)
                    ))
                new_chunks.append((chunk_type, chunk_data, crc))

            with open(output_path, "wb") as output_file:
                output_file.write(b"\x89PNG\r\n\x1a\n")
                for chunk_type, chunk_data, crc in new_chunks:
                    output_file.write(struct.pack(">I", len(chunk_data)))
                    output_file.write(chunk_type)
                    output_file.write(chunk_data)
                    output_file.write(crc)

        except IOError as e:
            raise IOError(f"文件操作失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"嵌入角色卡数据时发生错误: {str(e)}") from e

    @staticmethod
    def extract_character_card(image_path: Union[str, Path]) -> Dict[str, Any]:
        """从PNG文件中提取角色卡数据
        
        Args:
            image_path: PNG文件路径
            
        Returns:
            Dict[str, Any]: 解码后的角色卡JSON数据
            
        Raises:
            ValueError: 文件格式错误或未找到角色卡数据
            IOError: 文件读写错误
        """
        try:
            with open(image_path, "rb") as img_file:
                png_data = img_file.read()

            if png_data[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("输入文件不是有效的PNG文件")

            i = 8
            while i < len(png_data):
                length = struct.unpack(">I", png_data[i:i+4])[0]
                chunk_type = png_data[i+4:i+8]
                chunk_data = png_data[i+8:i+8+length]
                i += 12 + length

                if chunk_type == b"tEXt":
                    text = chunk_data.decode("latin1")
                    keyword, data = text.split("\x00", 1)

                    if keyword in ["ccv3", "chara"]:
                        decoded_data = base64.b64decode(data).decode("utf-8")
                        character_data = json.loads(decoded_data)

                        file_name = character_data.get("name")
                        if not file_name:
                            raise ValueError("角色卡数据中未找到'name'属性")

                        json_path = os.path.join(
                            os.path.dirname(__file__),
                            relative_json_path,
                            f"{file_name}.json"
                        )
                        
                        with open(json_path, 'w', encoding='utf-8') as card_json_file:
                            json.dump(
                                character_data,
                                card_json_file,
                                indent=4,
                                ensure_ascii=False
                            )
                        return character_data

            raise ValueError("PNG文件中未找到角色卡数据")

        except IOError as e:
            raise IOError(f"文件操作失败: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"角色卡数据格式错误: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"提取角色卡数据时发生错误: {str(e)}") from e

    @staticmethod
    async def get_file_url(file_receiver: Any, file_id: str) -> str:
        """获取文件下载链接
        
        Args:
            file_receiver: 文件接收器对象
            file_id: 文件ID
            
        Returns:
            str: 文件下载URL
            
        Raises:
            RuntimeError: API调用失败
        """
        try:
            bot: Bot = file_receiver.bot
            response = await bot.call_api("get_file", file_id=file_id)
            url = response.get("url")
            if not url:
                raise RuntimeError("获取文件URL失败")
            return url
        except Exception as e:
            raise RuntimeError(f"获取文件URL时发生错误: {str(e)}") from e

    @staticmethod
    async def download_file(url: str, file_name: str) -> str:
        """下载文件并保存
        
        Args:
            url: 文件下载链接
            file_name: 文件名
            
        Returns:
            str: 保存的文件路径
            
        Raises:
            ValueError: 文件格式错误
            IOError: 文件保存失败
            RuntimeError: 下载失败
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        save_path = os.path.join(
            os.path.dirname(__file__), 
            relative_card_path,
            f"{file_name}.png"
        )

        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers('DEFAULT')
        ssl_context.options |= (
            ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | 
            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | 
            ssl.OP_NO_COMPRESSION
        )

        try:
            async with httpx.AsyncClient(verify=ssl_context) as client:
                resp = await client.get(url, headers=headers)
                
                if resp.status_code != 200:
                    raise RuntimeError(f"下载失败,状态码: {resp.status_code}")
                    
                content = resp.content
                if content[:8] != b"\x89PNG\r\n\x1a\n":
                    raise ValueError("下载的文件不是有效的PNG文件")
                    
                with open(save_path, "wb") as f:
                    f.write(content)
                    
                return save_path
                
        except httpx.RequestError as e:
            raise RuntimeError(f"下载请求失败: {str(e)}") from e
        except IOError as e:
            raise IOError(f"保存文件失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"下载文件时发生错误: {str(e)}") from e

# 示例用法
if __name__ == "__main__":
    # 角色卡数据示例
    character_data = {
        "name": "Sakana",
        "description": "一个有趣且调皮的助理角色。",
        "version": "3.0"
    }

    # 嵌入角色卡数据
    CharacterCardParser.embed_character_card(
        r"C:\Users\hgl\Pictures\Camera Roll\Lingsha.png", r"C:\Users\hgl\Pictures\Saved Pictures\LingSha.png", character_data, format_version="V3"
    )

    # 提取角色卡数据
    extracted_data = CharacterCardParser.extract_character_card(r"C:\Users\hgl\Downloads\c7dcfbd3db56d5f9.png")
    #pprint(extracted_data, indent=4)
    print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
