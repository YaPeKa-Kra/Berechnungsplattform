import math
import matplotlib.pyplot as plt
import numpy as np

# Beispielanwendung mit Streckfaktor für Seite c
# B = [600, 0] #Hebelarm
# Winkel = [25] #auslenkung gewünscht in grad

def berechne_zylhub_mitte(hebel, winkel):
    winkel_rad = winkel*math.pi/180
    tangens_winkel = math.tan(winkel_rad)
    zylhub_halbe = hebel * tangens_winkel
    print(tangens_winkel)
    print(zylhub_halbe)
    return zylhub_halbe

berechne_zylhub_mitte(450, 25)



