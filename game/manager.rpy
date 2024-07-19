init python:
    import json
    import os
    import random
    import requests
    import math
    import time
    import io
    import re
    import base64


    with open(config.basedir + "/game/assets/prompts/prompt_templates.json", "r") as f:
        prompt = json.load(f)

    retrycount = 3

    class AIManager():
        def __init__(self, character_name, chathistory, full_path, resume=False):
            self.character_name = character_name
            self.chathistory = chathistory
            self.full_path = full_path
            self.resume = resume
            self.NARRATION = False
            self.rnd = random.randint(1,7)
            self.retrying = False
            self.dbase = Data(path_to_user_dir=self.full_path)




        def controlMood(self, face):
            """Display different facial expressions"""
            if not face: return

            char_name = Configs().characters[self.character_name.title()]
            sprite = char_name["sprite"]

            self.dbase.updateSceneData("character", self.character_name)

            for h in sprite:
                if h == face.lower():
                    self.dbase.updateSceneData("sprite", sprite[h])





        def generate_ai_background(self, guide):
            """Generates unique AI background if it doesn't already exist in the bg folder"""
            ai_art_path = config.basedir + "/game/images/bg/"+ guide + ".png"
            if os.path.exists(ai_art_path):
                guide = guide + ".png"
                self.dbase.updateSceneData("background", guide)
                self.dbase.updateSceneData("gen", "y")
                self.scene = guide
                self.ai_art_mode = True
                return self.scene

            
            result = ImageModel().getimgai(guide)
            guide = guide + ".png"
            if "error" not in result:
                with open(f"{config.basedir}/game/images/bg/{guide}", "wb") as f:
                    f.write(base64.b64decode(result["image"]))
                    self.dbase.updateSceneData("background", guide)
                    self.dbase.updateSceneData("gen", "y")
                    self.scene = guide
                    return guide
            else:
                self.dbase.updateSceneData("gen", "")
                return self.dbase.updateSceneData("background", bg_scenes['default']["art room"])





        def controlBackground(self, scene):
            """Display different background image"""
            if not scene: return

            bg_scenes = Configs().bg_scenes
            for key in ('default', 'checks'):
                if scene in bg_scenes[key]:
                    self.dbase.updateSceneData("gen", "")
                    return self.dbase.updateSceneData("background", bg_scenes[key][scene])

            return self.generate_ai_background(scene)




            
        def safeResponse(self, raw_response):
            """A response that's not entirely raw. If the AI
            speaks out of character but still returns the correct
            format, only capture the format it outputs"""
            clean_response = raw_response
            if "[SCENE]" in clean_response:
                clean_response = "[SCENE]" + clean_response.split("[SCENE]")[1]

            if "[CONTENT]" in clean_response:
                clean_response = re.sub(r'\*.*?\*', '', clean_response) # gets rid of anything in asterisks

            return clean_response




        def removeKeywords(self, reply):
            """Get rid of keywords and return a clean string"""

            def getContent(start, end, reply=reply):
                try:
                    content = reply.split(start)[1].split(end)[0].strip()
                    return content
                except IndexError:
                    return None
                except AttributeError:
                    return None

            scene = getContent('[SCENE]', '[FACE]')
            face = getContent('[FACE]', '[CONTENT]')
            reply = reply.split('[END]')[0]

            if scene:
                # Sometimes a model responds w/ text before [SCENE]
                # This removes any text before and only keeps [SCENE] and
                # everything that comes after it
                reply = "[SCENE] " + reply.split("[SCENE]")[1]

            if "[CONTENT]" in reply:
                reply = reply.split("[CONTENT]")[1].strip()

                # If the character replies with smthing like *giggles* remove it.
                # (and yes im using regex here)
                reply = re.sub(r'\*.*?\*', '', reply)

            else:
                # Typically this means that the model didnt return a proper content field
                reply = "ERROR"

            return reply, face, scene



        def removePlaceholders(self):
            """remove placeholders in json files"""
            level_normal = Info().getExamplePrompts[f"{self.character_name}"]
            raw_examples = level_normal 

            bg_scenes = [s for s in Configs().bg_scenes["default"]]
            emotions = ', '.join([e for e in Configs().characters[self.character_name.title()]['sprite']])
            backgrounds = ', '.join(bg_scenes)

            string = raw_examples[0]['content'].replace("{{format}}", Info().format["roleplay"])
            string = string.replace("{{char}}", self.character_name)
            string = string.replace("{{emotes}}", emotions)
            string = string.replace("{{scenes}}", backgrounds)
            string = string.replace("{{user}}", persistent.playername)


            # Basically, if the user has generate_imgs enabled then the AI should
            # come up with different scene names if it's not in the default scenes.
            # If it's disabled then the AI should not allow the user to go anywhere else
            conditional = "the user can optionally go anywhere not listed as well" if persistent.generate_imgs else Info().getReminder["conditional"].replace("{{char}}", self.character_name)
            string = string.replace("{{conditional}}", f"- {conditional}")

            string = raw_examples[0]['content'] = string
            raw_examples[0]['content'] = string


            with open(self.full_path + f"/full_history.json", 'w') as f:
                json.dump(raw_examples + self.chathistory, f, indent=2)

            return raw_examples




        def checkForContextLimit(self, range=120, contains_system_prompt=False):
            """Estimates the amount of tokens in the chathistory.
            If the max context window for an LLM is set to (for eg.) 1024 then if the tokens
            exceed that amount, the start of the chathistory will be deleted.
            
            Both the user message and the assistant message.

            Args:
                range -- the amount of words it will take before clearing up the chat. eg.
                        if the max context window is 1024, with a range of 40 and the current
                        context of the chathistory is >= 984 then it will delete the chat (first 2 msgs or more)
                        once the current tokens reach 984 or higher.
                
                contains_system_prompt -- Determines if the first index should be deleted or skipped
                                        (which would typically be the system prompt)
            """

            max_tokens = int(persistent.context_window)
            delete_pos = 0 if contains_system_prompt == False else 1
            current_tokens = self.count_tokens()

            # Continues to delete the chat from the top if
            # The current_tokens is still greater than max_tokens
            while (current_tokens) >= max_tokens - range:
                self.chathistory.pop(0 + delete_pos)
                self.chathistory.pop(1 + delete_pos)
                with open(f"{self.full_path}/chathistory.json", 'w') as f:
                    json.dump(self.chathistory, f, indent=2)
                print("***POPPED 2 MESSAGES***")
                current_tokens = self.count_tokens()




        def count_tokens(self):
            current_tokens = 0
            for content in self.chathistory:
                words_amnt = len(content['content'].split())
                current_tokens += words_amnt
            return current_tokens



        def retryPrompt(self, reply, current_emotion):
            """If the generated response doesnt use the emotions specified in the characters.json list
            eg. '[FACE] super shy' then remind the ai to only use what's in
            the list and redo the response
            """
            if current_emotion:
                if current_emotion not in Configs().characters[self.character_name.title()]["sprite"]:
                    print("<<retrying>>")
                    return True
            return False



        def checkForError(self, reply):
            """If An error happened with the API, return the Error"""
            try:
                if reply[0] == False:
                    false_return = reply[0]
                    error_message = reply[1]
                    return false_return, error_message
            except TypeError:
                return False




        def checkForBadFormat(self, response):
            """It writes a default narration if the ai generates an incorrectly formatted response 
            Only runs once when the realm is first loaded."""
            if "[SCENE]" not in response or "[FACE]" not in response or "[CONTENT]" not in response:
                response = "[SCENE] art room [FACE] happy [CONTENT] Hey [END]"
            return response



        def modelChoices(self, prompt):
            groq = chat_model_dict["groq"]["suggested"] + chat_model_dict["groq"]["other"]
            openai = chat_model_dict["openai"]["suggested"] + chat_model_dict["openai"]["other"]

            if persistent.chatModel in groq:
                return TextModel().getGroq(prompt=prompt)
            elif persistent.chatModel in openai:
                return TextModel().getGPT(prompt=prompt)
            else:
                return TextModel().getLLM(prompt=prompt)


        def ai_response(self, userInput):
            """Gets ai generated text based off given prompt"""

            emotions = ', '.join([e for e in Configs().characters[self.character_name.title()]['sprite']])
            reminder = "" if self.retrying == False else Info().getReminder["emotes"].replace("{{emotes}}", emotions)

            # Log user input
            self.chathistory.append({"role": "user", "content": userInput + reminder})

            # Make sure the user's msg doesn't go over the context window
            self.checkForContextLimit()
            examples = self.removePlaceholders()
            contextAndUserMsg = examples + self.chathistory

            response = self.modelChoices(contextAndUserMsg)
            self.dbase.updateSceneData("character", self.character_name)

            response = self.checkForBadFormat(response)


            # If An error happened with the API, return the Error
            check_error = self.checkForError(response)
            if check_error:
                return check_error[1]

            reply, face, scene = self.removeKeywords(response)

            # If the AI responds w/ an emotion not listed, redo the response
            global retrycount
            self.retrying = self.retryPrompt(response, face)
            if self.retrying:
                retrycount -= 1
                if retrycount <= 0:
                    self.retrying = False
                    retrycount = 3
                else:
                    self.chathistory.pop()
                    return self.ai_response(userInput)

            # Log AI input
            response = self.safeResponse(response)
            response = response.split('[END]')[0] + " [END]"


            self.chathistory.append({"role": "assistant", "content": response})

            self.controlMood(face)
            self.controlBackground(scene)

            with open(f"{self.full_path}/chathistory.json", 'w') as f:
                json.dump(self.chathistory, f, indent=2)
            return reply

