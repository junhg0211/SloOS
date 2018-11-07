import winsound

def playsound(filedir):
    winsound.PlaySound(filedir, winsound.SND_ASYNC)

def playsound_delay(filedir):
    winsound.PlaySound(filedir, winsound.SND_FILENAME)