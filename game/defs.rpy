##################################
# Model Configs
##################################
define default_context_window = "1024"
define default_temp = "6"
define default_seed = "random"
define chatModel = "llama3"
define default_prompt_header = "level1"

default persistent.context_window = default_context_window
default persistent.temp = default_temp
default persistent.seed = default_seed
default persistent.prompt_header = default_prompt_header

default context_window = persistent.context_window
default temp = persistent.temp
default seed = persistent.seed
default prompt_header = persistent.prompt_header 



default persistent.chatModel = None
default persistent.imgModel = None
#define persistent.charVoice = None
default persistent.chatToken = None
define persistent.imgToken = None


default llm_mode = True
default persistent.chatModel = chatModel
default persistent.chatToken = ""



##################################
default character_name = ""
default num = None
default persistent.in_game = False
define chat_model_dict = {
    "openai": {
        "suggested": ["gpt-4o", "gpt-4-1106-preview"],
        "other": ["gpt-3.5-turbo-1106"]
    },
    "groq": {
        "suggested": ["llama3-70b-8192"],
        "other": []
    },
    "llms": {
        "suggested": ["llama3"],
        "other": ["mistral"]
    }
}

define persistent.chatFolderName = None