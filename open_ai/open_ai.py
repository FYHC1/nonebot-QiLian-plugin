import asyncio
import json
import os

import requests
from openai import OpenAI


##
#chat_completion_type:{
#OpenAI
#Claude
#Google AI Studio
#}

class Open_Ai:
    # 文件地址
    script_dir = os.path.dirname(__file__)
    config_folder_path = os.path.join(script_dir, "../config/completion_configs")

    def __init__(self):
        self.chat_completion_type="Google AI Studio"
        self.api_url= "https:api.openai.com/v1"
        self.api_key= ""
        self.module="gemini-1.5-flash"
        self.max_tokens=1000
        self.temperature=0.5

        self.from_json()


    def set_chat_completion_type(self, chat_completion_type):
        self.chat_completion_type=chat_completion_type
        self.to_json("chat_completion_type", chat_completion_type)
        self.from_json()

    def set_api_url(self, url):
        self.api_url=url
        self.to_json("proxy_url", url)

    def set_api_key(self, key):
        self.api_key=key
        self.to_json("proxy_password", key)

    def set_module(self, module):
        self.module=module
        self.to_json("module", module)

    def set_max_tokens(self, max_tokens):
        self.max_tokens=max_tokens
        self.to_json("max_tokens", max_tokens)

    def set_temperature(self, temperature):
        self.temperature=temperature
        self.to_json("temperature", temperature)

    def to_json(self,config_name,config):

        with open(os.path.join(self.config_folder_path,f"chat_completion_{self.chat_completion_type}.json"),"r+",encoding='utf-8') as rf:
            completion_config=json.load(rf)
            completion_config[config_name]=config
        with open(os.path.join(self.config_folder_path, f"chat_completion_{self.chat_completion_type}.json"),
                            "w+",encoding='utf-8') as wf:
            json.dump(completion_config,wf,ensure_ascii=False,indent=4)


    def from_json(self):
        with open(os.path.join(self.config_folder_path,f"chat_completion_{self.chat_completion_type}.json"),"r",encoding='utf-8') as f:
            completion_config=json.load(f)
            self.chat_completion_type=completion_config["chat_completion_type"]
            self.api_key=completion_config["proxy_url"]
            self.api_key=completion_config["proxy_password"]
            self.module=completion_config["module"]
            self.max_tokens=completion_config["max_tokens"]
            self.temperature=completion_config["temperature"]

        return completion_config






    async def start_chat(self,messages):
        match self.chat_completion_type:
            case "OpenAi":
                return await self.chat_with_gpt(messages)
            case "Claude":
                return await self.chat_with_claude(messages)
            case "Google AI Studio":
                return await self.chat_with_gemini(messages)





    async def chat_with_gpt(self,messages):
        client = OpenAI(
            base_url=self.api_url,
            api_key=self.api_key,
        )

        # 请求模型的回复
        HEADERS = {"Content-Type": "application/json"}
        completion = client.chat.completions.create(
            model=self.module,
            messages=messages,
            extra_headers=HEADERS,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        # 打印返回的模型回复
        # print("Model's Reply:", completion.choices[0].message.content)
        msg = completion.choices[0].message.content
        # print(msg+'\n')
        print("completion_tokens: " + f'{completion.usage.completion_tokens}\n')
        print("prompt_tokens: " + f'{completion.usage.prompt_tokens}\n')
        print("total_tokens: " + f"{completion.usage.total_tokens}")

        return msg




    async def chat_with_claude(self, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": f"\n\nHuman: {messages}\n\nAssistant:",
            "model": self.module,
            "max_tokens_to_sample": self.max_tokens,
            "stop_sequences": ["\n\nHuman:"]
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data['completion'].strip()
        else:
            return f"请求失败，状态码：{response.status_code}, 错误信息：{response.text}"




    async def chat_with_gemini(self, messages):
        # genai.configure(api_key=self.api_key)
        # model = genai.GenerativeModel("gemini-1.5-flash")
        # response = model.generate_content(messages)
        #

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        HEADERS = {"Content-Type": "application/json"}

        response = client.chat.completions.create(
            model=self.module,
            n=1,
            messages=messages,
            extra_headers = HEADERS,
            max_tokens = self.max_tokens,
            temperature = self.temperature
        )

        try:
            msg = response.choices[0].message.content
        except AttributeError as e:
            print(e.args)
            msg = "reply已被过滤器拦截"
            return msg
        # print(msg+'\n')
        print("completion_tokens: " + f'{response.usage.completion_tokens}\n')
        print("prompt_tokens: " + f'{response.usage.prompt_tokens}\n')
        print("total_tokens: " + f"{response.usage.total_tokens}")
        #print(msg)
        return msg






if __name__=="__main__":
    # open_ai = Open_Ai()
    # open_ai.set_chat_completion_type("Google AI Studio")
    # open_ai.set_api_url("https://generativelanguage.googleapis.com/v1beta/openai/")
    # open_ai.set_api_key("GEMINI_API_KEY")
    # open_ai.set_module("gemini-1.5-flash")
    # open_ai.set_max_tokens(1000)
    # open_ai.set_temperature(0.5)
    #
    # print(open_ai.from_json())

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "你是谁啊"
        }
    ]


    open_ai = Open_Ai()
    open_ai.set_chat_completion_type("Google AI Studio")
    asyncio.run(open_ai.start_chat(messages))