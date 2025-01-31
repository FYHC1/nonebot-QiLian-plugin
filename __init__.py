import json
import os
from urllib.parse import urlparse, parse_qs

import requests

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent, PrivateMessageEvent, Event, \
    MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_startswith, on_message, on_command, on_regex
from nonebot.rule import startswith, to_me


from .character.character import Character
from .character.character_card_parser import CharacterCardParser
from .character.group_character import GroupCharacter
from .character.private_character import PrivateCharacter
from .chat.chat import Chat
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-sillytavern-plugin",
    description="",
    usage="",
    config=Config,
)

from .messages.messages import Messages
from .open_ai.open_ai import Open_Ai

from .user.group_user import GroupUser
from .user.private_user import PrivateUser




###
character=Character()
private_user=PrivateUser()
group_user=GroupUser()
chat = Chat()
messages = Messages()
open_ai = Open_Ai()





tigger=on_startswith(("怜祈"),ignorecase=True)

@tigger.handle()
async def sillytavern():
   await tigger.finish("正在运行中")


#查看角色列表
check_characters=on_command("查看角色列表",permission=SUPERUSER)

@check_characters.handle()
async def check_characters_list():
   await check_characters.finish(str(character.get_character_list()))



#指定角色
appoint_character=on_command("指定聊天角色")

@appoint_character.handle()
async def group_select_character(event:MessageEvent, args:Message=CommandArg()):

    message_type=event.message_type
    character_name=args.extract_plain_text()
    if message_type=="group":
        user=group_user
        user.chat_user_id = str(event.group_id)
        user.message_type = event.message_type
        user.character_name = args.extract_plain_text()
    else:
        user=private_user
        user.chat_user_id=str(event.user_id)
        user.message_type = event.message_type
        user.character_name = args.extract_plain_text()

    chat.from_user(user)

    if character_name not in character.character_list :
        appoint_character.finish("不存在此角色，请重新指定角色")
    await user.appoint_character(character_name)
    await appoint_character.send(f"已指定聊天角色{character_name}")
    await chat.new_chat()
    # await init()
    character.set_init()



#进行角色扮演对话
def groupMessage(event:MessageEvent):
    return event.message_type=="group"
def privateMessage(event:MessageEvent):
    return event.message_type =="private"



role_play=on_message(rule=groupMessage & to_me(),priority=10,block=True)


@role_play.handle()
async def role_play_chat(event:GroupMessageEvent, bot:Bot):

    group_user.set_chat_user(str(event.group_id))
    group_user.set_user_id(str(event.user_id))
    await group_user.set_nickname(bot)
    nickname=group_user.nickname
    group_user.message=event.get_plaintext()
    group_user.set_character_name()

    print(group_user.user_id,group_user.chat_user_id,nickname,group_user.message,group_user.character_name)

    chat.from_user(group_user)
    messages.from_user(group_user)


    chat_history=await chat.get_context()
    chat_messages=messages.construct_messages(character.preset_list,character.prompts_list,chat_history)
    #print(json.dumps(messages, indent=4, ensure_ascii=False))
    assistant_reply = await open_ai.start_chat(chat_messages)
    await chat.save_chat_message(assistant_reply)
    await role_play.finish(MessageSegment.at(group_user.user_id)+Message(assistant_reply))



#role_play1=on_regex(r"^怜祈\s*(.*)")
role_play1=on_message(rule=privateMessage,priority=10,block=True)

@role_play1.handle()
async def role_play_chat1(event:PrivateMessageEvent,bot:Bot):

    private_user.chat_user_id = str(event.user_id)
    private_user.user_id = str(event.user_id)
    await private_user.set_nickname(bot)
    nickname = private_user.nickname
    private_user.message = event.get_plaintext()
    private_user.set_character_name()

    print(private_user.chat_user_id, private_user.user_id, private_user.message, nickname,private_user.character_name)

    chat.from_user(private_user)
    messages.from_user(private_user)

    chat_history = await chat.get_context()
    chat_messages = messages.construct_messages(character.preset_list,character.prompts_list, chat_history)
    # print(json.dumps(messages, indent=4, ensure_ascii=False))
    assistant_reply = await open_ai.start_chat(chat_messages)
    await chat.save_chat_message(assistant_reply)
    await role_play.finish(MessageSegment.at(private_user.user_id)+Message(assistant_reply))





#清空聊天记录
clear_chat=on_command("clear",permission=SUPERUSER)
@clear_chat.handle()
async def clear_chat_message(event:MessageEvent):
    message_type=event.message_type
    if message_type=="group":
        chat_user_id=str(event.group_id)
    else:
        chat_user_id=str(event.user_id)

    character_name=character.get_charactername(message_type,chat_user_id)
    print(message_type, chat_user_id,character_name)
    await chat.clear_chat_message(message_type,chat_user_id,character_name)
    await clear_chat.finish("记忆已清除...")



