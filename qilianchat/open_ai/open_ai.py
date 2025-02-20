
import asyncio
import json
import os
import time  # Import time module for delay
from xmlrpc.client import Error

import openai
from openai import OpenAI
from openai import RateLimitError  # Import RateLimitError
from watchfiles import awatch


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

        self.chat_completion_source= "Google AI Studio" # Default to Google AI Studio
        self.api_url= ""
        self.api_keys= [] # Use a list to store API keys for potential polling, even for single key scenarios
        self.module=""
        self.max_tokens=1000
        self.temperature=0.8
        self.current_key_index = 0 # For API key rotation
        self.max_retries = 10  # Maximum number of retries for rate limit errors
        self.retry_delay = 3  # Delay in seconds between retries

        self.from_json() # Load configurations from JSON during initialization


    def set_chat_completion_source(self, chat_completion_source):
        self.chat_completion_source=chat_completion_source
        self.to_json("chat_completion_source", chat_completion_source)
        self.from_json() # Reload config after changing source to apply relevant settings

    def set_api_url(self, url):
        self.api_url=url
        self.to_json("api_url", url)

    def set_api_key(self, key):
        # Ensure api_keys is always a list, even if setting a single key.
        self.api_keys=[key]
        self.to_json("api_keys", self.api_keys) # Store as api_keys in json, even if single key

    def set_api_keys(self, keys): # Method to set a list of API keys directly
        self.api_keys=keys
        self.to_json("api_keys", keys)


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
        """Writes configuration to the appropriate JSON file based on chat_completion_source."""
        try:
            with open(os.path.join(self.config_folder_path,f"chat_completion_{self.chat_completion_source}.json"), "r+", encoding='utf-8') as rf:
                completion_config=json.load(rf)
                completion_config[config_name]=config
        except FileNotFoundError:
            completion_config = {config_name: config} # Create config if file not found

        with open(os.path.join(self.config_folder_path, f"chat_completion_{self.chat_completion_source}.json"),
                            "w+",encoding='utf-8') as wf:
            json.dump(completion_config,wf,ensure_ascii=False,indent=4)


    def from_json(self):
        """Loads configuration from the JSON file corresponding to chat_completion_source."""
        try:
            with open(os.path.join(self.config_folder_path,f"chat_completion_{self.chat_completion_source}.json"), "r", encoding='utf-8') as f:
                completion_config=json.load(f)
                self.chat_completion_source=completion_config.get("chat_completion_source", self.chat_completion_source) # Use get to avoid KeyError and default to current value
                self.api_url=completion_config.get("api_url", "") # Use get with default
                self.api_keys=completion_config.get("api_keys", []) # Load api_keys list, default to empty list
                if not self.api_keys and completion_config.get("api_key"): # For backward compatibility, if api_key exists but api_keys is empty, use api_key
                    self.api_keys = [completion_config["api_key"]] # Convert single api_key to api_keys list
                self.module=completion_config.get("module", "") # Use get with default
                self.max_tokens=completion_config.get("max_tokens", 1000) # Use get with default
                self.temperature=completion_config.get("temperature", 0.8) # Use get with default
                self.max_retries = completion_config.get("max_retries", 10) # Load retry config, default to 3
                self.retry_delay = completion_config.get("retry_delay", 5) # Load retry delay, default to 5
        except FileNotFoundError:
            print(f"Warning: Configuration file for '{self.chat_completion_source}' not found. Using default settings.")
            return {} # Return empty dict to indicate no config loaded, but defaults are used
        except json.JSONDecodeError:
            print(f"Error: Configuration file for '{self.chat_completion_source}' is corrupted. Please check the JSON format.")
            return {}
        return completion_config # Return loaded config for potential use, though not strictly necessary currently



    async def start_chat(self,messages):
        """Initiates chat based on the configured chat completion source."""
        match self.chat_completion_source.lower(): # Case-insensitive matching
            case "openai":
                return await self.chat_with_openai(messages)
            case "claude":
                return await self.chat_with_claude(messages)
            case "google ai studio":
                return await self.chat_with_gemini(messages)
            case "deepseek":
                return await self.chat_with_openai(messages)
            case "others": # Fallback to openai if "Others" is selected or for unknown types
                return await self.chat_with_openai(messages)
            case _: # Default case for robustness
                print(f"Warning: Unknown chat completion source '{self.chat_completion_source}'. Defaulting to OpenAI.")
                return await self.chat_with_openai(messages)


    async def chat_with_openai(self,messages):
        """Chats with OpenAI compatible models, including custom OpenAI endpoints, with rate limit retry."""
        retries = 0
        while retries <= self.max_retries: # Retry loop
            try:
                client = OpenAI(
                    api_key=self.api_keys[0] if self.api_keys else None, # Use the first key if available, handle no key case gracefully
                    base_url=self.api_url if self.api_url else "https://api.openai.com/v1" # Default base URL if not set
                )

                HEADERS = {"Content-Type": "application/json"}

                response = client.chat.completions.create( # Use async client
                    model=self.module,
                    n=1,
                    messages=messages,
                    extra_headers=HEADERS,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )

                msg = response.choices[0].message.content
                print(msg)
                print_usage_info(response.usage) # Print token usage info
                return msg # Success, return message and break retry loop

            except RateLimitError as e: # Catch RateLimitError specifically
                retries += 1
                if retries > self.max_retries:
                    print(f"OpenAI RateLimitError: Max retries reached. Error: {e}")
                    return f"Error: OpenAI Rate Limit - Max retries exceeded. Last error: {e}" # Return error after max retries
                else:
                    print(f"OpenAI RateLimitError: Retrying in {self.retry_delay} seconds... (Retry {retries}/{self.max_retries})")
                    await asyncio.sleep(self.retry_delay) # Wait before retrying
                    continue # Continue to the next retry attempt

            except openai.APIError as e: # Catch other OpenAI API errors
                print(f"OpenAI API error: {e}")
                return f"Error: OpenAI API - {e}" # Return error message to the user
            except Exception as e: # Catch any other potential exceptions
                print(f"An unexpected error occurred during OpenAI chat: {e}")
                return f"Error: Unexpected - {e}"


    async def chat_with_gpt(self,messages):
        """Chats specifically with OpenAI's GPT models using the standard OpenAI endpoint with rate limit retry."""
        retries = 0
        while retries <= self.max_retries: # Retry loop
            try:
                client = OpenAI(
                    base_url="https://api.openai.com/v1", # Standard OpenAI base URL
                    api_key=self.api_keys[0] if self.api_keys else None,
                )


                HEADERS = {"Content-Type": "application/json"}
                completion = client.chat.completions.create( # Use async client
                    model=self.module,
                    messages=messages,
                    extra_headers=HEADERS,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )


                msg = completion.choices[0].message.content
                print_usage_info(completion.usage) # Print token usage info
                return msg # Success, return message and break retry loop

            except RateLimitError as e: # Catch RateLimitError specifically
                retries += 1
                if retries > self.max_retries:
                    print(f"OpenAI RateLimitError: Max retries reached. Error: {e}")
                    return f"Error: OpenAI Rate Limit - Max retries exceeded. Last error: {e}" # Return error after max retries
                else:
                    print(f"OpenAI RateLimitError: Retrying in {self.retry_delay} seconds... (Retry {retries}/{self.max_retries})")
                    await asyncio.sleep(self.retry_delay) # Wait before retrying
                    continue # Continue to the next retry attempt

            except openai.APIError as e: # Catch other OpenAI API errors
                print(f"OpenAI API error: {e}")
                return f"Error: OpenAI API - {e}"
            except Exception as e: # Catch other exceptions
                print(f"An unexpected error occurred during GPT chat: {e}")
                return f"Error: Unexpected - {e}"



    async def chat_with_claude(self, messages):
        """Placeholder for Claude integration using OpenAI format."""
        print("Warning: Claude integration is a placeholder and might require further implementation to be fully functional.")
        return "Claude integration is not fully implemented in this version."



    async def chat_with_gemini(self, messages):
        """Chats with Google AI Studio (Gemini) models with API key polling and rate limit retry."""
        if not self.api_keys:
            return "Error: No API keys provided for Google AI Studio."

        for index in range(len(self.api_keys)): # Iterate through API keys
            api_key = self.api_keys[(self.current_key_index + index) % len(self.api_keys)] # Rotate through keys
            retries = 0 # Reset retries for each API key
            while retries <= self.max_retries: # Retry loop for rate limit
                try:
                    client = OpenAI(
                        api_key=api_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/" # Gemini API base URL
                    )

                    HEADERS = {"Content-Type": "application/json"}

                    response = client.chat.completions.create( # Use async client
                        model=self.module,
                        n=1,
                        messages=messages,
                        extra_headers = HEADERS,
                        max_tokens = self.max_tokens,
                        temperature = self.temperature
                    )


                    msg = response.choices[0].message.content
                    print_usage_info(response.usage) # Print token usage info
                    self.current_key_index = (self.current_key_index + index) % len(self.api_keys) # Update key index for next call
                    return msg # Success, return message and break retry loops

                except RateLimitError as e: # Catch RateLimitError specifically
                    retries += 1
                    if retries > self.max_retries:
                        print(f"Gemini RateLimitError with key index { (self.current_key_index + index) % len(self.api_keys)}: Max retries reached. Error: {e}")
                        break # Break retry loop for this key, try next key
                    else:
                        print(f"Gemini RateLimitError with key index { (self.current_key_index + index) % len(self.api_keys)}: Retrying in {self.retry_delay} seconds... (Retry {retries}/{self.max_retries})")
                        await asyncio.sleep(self.retry_delay) # Wait before retrying
                        continue # Continue to the next retry attempt with the same key

                except openai.APIError as e: # Catch other OpenAI API errors
                    print(f"Gemini API error with key index { (self.current_key_index + index) % len(self.api_keys)}: {e}")
                    if index == len(self.api_keys) - 1: # If all keys failed
                        return f"Error: Gemini API - All API keys failed. Last error: {e}" # Return error after trying all keys
                    else:
                        print(f"Trying next API key...") # Inform about key rotation attempt
                        break # Break retry loop for this key, move to next key
                except Exception as e: # Catch other exceptions
                    print(f"An unexpected error occurred during Gemini chat: {e}")
                    return f"Error: Unexpected - {e}"
            else: # This 'else' belongs to the 'while retries <= self.max_retries' loop, executed if the loop completes without 'break'
                continue # If retry loop for a key exhausted, continue to the next API key
            if index == len(self.api_keys) -1: # If all keys are tried and all failed after retries
                return f"Error: Gemini API - All API keys failed after multiple retries." # Return error after all keys and retries failed


def print_usage_info(usage):
    """Helper function to print token usage information."""
    print("Usage Info:")
    print(f"  Completion tokens: {usage.completion_tokens}")
    print(f"  Prompt tokens: {usage.prompt_tokens}")
    print(f"  Total tokens: {usage.total_tokens}")


if __name__=="__main__":
    # Example Usage and Testing

    async def main():
        open_ai = Open_Ai()
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