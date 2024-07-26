import socketio
from pynput import keyboard, mouse
import time
import json


# Initialize Socket.IO client
sio = socketio.Client()

#set this client to a raspberry pi room
room_ip = '141.34.8.31'

# Define your server URL
SERVER_URL = 'https://robotdashboard.medien.ifi.lmu.de'

# Timeout duration (2 minutes)
TIMEOUT_DURATION = 1.0

# Timestamp to track last activity time
last_activity_time = time.time()

# Flag to track activity state
active = False

# Function to send notifications
def send_notification(message):
    print('keylogger-notification: ', message)
    #message = json.dumps(message)
    sio.emit('keylogger_notification_room', message)

# Function to handle activity detected
def on_activity_detected():
    global active
    if not active:
        send_notification({'status': 'active', 'room': room_ip})
        active = True

# Function to handle inactivity
def check_inactivity():
    global last_activity_time, active
    current_time = time.time()
    print('time_difference: ', current_time - last_activity_time)

    if (current_time - last_activity_time > TIMEOUT_DURATION):
        send_notification({'status': 'inactive', 'room': room_ip})
        active = False

# Keyboard listener
def on_press(key):
    global last_activity_time
    last_activity_time = time.time()
    on_activity_detected()
    # Implement key logging or other actions here

def on_release(key):
    pass

# Mouse listener
def on_move(x, y):
    global last_activity_time
    last_activity_time = time.time()
    on_activity_detected()

def on_click(x, y, button, pressed):
    global last_activity_time
    last_activity_time = time.time()
    on_activity_detected()

def on_scroll(x, y, dx, dy):
    global last_activity_time
    last_activity_time = time.time()
    on_activity_detected()

# Start listeners
def start_listening():
    try:
        sio.connect(SERVER_URL)
        print('Keylogger connected to server')
        # tell server this is a keylogger
        sio.emit('keylogger', room_ip)


        # Configure keyboard listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as k_listener:

            # Configure mouse listener
            with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as m_listener:
                sio.emit('keylogger_message', 'Keylogger Started')  # Send initial notification that keylogger is active

                # Main loop to check for inactivity
                while True:
                    check_inactivity()
                    time.sleep(60)  # Check every minute for activity

    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == '__main__':
    start_listening()