#添加角色卡
append_character_card=on_command("上传角色卡",permission=SUPERUSER)

@append_character_card.handle()
async def handle_file(event: MessageEvent,bot:Bot):
    # 检查消息是否包含文件
    character_card_paser=CharacterCardParser()
    image_url=''
    file_name=''
    print(event.message)
    for segment in event.message:
        if segment.type == "image":

            # 获取图片的 URL
            image_url = segment.data["url"]

            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)  # 解析查询参数
            file_name =query_params.get("fileid", [None])[0]
            print(image_url,file_name)


            if image_url:
                # 下载文件并保存
                img_path= await character_card_paser.download_file(image_url, file_name)
                character_card_paser.extract_character_card(img_path)
                #await init()
                await append_character_card.send(character.get_character_list())
                character.set_init()
                await append_character_card.finish(f"文件 {file_name} 已保存！")
            else:
                await append_character_card.finish("未能获取文件下载链接。")



@append_character_card.got("message",prompt="请上传文件")
async def update_file(event:MessageEvent):
    global file_type, file_id, file_name, image_url
    script_dir = os.path.dirname(__file__)
    message = event.get_message()

    for part in message:
        if part.type == "image":
            # 处理图片文件
            image_url = part.data["url"]

            file_id = part.data["file_id"]
            file_name = file_id.split('.')[-2].lower()
            file_type = file_id.split('.')[-1].lower()

        elif part.type == "file":

            file_id=part.data["file_id"]
            file_name = file_id.split('.')[-2].lower()
            file_type = file_id.split('.')[-1].lower()  # 获取文件扩展名

        if file_type == "png":
            character_card_paser=CharacterCardParser()
            img_path= await character_card_paser.download_file(image_url, file_name)
            character_card_paser.extract_character_card(img_path)

            await append_character_card.send(character.get_character_list())
            character.set_init()
            await append_character_card.finish("收到PNG数据")

        elif file_type == "json":
            source_path = await get_file(file_id)
            destination_path=os.path.join(script_dir,"./data/character_cards/json",f"{file_name}.{file_type}")


            # 处理 JSON 文件
            try:
                with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
                    dst.write(src.read())

                #await init()
                await append_character_card.send(character.get_character_list())
                character.prompts_list = character.get_prompts_list()
                await append_character_card.finish(f"收到 JSON 数据")
            except json.JSONDecodeError:
                await append_character_card.finish("收到的文件不是有效的 JSON 文件。")
        else:
            # 处理其他文件类型
            await append_character_card.finish(f"收到一个文件：{file_name}.{file_type}")
    # else:
    #     await append_character_card.finish("收到的消息中没有包含有效的文件。")


