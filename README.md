"""
Chaster → OpenShock Bridge
==========================
Polls the Chaster API for lock events and forwards them as 
shock/vibrate/beep commands to the OpenShock API.
Polls at random times in seconds between these values you can change for faster or slow behaviour:
POLL_MIN = int()
POLL_MAX = int()

Requirements:
    chaster developer privileges 
    python
    pip install requests 
    

Setup:
    Fill in this constants directly:
    the constants require '' so the right way would look like this: 'dsghklfdkhdjknk'
    CHASTER_TOKEN=''  'on the developer mode, need to create a aplication and within the aplication there a token menu
    CHASTER_LOCK_ID=''  'just the part of the link where there a bunch of characterers like this '694b4784agfdgdhgjho545fgdg5'
    OPENSHOCK_TOKEN=''  'go on openshock.app and generate a token on Api tokens
    
    'on shocker page, click the 3 dots in the shocker section, click edit and you can find the id, there 2 ways of inputing the first one supports only 1 collar, the second one each line supports 1 collar and you can add or remove extras in case you wanna multiples shockers working together'
    
1   OPENSHOCK_SHOCKER_ID = ''
2   OPENSHOCK_SHOCKER_ID = [  
    "",
    "",
    ""
  ]  
  
  
IF YOU WANNA MESS WITH THE SHOCKING BEHAVIOUR IS ALL ON 'def handle_event' as a bunch of if statments each one has its own logic that you can mess, look at a how it works and adapt for how you want to behave, creating new ones is simple just copy one elif already made and change event_type .

You can find the events list on:https://docs.chaster.app/api/reference/action-logs or by the logging printing that happens every time your lock does something.


EXTRA: 
IS POSSIBLE TO RUN ON YOUR ANDROID PHONE WITH AN APP CALLED Termux it requires a bit of a setup but it isnt super complex , idk if is possible on ios
first run these commands in this order:

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
