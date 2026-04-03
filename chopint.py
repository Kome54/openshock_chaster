"""
Chaster → OpenShock Bridge
==========================
Polls the Chaster API for lock events and forwards them as 
shock/vibrate/beep commands to the OpenShock API.
Polls at random times in seconds between these values you can change for faster or slow behaviour:
POLL_MIN = int()
POLL_MAX = int()

Requirements:
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

import os
import time
import json
import logging
import requests
import random
from datetime import datetime, timezone


# ─────────────────────────────────────────────
#  CONFIG  –  fill these in
# ─────────────────────────────────────────────

CHASTER_TOKEN=''
CHASTER_LOCK_ID=''  
OPENSHOCK_TOKEN=''
OPENSHOCK_SHOCKER_ID = [
    "",
    ""
]

# How often (seconds) to poll Chaster for new events
POLL_MIN = int(120)
POLL_MAX = int(240)

# ── OpenShock defaults (can be overridden per-event in EVENT_MAP below) ──
DEFAULT_INTENSITY = 30   # 1-100
DEFAULT_DURATION  = 1000 # milliseconds

# ─────────────────────────────────────────────
#  EVENT → SHOCK MAPPING
#  Map Chaster event types to OpenShock actions.
#  OpenShock types: "Shock", "Vibrate", "Sound", "Stop"
# ─────────────────────────────────────────────

def on_time_changed(ev):
    rolled = ev["payload"].get("diceRolled", 1)
    send_openshock_command(OPENSHOCK_SHOCKER_ID, "Shock", intensity=rolled * 10, duration=1000)




# ─────────────────────────────────────────────
#  LOGGING SETUP
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bridge")

# ─────────────────────────────────────────────
#  CHASTER CLIENT
# ─────────────────────────────────────────────

CHASTER_BASE = "https://api.chaster.app"

def chaster_headers():
    return {
        "Authorization": f"Bearer {CHASTER_TOKEN}",
        "Content-Type": "application/json",
    }

def get_lock_info(lock_id: str) -> dict | None:
    """Fetch basic info about a single lock."""
    url = f"{CHASTER_BASE}/locks/{lock_id}"
    try:
        r = requests.get(url, headers=chaster_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        log.error(f"[Chaster] HTTP error fetching lock: {e} | {r.text}")
    except Exception as e:
        log.error(f"[Chaster] Error fetching lock: {e}")
    return None

def get_lock_history(lock_id: str, limit: int = 20) -> list:
    """
    Fetch the most recent history entries for a lock.
    Endpoint: POST /locks/{lockId}/history  (requires a JSON body)
    Returns a list of event objects (newest first).
    """
    url = f"{CHASTER_BASE}/locks/{lock_id}/history"
    body = {"limit": limit}
    try:
        r = requests.post(url, headers=chaster_headers(), json=body, timeout=10)
        r.raise_for_status()
        data = r.json()
        # API returns { results: [...], ... }
        return data.get("results", data) if isinstance(data, dict) else data
    except requests.HTTPError as e:
        log.error(f"[Chaster] HTTP error fetching history: {e} | {r.text}")
    except Exception as e:
        log.error(f"[Chaster] Error fetching history: {e}")
    return []

def get_my_locks() -> list:
    """List all of your own locks (useful for discovering lock IDs)."""
    url = f"{CHASTER_BASE}/locks"
    try:
        r = requests.get(url, headers=chaster_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.error(f"[Chaster] Error fetching locks: {e}")
    return []

# ─────────────────────────────────────────────
#  OPENSHOCK CLIENT
# ─────────────────────────────────────────────

OPENSHOCK_BASE = "https://api.openshock.app"
OPENSHOCK_USER_AGENT = "ChasterOpenShockBridge/1.0"

def openshock_headers():
    return {
        "Open-Shock-Token": OPENSHOCK_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": OPENSHOCK_USER_AGENT,
    }



def send_openshock_command(
    shocker_ids,
    action_type: str = "Vibrate",
    intensity: int = DEFAULT_INTENSITY,
    duration: int = DEFAULT_DURATION,
) -> bool:
    """
    Send a control command to one or multiple OpenShock devices.

    shocker_ids: str OR list[str]
    action_type: "Shock" | "Vibrate" | "Sound" | "Stop"
    intensity  : 1–100
    duration   : milliseconds
    """

    # Normalize to list
    if isinstance(shocker_ids, str):
        shocker_ids = [shocker_ids]

    url = f"{OPENSHOCK_BASE}/2/shockers/control"

    payload = {
        "shocks": [
            {
                "id": sid,
                "type": action_type.lower(),  # API expects lowercase
                "intensity": intensity,
                "duration": duration,
            }
            for sid in shocker_ids
        ]
    }

    try:
        r = requests.post(url, headers=openshock_headers(), json=payload, timeout=10)
        r.raise_for_status()

        log.info(
            f"[OpenShock] ✓ Sent {action_type.upper()} to {len(shocker_ids)} device(s) | "
            f"intensity={intensity} | duration={duration}ms"
        )
        return True

    except requests.HTTPError as e:
        log.error(f"[OpenShock] HTTP error: {e} | {r.text}")
    except Exception as e:
        log.error(f"[OpenShock] Error: {e}")

    return False

def shock_sequence(intensity=50, duration=500, count=5):
    for i in range(count):
        send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Shock",
            intensity,
            duration
        )

        gap = int(random.uniform(6, 10))
        print(f"Next shock in {gap:.2f}s")
        time.sleep(gap)

        
def get_my_shockers() -> list:
    """List shockers on your account (useful for discovering shocker IDs)."""
    url = f"{OPENSHOCK_BASE}/1/shockers/own"
    try:
        r = requests.get(url, headers=openshock_headers(), timeout=10)
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception as e:
        log.error(f"[OpenShock] Error fetching shockers: {e}")
    return []

# ─────────────────────────────────────────────
#  BRIDGE LOGIC
# ─────────────────────────────────────────────


def handle_event(event: dict):
    event_type = event.get("type", "").lower()
    payload    = event.get("payload", {})
    event_time = event.get("createdAt", "?")

    log.info(f"[Event] type={event_type!r}  time={event_time}  payload={payload}")

    # ── TIME CHANGED ─────────────────────────────
    if event_type == "time_changed":
        duration = payload.get("duration", 0)

        if duration > 0:
        # ── CONFIG ─────────────────────────────
            BASE_TIME = 3600        # X threshold (seconds)
            MAX_INTENSITY = 100
            MIN_INTENSITY = 20
    
        # ── INTENSITY SCALES WITH TIME ─────────
            intensity = int((duration / BASE_TIME) * 40)
            intensity = max(MIN_INTENSITY, min(intensity, MAX_INTENSITY))

        # ── COUNT BASED ON TIME ────────────────
            count = max(1, duration // BASE_TIME)

        
              

            log.info(
                f"[Bridge] Time change: {duration}s → intensity={intensity}, count={count}"
            )

            shock_sequence(
                intensity=intensity,
                duration=1000,
                count=int(count),
                )

        else:
            log.info("[Bridge] Small or negative time change, skipping.")
    
    # ── PILLORY ─────────────────────────────

    elif event_type == "pillory_in":
         
        send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Shock",
            30,
            5000
        )
        
    elif event_type == "pillory_out":
        if duration > 0:
        # ── CONFIG ─────────────────────────────
            BASE_TIME = 10800        # X threshold (seconds)
            MAX_INTENSITY = 66
            MIN_INTENSITY = 20
    
        # ── INTENSITY SCALES WITH TIME ─────────
            intensity = int((duration / BASE_TIME) * 40)
            intensity = max(MIN_INTENSITY, min(intensity, MAX_INTENSITY))

        # ── COUNT BASED ON TIME ────────────────
            count = max(1, duration // BASE_TIME)

        
              

            log.info(
                f"[Bridge] Time change: {duration}s → intensity={intensity}, count={count}"
            )

            shock_sequence(
                intensity=intensity,
                duration=5000,
                count=int(count),
                )

        else:
            log.info("[Bridge] Small or negative time change, skipping.")
            
    
    
    # ── SHARED LINK TO DO ──────────────────────────
    elif event_type == "link_time_changed":
           send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Shock",
            50,
            15000
        )
            
    # ── HYGIENE START ──────────────────────────
    elif event_type == "temporary_opening_opened":
        send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Vibrate",
            33,
            2000
        )
    
    elif event_type == "temporary_opening_locked":
        send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Vibrate",
            33,
            2000
        )       

    
    elif event_type == "temporary_opening_locked_late":
        send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Vibrate",
            50,
            1000
        )
        # ── TASK  ─────────────────────────────
    elif event_type == "task_failed":
        failures  = payload.get("failCount", 1)

        intensity = 100
        duration  = 15
        
        shock_sequence(
                intensity=intensity,
                duration=1000,
                count=int(count),
        )

    
    elif event_type == "task_completed":
        send_openshock_command(
            OPENSHOCK_SHOCKER_ID,
            "Vibrate",
            50,
            1000
        )

    # ── UNKNOWN EVENT ──────────────────────────
    else:
        log.info(f"[Bridge] No handler for event type {event_type!r}")
        

def run_bridge():
    """
    Main polling loop.
    Keeps track of the most recently seen event ID and only
    processes events that arrived since the last poll.
    """
    log.info("=" * 60)
    log.info("  Chaster → OpenShock Bridge starting up")
    log.info("=" * 60)

    # ── startup checks ──────────────────────────────────────────
    log.info("[Init] Fetching lock info…")
    lock = get_lock_info(CHASTER_LOCK_ID)
    if lock:
        log.info(
            f"[Init] Lock found: {lock.get('title', 'Unnamed')} | "
            f"status={lock.get('status')} | "
            f"totalDuration={lock.get('totalDuration')}s"
        )
    else:
        log.warning("[Init] Could not fetch lock — check your CHASTER_LOCK_ID / token.")

    log.info("[Init] Fetching shockers…")
    shockers = get_my_shockers()
    if shockers:
        for s in shockers:
            log.info(f"[Init] Shocker: {s.get('name')} | id={s.get('id')}")
    else:
        log.warning("[Init] No shockers found — check your OPENSHOCK_TOKEN.")

    # ── seed the seen-events set with whatever is already in history ──
    log.info("[Init] Seeding history (won't replay old events)…")
    seen_ids: set[str] = set()
    initial = get_lock_history(CHASTER_LOCK_ID, limit=50)
    for ev in initial:
        seen_ids.add(ev.get("_id") or ev.get("id", ""))
    log.info(f"[Init] Seeded {len(seen_ids)} existing event(s). Starting poll loop.\n")

    # ── main loop ───────────────────────────────────────────────
    while True:
        try:
            log.debug("[Poll] Checking for new events…")
            events = get_lock_history(CHASTER_LOCK_ID, limit=20)

            new_events = []
            for ev in events:
                eid = ev.get("_id") or ev.get("id") or ""
                if eid and eid not in seen_ids:
                    new_events.append(ev)
                    seen_ids.add(eid)

            if new_events:
                log.info(f"[Poll] {len(new_events)} new event(s) detected!")
                # Process oldest first (history is newest-first)
                for ev in reversed(new_events):
                    handle_event(ev)
            else:
                log.info(f"[Poll] No new events.")

        except KeyboardInterrupt:
            log.info("\n[Bridge] Stopped by user. Goodbye!")
            break
        except Exception as e:
            log.error(f"[Bridge] Unexpected error: {e}")
            
        sleep_time = random.uniform(POLL_MIN, POLL_MAX)
        time.sleep(int(sleep_time))

# ─────────────────────────────────────────────
#  HELPERS  (run directly to inspect your accounts)
# ─────────────────────────────────────────────

def print_my_locks():
    """Print all your Chaster locks with their IDs."""
    locks = get_my_locks()
    print("\n── Your Chaster Locks ──")
    for lock in locks:
        print(f"  [{lock.get('status')}] {lock.get('title')}  id={lock.get('_id')}")

def print_my_shockers():
    """Print all your OpenShock shockers with their IDs."""
    shockers = get_my_shockers()
    print("\n── Your OpenShock Shockers ──")
    for s in shockers:
        print(f"  {s.get('name')}  id={s.get('id')}  model={s.get('model')}")

def test_shock(action: str = "Vibrate", intensity: int = 20, duration: int = 1000):
    """Quick test — fire one command at your shocker."""
    print(f"\nSending test {action} (intensity={intensity}, duration={duration}ms)…")
    ok = send_openshock_command(OPENSHOCK_SHOCKER_ID, action, intensity, duration)
    print("Success!" if ok else "Failed — check logs.")

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"

    if cmd == "locks":
        print_my_locks()
    elif cmd == "shockers":
        print_my_shockers()
    elif cmd == "test":
        action    = sys.argv[2] if len(sys.argv) > 2 else "Vibrate"
        intensity = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        duration  = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
        test_shock(action, intensity, duration)
    else:
        run_bridge()
