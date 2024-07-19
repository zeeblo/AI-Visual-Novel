init python:
    import os
    import random
    import requests
    import base64

    class TextModel:

        def __init__(self):
            self.tokens = Configs().config


        def getGPT(self, prompt):
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.tokens['GPT']}"
            }
            payload = {
                "model": persistent.chatModel, # gpt-4-1106-preview, gpt-4-turbo, gpt-4-turbo-2024-04-09, gpt-3.5-turbo-1106, gpt-3.5-turbo-16k
                "max_tokens": 200,
                "temperature": float(f".{persistent.temp}"),
                "stop": "[END]",
                "messages": prompt
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip() + " [END]"

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return False, f"<Error> {e}"



        def getGroq(self, prompt):
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.tokens['GROQ']}"
            }
            payload = {
                "model": persistent.chatModel, # llama3-70b-8192, llama3-8b-8192, mixtral-8x7b-32768
                "max_tokens": 200,
                "temperature": float(f".{persistent.temp}"),
                "stop": "[END]",
                "messages": prompt
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip() + " [END]"

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return False, f"<Error> {e}"




        def getLLM(self, prompt):
            if persistent.seed == "random":
                options = {
                    "options": {
                        "temperature": float(f".{persistent.temp}"),
                        "stop": ['[INST', '[/INST', '[END]'],
                        "num_ctx": int(persistent.context_window)
                        }
                }
            else:
                options = {
                    "options": {
                        "temperature": float(f".{persistent.temp}"),
                        "stop": ['[INST', '[/INST', '[END]'],
                        "num_ctx": int(persistent.context_window),
                        "seed": persistent.seed
                        }
                }

            response = requests.post(
                "http://localhost:11434/v1/chat/completions",
                json={"model": persistent.chatModel, "messages": prompt, "stream": False,
                    "options": options["options"]},
            )

            try:
                response.raise_for_status()
                data = response.json()
                result = data["choices"][0]["message"]["content"] 

                if "[END]" not in result:
                    return result + " [END]"
                return  result

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return False, f"<Error> {e}"






    class ImageModel:

        def __init__(self):
            self.tokens = Configs().config

        def getimgai(self, guide):
            url = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"
            with open(f"{config.basedir}/game/assets/prompts/img_generation.json") as f:
                scene = json.load(f)

            payload = {
                "model": "dark-sushi-mix-v2-25",
                "prompt":  scene["getimg"]["prompt"].replace("<guide>", guide),
                "negative_prompt": scene["stable"]["negative"],
                "width": 1024,
                "height": 1024,
                "steps": 30,
                "guidance": 9,
                "output_format": "png"
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {self.tokens['GETIMG']}"
            }

            r = requests.post(url, json=payload, headers=headers).json()
            return r


