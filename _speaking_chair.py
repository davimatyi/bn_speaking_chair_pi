import cmd, sys, os, random, time, _thread
import RPi.GPIO as GPIO
import pyttsx3
from pygame import mixer
from datetime import datetime
import traceback
import asyncio

sound_dir = '/home/pi/Music'
patience_time_in_seconds = 10
event_sound_enabled = True
some_motherfucker_is_sitting_there = False
ass_sensor_pin = 7
language = 'hu'
tts = pyttsx3.init()
sound_lock = asyncio.Lock()

def say(line):
    tts.say(line)
    tts.runAndWait()


async def play_dir(dir):
    files = [ f for f in os.listdir(dir) if f.endswith('.mp3') ]
    if len(files) > 0:
        print ('Playing: '+os.path.join(dir,random.choice(files)))
        await sound_lock.acquire()
        try:
            play(os.path.join(dir,random.choice(files)))
        finally:
            sound_lock.release()
    else:
        print ('No files have been found!')

async def play(file):
    await sound_lock.acquire()
    try:
        if not mixer.music.get_busy():
            try:
                print ('Playing: '+file)
                mixer.music.load(file)
                mixer.music.play()
            except:
                print ('Cannot play: '+file)
    finally:
        sound_lock.release()


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
        exit()

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
                    say('Húzz már el innen a faszomba mert szétbaszlak')
        
        prev = inputValue
        time.sleep(0.3)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ass_sensor_pin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
#    espeak.set_voice("hu")
    tts.setProperty('voice', 'hungarian')
    mixer.pre_init(devicename="Audio Device Analog Stereo")
    mixer.init()
    shell = Shell()
    try:
        _thread.start_new_thread(event_loop,(shell,))
    except:
        print('Cannot start event loop.')
        traceback.print_exc()

    shell.cmdloop()
