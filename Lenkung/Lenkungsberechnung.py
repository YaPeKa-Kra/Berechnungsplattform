import numpy as np
import matplotlib.pyplot as plt

def Zylinder_Bewegung(hebelarm, a_x, a_y, streckfaktor):
    """
    Berechnet die Winkeländerung und den neuen Punkt B' und visualisiert die Bewegung skaliert,
    mit der Legende außerhalb des linken Plots.

    Args:
        hebelarm (float): Länge des Hebelarms (Radius CB).
        a_x (float): x-Koordinate des Fixpunkts A.
        a_y (float): y-Koordinate des Fixpunkts A.
        streckfaktor (float): Faktor, um den sich der Zylinder relativ zu seiner Ausgangslänge ändert.

    Returns:
        tuple: Ein Tupel mit dem neuen Winkel (in Grad) und den Koordinaten des neuen Punkts B' als NumPy-Array.
               Gibt None zurück, wenn keine realen Lösungen existieren.
    """
    r = hebelarm
    ax = a_x
    ay = a_y

    # Ausgangslänge des Zylinders
    l0 = np.sqrt((r - ax)**2 + ay**2)

    # Neue Länge des Zylinders
    l1 = l0 * streckfaktor

    # Betrag des Vektors AC
    la = np.sqrt(ax**2 + ay**2)

    # Berechnung des Kosinus des Winkels theta - phi
    cos_theta_minus_phi = (r**2 + la**2 - l1**2) / (2 * r * la)

    if cos_theta_minus_phi > 1 or cos_theta_minus_phi < -1:
        print("Keine Lösungen für den Winkel mit diesem Streckfaktor.")
        return None

    theta_minus_phi1 = np.arccos(cos_theta_minus_phi)
    theta_minus_phi2 = -theta_minus_phi1

    phi = np.arctan2(ay, ax)

    theta1 = phi + theta_minus_phi1
    theta2 = phi + theta_minus_phi2

    if abs(theta1) < abs(theta2):
        theta_neu_rad = theta1
    else:
        theta_neu_rad = theta2

    theta_neu_grad = np.degrees(theta_neu_rad)
    b_neu = np.array([r * np.cos(theta_neu_rad), r * np.sin(theta_neu_rad)])
    b_alt = np.array([r, 0])
    c_punkt = np.array([0, 0])
    a_punkt = np.array([ax, ay])

    # Visualisierung
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))  # Platz für die Legende
    fig.suptitle("Bewegung des Lenkzylinders")

    # --- Linker Plot: Gesamte Anordnung MIT sichtbarem Kreis um C ---
    ax1.axhline(0, color='black', linewidth=0.5)
    ax1.axvline(0, color='black', linewidth=0.5)
    ax1.grid(True)
    ax1.set_xlabel("x-Koordinate")
    ax1.set_ylabel("y-Koordinate")
    ax1.set_title("Geometrische Anordnung mit sichtbarem Radius")
    ax1.set_aspect('equal', adjustable='box')

    # Kreis um C hinzufügen
    kreis_gesamt = plt.Circle(c_punkt, r, fill=False, color='gray', linestyle=':')
    ax1.add_patch(kreis_gesamt)

    # Ausgangszustand
    line_cb_alt, = ax1.plot(*zip(c_punkt, b_alt), marker='o', linestyle='-', label='CB (Ausgang)')
    line_ab_alt, = ax1.plot(*zip(a_punkt, b_alt), marker='o', linestyle='--', label=f'AB (Länge: {np.sqrt((r - ax)**2 + ay**2):.2f})')
    scatter_c = ax1.scatter(*c_punkt, color='black', label='Drehpunkt C')
    scatter_a = ax1.scatter(*a_punkt, color='red', label='Fixpunkt A')
    scatter_b_alt = ax1.scatter(*b_alt, color='blue', label='Punkt B (Ausgang)')

    # Neuer Zustand
    line_cb_neu, = ax1.plot(*zip(c_punkt, b_neu), marker='o', linestyle='-', color='green', label='CB\' (Neu)')
    line_ab_neu, = ax1.plot(*zip(a_punkt, b_neu), marker='o', linestyle='--', color='purple', label=f'AB\' (Länge: {np.linalg.norm(b_neu - a_punkt):.2f})')
    scatter_b_neu = ax1.scatter(*b_neu, color='lime', label='Punkt B\' (Neu)')

    # Legende außerhalb des Plots platzieren
    ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

    # Skalierung des linken Plots so anpassen, dass der Kreis immer sichtbar ist
    min_grenze = min(-r - 1, ax - 1, b_neu[0] - 1)
    max_grenze = max(r + 1, ax + 1, b_neu[0] + 1)

    min_y_grenze = min(-r - 1, ay - 1, b_neu[1] - 1)
    max_y_grenze = max(r + 1, ay + 1, b_neu[1] + 1)

    ax1.set_xlim(min_grenze, max_grenze)
    ax1.set_ylim(min_y_grenze, max_y_grenze)

    # --- Rechter Plot: Visualisierung am Kreis um C ---
    ax2.axhline(0, color='black', linewidth=0.5)
    ax2.axvline(0, color='black', linewidth=0.5)
    ax2.grid(True)
    ax2.set_xlim(-r - 1, r + 1)
    ax2.set_ylim(-r - 1, r + 1)
    ax2.set_xlabel("x-Koordinate")
    ax2.set_ylabel("y-Koordinate")
    ax2.set_title("Bewegung auf dem Kreis um C")
    ax2.set_aspect('equal', adjustable='box')

    # Kreis um C
    kreis_detail = plt.Circle(c_punkt, r, fill=False, color='gray', linestyle=':')
    ax2.add_patch(kreis_detail)
    ax2.scatter(*c_punkt, color='black', label='Drehpunkt C')

    # Ausgangspunkt B
    ax2.scatter(*b_alt, color='blue', label='Punkt B (Ausgang)')
    ax2.arrow(c_punkt[0], c_punkt[1], b_alt[0] - c_punkt[0], b_alt[1] - c_punkt[1],
              head_width=0.2, head_length=0.3, fc='blue', ec='blue', label='Ausgangsvektor CB')

    # Neuer Punkt B'
    ax2.scatter(*b_neu, color='lime', label='Punkt B\' (Neu)')
    ax2.arrow(c_punkt[0], c_punkt[1], b_neu[0] - c_punkt[0], b_neu[1] - c_punkt[1],
              head_width=0.2, head_length=0.3, fc='lime', ec='lime', label='Neuer Vektor CB\'')

    # Winkeländerung visualisieren
    from matplotlib.patches import Arc
    winkel_start = 0
    winkel_ende = np.degrees(theta_neu_rad)
    bogen = Arc(c_punkt, 2*0.8*r, 2*0.8*r, theta1=winkel_start, theta2=winkel_ende, color='red', linewidth=2, label='Winkeländerung')
    ax2.add_patch(bogen)

    # Text für die Winkeländerung
    ax2.text(0.5*r * np.cos(theta_neu_rad/2), 0.5*r * np.sin(theta_neu_rad/2), f'{winkel_ende:.2f}°',
             horizontalalignment='center', verticalalignment='center', fontsize=10, color='red')

    ax2.legend()

    plt.tight_layout()
    plt.show()

    return theta_neu_grad, b_neu

if __name__ == "__main__":
    # Parameter der Anordnung
    hebel = 150.0  # Hebelarm (Radius CB)
    a_x_koordinate = 50.0  # x-Koordinate des Fixpunkts A
    a_y_koordinate = -100.0 # y-Koordinate des Fixpunkts A

    # Streckfaktor eingeben
    try:
        streckfaktor = float(input("Gib den Streckfaktor des Hydraulikzylinders ein (z.B. 1.2 für 20% Ausfahren, 0.8 für 20% Einfahren): "))
    except ValueError:
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        exit()

    ergebnis = Zylinder_Bewegung(hebel, a_x_koordinate, a_y_koordinate, streckfaktor)

    if ergebnis:
        winkel_aenderung_grad, b_neu_punkt = ergebnis
        print(f"\nNeuer Winkel von B': {winkel_aenderung_grad:.2f} Grad")
        print(f"Koordinaten des neuen Punkts B': [{b_neu_punkt[0]:.2f}, {b_neu_punkt[1]:.2f}]")