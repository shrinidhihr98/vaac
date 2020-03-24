from subprocess import Popen, PIPE
import subprocess
import csv
import json
import argparse
import time

### The _GetchUnix function replicates the functionality of the getch() method.

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

getch = _GetchUnix()

desc = '''
This program prompts a command and records it in a file.
Read the prompted command vocally into the microphone.
Press j to start recording.
Press k to stop recording.
Press l to store recording.
Press ; to re-record without storing.
Press e or any other key to exit.
INFO: Verify your recordings as often as possible.
"WARNING: Before stopping recording, wait for a moment, in order to account for delay from the microphone.
'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("--count", default=10,type=int, help="Takes number of repetitions of each sentence in corpus to be prompted.")
parser.add_argument("--corpus",required=True,type=str, help="Takes path to corpus file.")
parser.add_argument("--modeldir",required=True,type=str, help="Takes path to model directory.")

args = parser.parse_args()
count = args.count
corpus_file_string = args.corpus
model_dir_string = args.modeldir
corpus_file = open(corpus_file_string)
corpus = list(csv.reader(corpus_file))

with open(model_dir_string+"recording_progress.json",'r') as recording_data_file:
    recording_data = json.load(recording_data_file)
    i = recording_data["i"]
    n = recording_data["n"]

def printStatus():
    if n < len(corpus):
        print("Read "+str(i+1)+" of "+str(count)+":\n\t", corpus[n][0])

print(desc)
print("___________________________________")
print("Length of corpus:",len(corpus))
print("Progress:")
print("Number of corpus words done:",n)
printStatus()
print("Press j to start recording.",end="",flush=True)

while n < len(corpus):
    ch = getch()
    if ch == "j":
        # Recording
        print("\rRecording... Press k to stop recording.",end="")
        
        p = Popen(['exec arecord -f S16_LE -r 16000 /tmp/test.wav'],stdin=PIPE, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,shell=True)
        previous = ch
    elif ch == "k" and previous == "j":        
        # stop recording
        print("\rRecorded. Press l to save, ; otherwise.",end="")                        
        p.kill()            
        previous = ch
    elif ch == "l" and previous == "k":
        # save
        print("Saving...")
        fname = model_dir_string+"recordings/recording"+str(n)+"_"+str(i)
        subprocess.run(['mv','/tmp/test.wav',fname+".wav"])
        
        i += 1
        if i == count:
            i = 0
            n += 1        
                
        if n == len(corpus) and i == 0:
            print("Hurray! You finished recording a complete set with "+str(count)+" repetitions.")
            print()
            recording_data["i"] = i
            recording_data["n"] = n
            with open(model_dir_string+"recording_progress.json",'w') as recording_data_file:
                json.dump(recording_data,recording_data_file)
        
            corpus_file.close()
            recording_data_file.close()
            break
        printStatus()
        print("\rPress j to start recording.",end="")
        previous = ch

    elif ch == ";" and previous == "k":        
        print()
        printStatus()
        print("\rPress j to start recording.",end="")   
    else:
        print()
        recording_data["i"] = i
        recording_data["n"] = n
        with open(model_dir_string+"recording_progress.json",'w') as recording_data_file:
            json.dump(recording_data,recording_data_file)
        
        corpus_file.close()
        recording_data_file.close()
        break     