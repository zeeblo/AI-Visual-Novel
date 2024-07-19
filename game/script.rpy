


label custom_chat_model_label:
    "Enter a chat model, eg. gpt-4o, llama3-70b-8192"
    $ model = renpy.input("Enter a model", f"{persistent.chatModel}").strip()
    $ persistent.chatModel = model 
    $ renpy.save_persistent()
    return


label chat_token_label:
    $ token = renpy.input("Enter API Key", f"{persistent.chatToken}").strip()
    $ persistent.chatToken = token
    $ renpy.save_persistent()
    return


label img_token_label:
    $ token = renpy.input("Enter API Key", f"{persistent.imgToken}").strip()
    $ persistent.chatModel = token
    $ renpy.save_persistent()
    return



label go_back:
    "..."
    $ MainMenu()
    return


label start:


    init python:
        import threading
        config.has_autosave = False
        config.has_quicksave = False
        config.autosave_on_quit = False
        config.autosave_on_choice = False



    jump AICharacter

    return



label AICharacter:
    $ tokenSetter.set_token()
    $ persistent.in_game = True
    $ renpy.save_persistent()
    scene black with dissolve

    $ resume = None # Used to check if a file has been loaded

    "Type one of the character names in characters.json to start interacting with that character. (Not case sensitive)"
    $ all_characters = Info().characters
    $ characterSelect = ""
    while characterSelect.lower() not in all_characters:
        $ characterSelect = renpy.input("Character Name: ", "Sam", allow=" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_").strip()
        if characterSelect.lower() not in all_characters:
            "This character was not found. Try again."


    # "num" is a default value set to None. If a number is
    # assigned to it, that means the user is opening an old file
    if num != None:
        if num >= 0:
            $ resume = True
            $ pathSetup = f"{config.basedir}/chats/"+persistent.chatFolderName[num]
            $ current_char = Data(path_to_user_dir=pathSetup).getSceneData("character")

            $ chatSetup = SetupChat(chat_name=persistent.chatFolderName[num], character_name=current_char)
            $ memory = Data(path_to_user_dir=pathSetup).getChathistory
            $ SetVariable("num", None)

    else:
        $ chatFolderName = renpy.input("Name This Realm: ", "realm", allow=" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_").strip()
        $ chatSetup = SetupChat(chat_name=chatFolderName, character_name=characterSelect)
        $ pathSetup = chatSetup.setup()

        # Start generating text in a separate thread
        $ chatSetup.is_generating = True
        $ threading.Thread(target=chatSetup.chat, args=[pathSetup, [], "hello"]).start()

        $ _history = False
        $ wait_msg = ""

        # Wait for AI to finish generating text
        while chatSetup.is_generating == True:
            # If you want to add a popup menu or some sort of animation, you can do so here
            $ wait_msg = wait_msg + "." if len(wait_msg) < 3 else "."
            "Loading[wait_msg] {fast} {w=0.7}{nw}"

        $ _history = True
        $ convo = chatSetup.generated_text



    ###########################
    # Setup old/new data
    ###########################
    $ memory = Data(path_to_user_dir=pathSetup).getChathistory
    $ current_char = Data(path_to_user_dir=pathSetup).getSceneData("character")
    $ current_char_title = current_char.title()
    $ current_sprite = Data(path_to_user_dir=pathSetup).getSceneData("sprite")
    $ current_background = Data(path_to_user_dir=pathSetup).getSceneData("background")


    image _bg:
        zoom 1.5
        "bg/[current_background]"
    scene _bg




    if resume:
        $ last_msg = Data(path_to_user_dir=pathSetup).getLastMessageClean

        image full_sprite:
            im.Composite((960, 960), (0, 0), f"characters/{current_char}/{current_sprite}")
            uppies

        show full_sprite

        if current_char_title != "":
            $ renpy.say("[current_char_title]", last_msg)


    else:
        $ renpy.say(current_char, convo)


    ###########################
    # Main Event Loop
    ###########################
    $ main_event_loop = True
    while main_event_loop == True:
        $ user_msg = ""
        $ rnd_continue = renpy.random.randint(1, 6)
        $ current_char = Data(path_to_user_dir=pathSetup).getSceneData("character")

        if current_char != "" and rnd_continue == 4:
            # Randomly continue the chat to have variety so it's not a constant back and forth
            $ user_msg = "continue"
        else:
            while user_msg.strip() == "":
                $ user_msg = renpy.input("Enter a message: ")


        # Start generating text in a separate thread
        $ chatSetup.is_generating = True
        $ threading.Thread(target=chatSetup.chat, args=(pathSetup, memory, user_msg)).start()

        $ _history = False # Disable history so the "Loading" msg isn't spammed in there.
        $ wait_msg = ""

        # Wait for AI to finish generating text
        while chatSetup.is_generating == True:
            $ wait_msg = wait_msg + "." if len(wait_msg) < 3 else "."
            "Loading[wait_msg] {fast} {w=0.7}{nw}"

        $ _history = True # Re-enable history to show the actual dialog

        $ final_msg = chatSetup.generated_text
        $ raw_msg = Data(path_to_user_dir=pathSetup).getLastMessage

        $ current_char = Data(path_to_user_dir=pathSetup).getSceneData("character")
        $ current_char_title = current_char.title()
        $ current_sprite = Data(path_to_user_dir=pathSetup).getSceneData("sprite")
        $ current_background = Data(path_to_user_dir=pathSetup).getSceneData("background")

        if raw_msg.startswith("[SCENE]"):
            image _bg:
                "bg/[current_background]"
            scene _bg



        if final_msg.startswith("<Error>"):
            show screen error_popup(message=final_msg)
        else:
            image full_sprite:
                im.Composite((960, 960), (0, 0), f"characters/{current_char}/{current_sprite}")
                uppies

            show full_sprite


            $ renpy.say("[current_char_title]", final_msg)
    return
