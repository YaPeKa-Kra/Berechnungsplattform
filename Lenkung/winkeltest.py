import numpy as np
import matplotlib.pyplot as plt

""" 20240514: unfertige Variante V1, geplante Änderungen:
    - statt Streckfaktor soll Drehwinkel vom User eingegeben werden
    - resultierend aus dieser Winkeländerung soll der Zylinderhub bestimmt werden können"""

# Eingabe
r = 500
ax = a_x
ay = a_y
phi = 0

    # Ausgangslänge des Zylinders
l0 = np.sqrt((r - ax)**2 + ay**2)

    # Neue Länge des Zylinders
l1 = l0 * streckfaktor

    # Betrag des Vektors AC
la = np.sqrt(ax**2 + ay**2)

cos_theta_minus_phi = (r**2 + la**2 - l1**2) / (2 * r * la)
# cos satz


theta_minus_phi1 = np.arccos(cos_theta_minus_phi)