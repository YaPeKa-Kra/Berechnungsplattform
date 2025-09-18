import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import matplotlib.transforms as transforms
import numpy as np

# Wände definieren (bei x=0 und x=10)
left_wall = 0
right_wall = 1.6

# Fahrzeugzustand
x = 0.8   # Startposition mittig
y = 0.0   # Vorwärtsbewegung
vx = 0.0
vy = 0.5  # konstante Vorwärtsgeschwindigkeit

# Fahrzeug (ASV)
car_width = 1.2
car_length = 12
car_angle = 5

#Sensoren
sensor_vl = (((-car_length/2)+1480),-car_width/2)
sensor_hl = (((car_length/2)-1480),-car_width/2)
sensor_vr = (((car_length/2)-1480),car_width/2)
sensor_hr = ((()))
sensors = [sensor_vl, sensor_hl, sensor_vr]

positions = []

def update(frame):
    global x, y, vx, vy

    # Sensoren messen Abstand zu den Wänden
    dist_left = x - left_wall
    dist_right = right_wall - x

    # Regelung: wenn Abstand < 1.0 → nach innen lenken
    if dist_left < 0.8:
        vx = 0.05   # leicht nach rechts
    elif dist_right < 0.8:
        vx = -0.05  # leicht nach links
    else:
        vx = 0.0

    # Bewegung updaten
    x += vx
    y += vy
    positions.append((x, y))

    # Plot zurücksetzen
    ax.clear()
    ax.set_xlim(-1, 50)
    ax.set_ylim(0, 50)

    # Wände zeichnen
    ax.plot([left_wall, left_wall], [0, 50], "k--")
    ax.plot([right_wall, right_wall], [0, 50], "k--")

    # Fahrzeug zeichnen
    #altes fahrzeug punkt 
    # x.plot(x, y, "ro")
    car_center = (x, y - car_length/2)
    t = transforms.Affine2D().rotate_deg_around(car_center[0], car_center[1], car_angle) + ax.transData
    car = patches.Rectangle(
        (x - car_width/2, y - car_length),
        car_width,
        car_length,
        linewidth=1,
        edgecolor="b",
        facecolor="b",
        #transform=t
    )
    ax.add_patch(car)

fig, ax = plt.subplots(figsize=(10, 10))  # Fenstergröße anpassen (Breite, Höhe)
ax.set_aspect('equal')  # <-- Seitenverhältnis gleichsetzen
ani = animation.FuncAnimation(fig, update, frames=300, interval=50)
plt.show()