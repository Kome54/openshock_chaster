Chaster → OpenShock Bridge
==========================

it works, values i made for myself so tweak them if you dont want strong shocks.
Im not a developer so it isnt pretty code and i used a lot of ai help, disclosing in case the code looks weird,i dont mind forking out and someone else improving, this is most a proof of concept.

Requirements:

    chaster developer privileges
    
    python
    
    pip install requests 
    
Setup:
    Fill these constants directly:
    
    the constants require '' so the right way would look like this: 'dsghklfdkhdjknk'
    
    CHASTER_TOKEN=''  'on the developer mode, need to create a aplication and within the aplication there a token menu
    
    CHASTER_LOCK_ID=''  'just the part of the link where there a bunch of characterers like this '694b4784agfdgdhgjho545fgdg5'
     
    OPENSHOCK_TOKEN=''  'go on openshock.app and generate a token on Api tokens
       
      
    OPENSHOCK_SHOCKER_ID = ''
    
    or
    
    OPENSHOCK_SHOCKER_ID = [  
    "",
    "",
    ""
    ]  

On openshock.app shocker page, click the 3 dots in the shocker section, click edit and you can find the id, there 2 ways of inputing the first one supports only 1 collar, the second one each line supports 1 collar and you can add or remove extras in case you wanna multiples shockers working together'  
  
IF YOU WANNA MESS WITH THE SHOCKING BEHAVIOUR IS ALL ON 'def handle_event' as a bunch of if statments each one has its own logic that you can mess, look at a how it works and adapt for how you want to behave, creating new ones is simple just copy one elif already made and change event_type .

You can find the events list on:https://docs.chaster.app/api/reference/action-logs or by the logging printing that happens every time your lock does something.


EXTRA: 
IS POSSIBLE TO RUN ON YOUR ANDROID PHONE WITH AN APP CALLED Termux it requires a bit of a setup but it isnt super complex , idk if is possible on ios.
First run these commands in this order:

    termux-setup-storage                    (give termux permission for local archives)             
    pkg update && pkg upgrade
    pkg install python tmux
    pkg install nano git
    pip install requests
    termux-wake-lock                        (for the app run in the background)
    tmux     
    cd /storage/emulated/0/Download         (folder where the script is, you can adapt depending where it is or put in download)
    python chopint.py                       (it should run the script)

TO STOP IT, PRESS CTRL and type C
  

"""
