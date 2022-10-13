# -*- coding: utf8 -*

import cmd, sys, os, random, time, _thread, threading, traceback, asyncio, pyttsx3
import RPi.GPIO as GPIO
from pygame import mixer
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

sound_dir = './sounds'
patience_time_in_seconds = 60
impatient_message = "Kérlek hagyd el ezt a helyet mert már jönnek érted"
event_sound_enabled = True
some_motherfucker_is_sitting_there = False
ass_sensor_pin = 7
led_pin = 12
language = 'hungarian'
tts = None
stop_loop = False

host_name = '0.0.0.0'
host_port = 8000

def say(line):
    tts.say(line)
    tts.runAndWait()

def say_random():
    file = open("./lines.txt", "r")
    lines = file.read().splitlines()
    file.close()
    if len(lines) > 0:
        line = random.choice(lines)
        print('Saying', line)
        tts.say(line)
        tts.runAndWait()


def play_dir(dir):
    files = [ f for f in os.listdir(dir) if f.endswith('.mp3') ]
    if len(files) > 0:
        print ('Playing: '+os.path.join(dir,random.choice(files)))
        play(os.path.join(dir,random.choice(files)))
    else:
        print('No files have been found!')

def play(file):
    if not mixer.music.get_busy():
        try:
            print ('Playing: '+file)
            mixer.music.load(file)
            mixer.music.play()
        except:
            print('Cannot play: '+file)


class Shell(cmd.Cmd):
    intro = 'The Truth Speaking Chair (powered by ???????) welcomes you. Type help or ? to list commands.\n'
    prompt = '> '

    def default(self, line):
        self.do_say(line)

    def do_say(self, line):
        'Saying things out loud.'
        print ('Saying: '+line)
        say(line)

    def do_play(self, line):
        'Play audio file'
        play(line)

    def do_play_dir(self, line):
        'Play random mp3 file from the given dir'
        play_dir(line)

    def do_lang(self, line):
        'Set the speaking language.'
        tts.setProperty('voice', line)
    
    def do_exit(self, line):
        'Exit'
        stop_loop = True
        time.sleep(0.5)
        exit()

    def do_say_random(self, line):
        say_random()


class WebSocket(BaseHTTPRequestHandler):
    """
        Hosts a web page with an input field
        Entered text is sent with a POST request, and is read aloud by TTSx3
    """
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        html = '''
            <html>
            <meta charset="UTF-8">
            <body style="margin: 20px; width: 500px; font-size: 30px;">
            <h1>Gecis fotel xd</h1>
            <p>Mondja ezt a szék:</p>
            <form action="/" method="POST">
                <input type="text" name="say" style="margin: 10px; font-size: 30px;"/>
                <input type="submit" value="Mondjad" style="margin: 10px; font-size: 30px;"/>
                <br>
                <input type="submit" name="playrandom" value="Mondjon valami random felvett dolgot" style="margin: 10px; font-size: 30px;"/> 
                <input type="submit" name="sayrandom" value="Olvasson fel valami random dolgot" style="margin: 10px; font-size: 30px;"/>
                <input type="submit" name="playxfiles" value="X akták zene" style="margin: 10px; font-size: 30px;"/>
            </form>
            </body>
            </html>
        '''
        self.do_HEAD()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])    # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")   # Get the data
        if "playrandom" in post_data:
            print("Got a request to play something random")
            play_dir("./sounds")
        elif "sayrandom" in post_data:
            print("Got a request to say something random")
            say_random()
        elif "playxfiles" in post_data:
            print("Playing x-files theme")
            play("./sounds/effects/x-files.mp3")
        else:
            post_key = post_data.split("=")[0]
            post_data = post_data.split("=")[1]    # Only keep the value
            # post_data = post_data[0:-7] # get rid of &submit
            post_data = post_data.replace("+", " ")

            post_data = urllib.parse.unquote(post_data)

            if(post_key == "say"):
                print("Got a request to say:",post_data)
                say(post_data)
        self._redirect('/')



def event_loop(sh):
    global event_sound_enabled
    global some_motherfucker_is_sitting_there
    global sit_start

    some_motherfucker_is_sitting_there = not GPIO.input(ass_sensor_pin)
    prev=True
    while True:
        inputValue = GPIO.input(ass_sensor_pin)

        if (prev == True and inputValue == False):
            sit_start = datetime.now()
            some_motherfucker_is_sitting_there = True
            print("Motherfucker has just sat in that fucking chair!")
            if event_sound_enabled:
                play_dir(sound_dir)

        if (prev == False and inputValue == True):
            some_motherfucker_is_sitting_there = False
            print("Finally, that ass has just moved away...")
            if event_sound_enabled:
                # say('Egy öröm volt! Viszlát!')
                pass
        
        if some_motherfucker_is_sitting_there:
            diff = (datetime.now() - sit_start).total_seconds()
            if event_sound_enabled:
                if diff >= patience_time_in_seconds:
                    say(impatient_message)
        
        prev = inputValue
        time.sleep(0.3)

def pulseLed():
    pwm = GPIO.PWM(led_pin, 100)
    brightness = 10
    pwm.start(brightness)
    increment = 2.5
    while not stop_loop:
        if brightness > 100:
            brightness = 100
        if brightness < 0:
            brightness = 0
        pwm.ChangeDutyCycle(brightness)
        if (brightness >= 100) or (brightness <= 0):
            increment = -increment
        if some_motherfucker_is_sitting_there:
            brightness = brightness + increment * 6
        else:
            brightness = brightness + increment
        time.sleep(0.1)
    pwm.stop()

    

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(ass_sensor_pin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.OUT)
    tts = pyttsx3.init()
    tts.setProperty('voice', language)
    tts.setProperty('rate', 125)
    mixer.pre_init(devicename="Audio Device Analog Stereo")
    mixer.init()
    shell = Shell()
    try:
        _thread.start_new_thread(event_loop,(shell,))
        server = HTTPServer((host_name, host_port), WebSocket)
        _thread.start_new_thread(server.serve_forever, ()) 
        _thread.start_new_thread(pulseLed, ())
    except:
        print('Cannot start event loop.')
        traceback.print_exc()

    shell.cmdloop()
