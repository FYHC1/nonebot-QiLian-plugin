# QiLianChat 项目说明

## 项目简介

QiLianChat 是一个基于 Python 的NoneBot聊天机器人插件，兼容sillytavern的角色卡和预设，旨在为用户提供丰富的对话体验。该项目支持多种角色的管理和对话记录的存储，能够与用户进行自然的对话。

## 目录结构

```
plugins/
└── qilianchat/
    ├── __init__.py
    ├── .idea/
    ├── chat/
    │   ├── chat.py
    │   ├── chat_session.py
    │   ├── chat_session_manager.py
    ├── character/
    │   ├── character.py
    │   ├── character_card.py
    │   ├── character_card_parser.py
    ├── config/
    │   ├── characters.json
    │   ├── completion_configs/
    │   ├── preset/
    └── ...
```

## 功能特性

- **角色管理**：支持创建、更新和删除角色，角色信息包括名称、描述、性格特征等。
- **聊天记录管理**：能够保存和读取用户与角色之间的对话记录，支持群聊和私聊。
- **多种配置**：支持多种聊天完成配置，用户可以根据需要选择不同的聊天模型。
- **正则表达式支持**：提供正则表达式功能，用户可以自定义文本处理规则。

## 安装与使用

首先需要安装NoneBot2框架，请参考[NoneBot2官方文档](https://v2.nonebot.dev/docs/installation)进行安装。
并且在.env.prod文件中配置SUPERUSERS，否则无法使用Superuser权限。
列如：
```
SUPERUSERS=["1234567890"]
```

1. **安装依赖**：
   确保已安装 Python 3.12 及以上版本，并安装所需的依赖库。

   ```bash
   pip install -r requirements.txt
   ```

2. **配置聊天服务**：
   在 `config/completion_configs/` 中添加聊天完成配置。
   默认使用 `chat_completion_Google AI Studio.json` 配置，使用Gemini 2.0 系列模型。
   如果需要使用其他配置，请在 `config/completion_configs/` 中添加对应的配置文件。

   也可以使用‘/怜祈 帮助’查看详细使用说明。
   首先需指定聊天服务来源，ChatGPT,Google AI Studio,DeepSeek，可只需配置API_KEY。如需使用其他聊天服务或者代理服务，请配置为Others,并配置对应的API_URL和API_KEY。
   然后需指定聊天模型，Gemini 2.0 系列模型
   最后需指定聊天完成配置，默认使用 `chat_completion_Google AI Studio.json` 配置，使用Gemini 2.0 系列模型。


3. **运行项目**：
   使用以下命令启动聊天机器人：

   ```
   nb run --reload
   ```

## 文件说明

- **chat/chat.py**：聊天记录管理类，负责处理和存储聊天记录。
- **character/character.py**：角色类，管理角色的基本信息和属性。
- **character/character_card.py**：角色卡类，管理角色卡数据。
- **config/**：存放配置文件，包括角色配置、聊天完成配置等。

## 贡献
本项目灵感来源与sillytavern项目，参考并使用了类脑社区的优秀角色卡和预设，感谢类脑社区的贡献！

欢迎任何形式的贡献！请提交问题或拉取请求。

## 许可证

本项目采用 MIT 许可证，详细信息请查看 LICENSE 文件。

---

如需更多信息，请查阅项目中的文档或联系项目维护者。
