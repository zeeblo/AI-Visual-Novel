# Change character sprite

**When adding a new character do the following**


- add new folder w/ sprites
- add new name to characters.json
- add new name to prompt_templates.json



### New folder

- Create a new folder in `game\images\characters`
- The name of the folder should be the name of your character
- Fill the folder with character sprites
- The images should ideally be 960x960

### character.json

- go to `game\assets\configs\characters.json`
- Add the name of the character you want
- Reference the structure you see in the file.
- Replace the emotions with the emotions you want.

The emotions that don't end in `.png` is what the AI will see.
Just add the .png sprites you have in your characters folder.

### prompt_template.json

- go to `game\assets\prompts\prompt_templates.json`
- Add the name of the character you want
- Reference the structure you see in the file.
- Add background information about your character
- Make sure at the end of your message, you have "{{format}}" just like the other things in the file.



# Default Backgrounds

**When adding a new background do the following**

- add new background image in `game\images\bg`
- add new background name in `game\assets\configs`

Once you've added the images you want in `game\images\bg`

- go to `game\assets\configs`
- remove the default background images (if you want, you don't have to)
- add the name of your background image in the "default" dictionary.

eg. I want to add a "park" as a default background.

The name of my background image is "park-day-1.png" so this is how I'd write it in the json

```json
    "default": {
        "park": "park-day-1.png",
    }
```

You'll notice that there's another key in the json called "checks".
Everything inside "checks" is a backup just incase the AI doesn't correctly spell something correctly.

For example, all the default backgrounds are injected into the system prompt by default and we display a scene by using 1 of those injected scenes
but what if the AI "hallucinates" and doesn't correctly spell the default scene correctly?

"checks" is used as a potential typo that the AI may make so that it falls back onto the correct scene.

so for example

```json
    "checks": {
        "parks": "park-day-1.png"
    }
```

maybe instead of the ai returning "park" like we instructed, it returns "parks". This check here ensures that we get the appropriate scene and not something else.