


label custom_chat_model_label:
    $ model = renpy.input("Enter a model", f"{persistent.chatModel}").strip()
    $ persistent.chatModel = model 
    $ renpy.save_persistent()
    return




label start:


    "You've created a new Ren'Py game."

    "Once you add a story, pictures, and music, you can release it to the world!"


    return



