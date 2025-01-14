import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import threading
import serial

CLIENT_ID = "55985fc6751c4c5ea97d044ebe0861ca"
CLIENT_SECRET = "e680c5ac23264c0593a3ea15148b172d"
REDIRECT_URI = "https://localhost:8080"

scope = 'user-modify-playback-state, user-read-playback-state'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,scope=scope))


    
def openPort():
    try:
        ser = serial.Serial("/dev/ttyACM0",115200,timeout=1)
        ser.reset_input_buffer()
    except serial.serialutil.SerialException:
        print("Could not open port, retrying in 1 second")
        time.sleep(1)
        openPort()
    
openPort()


while True:
    # Get current song data from API
    current_playback = spotify.current_playback()
    
    print("Currently playing: " + current_playback["item"]["name"])
    
    # Send song data to Arduino via serial 
    # Message format: songName > artistName @ isPlaying # progress $ duration % repeatState ^ shuffleState &
    message = current_playback["item"]["name"] + ">" + ', '.join([artist["name"] for artist in current_playback["item"]["album"]["artists"]]) + "@" + ("1" if current_playback["is_playing"] else "0") + "#" + str(current_playback["progress_ms"]) + "$" + str(current_playback["item"]["duration_ms"]) + "%" + ("0" if current_playback["repeat_state"] == "off" else "1") + "^" + ("1" if current_playback["shuffle_state"] else "0") + "&"
    # print(message) # Uncomment this to debug
    ser.write(bytes(message, "utf-8"))
    
    
    # Read Arduino message (if any is sent)
    arduino_message = ser.readline().decode("utf-8").strip()
    if len(arduino_message) > 0:
        print("Recieved message from arduino:", arduino_message)
        
    
    # Send request to API corresponding to Arduino message
    if arduino_message == "pause":
        spotify.pause_playback()
    elif arduino_message == "play":
        spotify.start_playback()
    elif arduino_message == "prev":
        spotify.previous_track()
    elif arduino_message == "next":
        spotify.next_track()
    elif arduino_message == "shuffleOn":
        spotify.shuffle(True)
    elif arduino_message == "shuffleOff":
        spotify.shuffle(False)
    elif arduino_message == "repeatOn":
        spotify.repeat("track")
    elif arduino_message == "repeatOff":
        spotify.repeat("off")
    
        
    
    time.sleep(1)

