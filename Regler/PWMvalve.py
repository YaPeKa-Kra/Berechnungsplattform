import numpy as np
import matplotlib.pyplot as plt

# --- 1. Parameter definieren ---
# Systemparameter (Ventil)
TAU = 0.2     # Zeitkonstante Tau [s] (Trägheit/Ansprechzeit)
K_GAIN = 1.0  # Übertragungsfaktor (Gain)

# PWM- und SPS-Parameter
V_MAX = 24.0   # Maximale Spannung [V]
F_PWM = 100.0  # PWM-Frequenz [Hz]
T_PWM = 1.0 / F_PWM # PWM-Periodendauer [s]

# SPS-Steuerung (wechselnder Duty Cycle)
# ACHTUNG: Der Duty Cycle ist hier in % (0-100)
sps_duty_cycle_werte = np.array([0, 20, 50, 80, 100, 50, 0])
sps_schaltzeiten = np.array([0, 1, 3, 4, 6, 8, 10]) # Zeitpunkte für Duty Cycle Wechsel [s]

# Simulationsparameter
T_MAX = sps_schaltzeiten[-1] + 2 # Gesamte Simulationszeit [s]
DT = 0.0001                      # Sehr kleiner Zeitschritt [s] für hohe Auflösung des Pulses
N_STEPS = int(T_MAX / DT)
time = np.linspace(0, T_MAX, N_STEPS)

# --- 2. Initialisierung ---
y = np.zeros(N_STEPS)     # Ventil-Stellung / Durchfluss (Ausgang)
u_pwm = np.zeros(N_STEPS) # Diskretes PWM-Signal (Eingang)
y[0] = 0.0

# --- 3. Generierung des PWM-Signals und numerische Lösung ---
duty_cycle_index = 0
for i in range(N_STEPS - 1):
    t = time[i]
    
    # Bestimme aktuellen Duty Cycle (basierend auf SPS-Programm)
    if duty_cycle_index < len(sps_schaltzeiten) - 1 and t >= sps_schaltzeiten[duty_cycle_index + 1]:
        duty_cycle_index += 1
        
    duty_cycle_percent = sps_duty_cycle_werte[duty_cycle_index]
    D = duty_cycle_percent / 100.0 # Duty Cycle (0 bis 1)

    # a) Generierung des diskreten PWM-Pulses (U_PWM)
    # Die Zeit innerhalb der aktuellen PWM-Periode
    t_cycle = t % T_PWM 
    
    # Der Puls ist AN (V_MAX), wenn die Zykluszeit kleiner ist als die AN-Zeit (D * T_PWM)
    if t_cycle < D * T_PWM:
        u_pwm[i] = V_MAX
    else:
        u_pwm[i] = 0.0
    
    # b) Effektive Spannung (U_eff) für die PT1-Gleichung
    # Das PT1-Glied "filtert" den PWM-Puls intern,
    # es reagiert auf den momentanen Wert U_PWM[i]
    U_eff_momentan = u_pwm[i] 
    
    # c) Numerische Lösung (Euler-Verfahren)
    # Die PT1-Gleichung wird mit dem momentanen Pulswert U_eff_momentan befeuert
    dy_dt = (K_GAIN * U_eff_momentan - y[i]) / TAU
    
    # Neuen Wert berechnen
    y[i+1] = y[i] + DT * dy_dt

# --- 4. Darstellung der Ergebnisse ---
plt.figure(figsize=(12, 8))

# Plot 1: Diskreter PWM-Puls (mit Zoom für bessere Sichtbarkeit)
plt.subplot(3, 1, 1)
plt.plot(time, u_pwm, label='PWM-Puls ($U_{PWM}$)', color='tab:blue')
plt.title(f'Diskreter PWM-Puls (F={F_PWM} Hz)')
plt.ylabel('Spannung [V]')
plt.grid(True, axis='y')
plt.xlim(0.8, 1.2) # Zoom auf den ersten Duty Cycle Wechsel
plt.legend(loc='upper right')

# Plot 2: Ventilstellung (langsame Reaktion)
plt.subplot(3, 1, 2)
plt.plot(time, y, label='Ventilstellung (simuliert, PT1)', color='tab:red')
plt.ylabel('Ventilstellung [normiert]')
plt.grid(True)
plt.legend(loc='upper right')

# Plot 3: Ventilstellung mit Detail-Zoom
plt.subplot(3, 1, 3)
plt.plot(time, y, label='Ventilstellung (simuliert, PT1)', color='tab:red')
plt.xlabel('Zeit [s]')
plt.ylabel('Ventilstellung [normiert]')
plt.grid(True)
plt.xlim(0, T_MAX) # Volle Zeitachse
plt.ylim(-0.05, 1.05)
plt.legend(loc='upper right')

plt.tight_layout()
plt.show()

print(f"Simulation beendet. Trägheit (TAU): {TAU} s. PWM-Frequenz: {F_PWM} Hz. Simulations-DT: {DT} s.")