# 获取文件
async def get_file(file_id: str):
    url = " http://127.0.0.1:3000/get_file"

    payload = json.dumps({
        "file_id": file_id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    data = response.json()['data']
    source_path = data['url']

    '''
        {"status":"ok","retcode":0,"data":{"file":"C:\\Users\\hgl\\Documents\\Tencent Files\\NapCat\\temp\\怜祈.json","url":"C:\\Users\\hgl\\Documents\\Tencent Files\\NapCat\\temp\\怜祈.json","file_size":"1197","file_name":"怜祈.json"},"message":"","wording":"","echo":null}

    '''

    return source_path




set_proxy_type = on_command("设置文本补全类型",permission=SUPERUSER)

chat_completion_type = ["OpenAI", "Claude", "Google AI Studio"]

@set_proxy_type.handle()
async def handle_proxy_type(event: MessageEvent, args: Message = CommandArg()):
    proxy_type = args.extract_plain_text().strip()
    if proxy_type in chat_completion_type:
        open_ai.set_chat_completion_type(proxy_type)
        await set_proxy_type.finish(f"已设置文本补全类型为：{proxy_type}")
    else:
        await set_proxy_type.send(f"无效的文本补全类型，请选择以下之一：{', '.join(chat_completion_type)}")

@set_proxy_type.got("chat_type", prompt=f"请输入文本补全类型：{', '.join(chat_completion_type)}")
async def handle_proxy_type_followup(event: MessageEvent):
    chat_type = event.get_plaintext().strip()
    if chat_type in chat_completion_type:
        open_ai.set_chat_completion_type(chat_type)
        await set_proxy_type.finish(f"已设置文本补全类型为：{chat_type}")
    else:
        await set_proxy_type.finish(f"无效的文本补全类型，请选择以下之一：{', '.join(chat_completion_type)}")


set_api_url = on_command("设置代理url",permission=SUPERUSER)

@set_api_url.handle()
async def handle_api_url(event: MessageEvent, api_url: Message = CommandArg()):
    api_url = api_url.extract_plain_text().strip()
    if api_url:
        open_ai.set_api_url(api_url)
        await set_api_url.finish(f"已设置代理url为：{api_url}")
    else:
        await set_api_url.send("请输入有效的代理url！")

@set_api_url.got("api_url", prompt="请输入代理url")
async def handle_api_url_followup(event: MessageEvent):
    api_url = event.get_plaintext().strip()
    if api_url:
        open_ai.set_api_url(api_url)
        await set_api_url.finish(f"已设置代理url为：{api_url}")
    else:
        await set_api_url.finish("无效的代理url，请重新输入！")




set_api_key = on_command("设置代理密钥",permission=SUPERUSER)

@set_api_key.handle()
async def handle_api_key(event: MessageEvent, args: Message = CommandArg()):
    key = args.extract_plain_text().strip()
    if key:
        open_ai.set_api_key(key)
        await set_api_key.finish(f"已设置代理密钥为：{key}")
    else:
        await set_api_key.send("请输入有效的代理密钥！")

@set_api_key.got("key", prompt="请输入代理密钥")
async def handle_api_key_followup(event: MessageEvent):
    key = event.get_plaintext().strip()
    if key:
        open_ai.set_api_key(key)
        await set_api_key.finish(f"已设置代理密钥为：{key}")
    else:
        await set_api_key.finish("无效的代理密钥，请重新输入！")


set_chat_module = on_command("设置模型",permission=SUPERUSER)

module_name = ["gpt-4o","gpt-4o-mini","gpt-4","gpt-4 turbo","gpt-3.5","gpt-3.5 turbo"]

@set_chat_module.handle()
async def handle_module(event: MessageEvent, args: Message = CommandArg()):
    module = args.extract_plain_text().strip()
    if module in module_name:
        open_ai.set_module(module)
        await set_chat_module.finish(f"已设置模型为：{module}")
    else:
        await set_chat_module.send(f"无效的模型名称，请选择：{module_name}")

@set_chat_module.got("module", prompt=f"请输入模型名称\n{module_name}")
async def handle_module_followup(event: MessageEvent):
    module = event.get_plaintext().strip()
    if module in module_name:
        open_ai.set_module(module)
        await set_chat_module.finish(f"已设置模型为：{module}")
    else:
        await set_chat_module.finish(f"无效的模型名称，请选择：{module_name}")


set_max_tokens = on_command("设置max_tokens",permission=SUPERUSER)

@set_max_tokens.handle()
async def handle_max_token(event: MessageEvent, args: Message = CommandArg()):
    max_tokens_text = args.extract_plain_text().strip()
    if max_tokens_text.isdigit() and int(max_tokens_text) > 0:
        max_tokens = int(max_tokens_text)
        open_ai.set_max_tokens(max_tokens)
        await set_max_tokens.finish(f"已设置最大令牌数为：{max_tokens}")
    else:
        await set_max_tokens.send("请输入有效的正整数！")

@set_max_tokens.got("max_tokens", prompt="请输入max_tokens")
async def handle_max_token_followup(event: MessageEvent):
    max_tokens_text = event.get_plaintext().strip()
    try:
        max_tokens = int(max_tokens_text)
        if max_tokens > 0:
            open_ai.set_max_tokens(max_tokens)
            await set_max_tokens.finish(f"已设置最大令牌数为：{max_tokens}")
        else:
            await set_max_tokens.finish("令牌数必须是正整数！")
    except ValueError:
        await set_max_tokens.finish("无效的令牌数，请输入一个正整数！")


set_temperature = on_command("设置temp",permission=SUPERUSER)

@set_temperature.handle()
async def handle_temperature(event: MessageEvent, args: Message = CommandArg()):
    temperature_text = args.extract_plain_text().strip()
    try:
        temperature = float(temperature_text)
        if temperature>0 and temperature<2:
            open_ai.set_temperature(temperature)
        else:
            await set_temperature.send("请输入0到2的浮点数")
        await set_temperature.finish(f"已设置温度为：{temperature}")
    except ValueError:
        await set_temperature.send("请输入有效的温度值！")

@set_temperature.got("temp", prompt="请输入temperature")
async def handle_temperature_followup(event: MessageEvent):
    temperature_text = event.get_plaintext().strip()
    try:
        temperature = float(temperature_text)
        if temperature>0 and temperature<2:
            open_ai.set_temperature(temperature)
        else:
            await set_temperature.finish("请输入0到2的浮点数")

        await set_temperature.finish(f"已设置温度为：{temperature}")
    except ValueError:
        await set_temperature.finish("无效的温度值，请重新输入！")
