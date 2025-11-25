import numpy as np
import matplotlib.pyplot as plt

# --- 1. Konstanten und Parameter ---
# Physikalische Konstanten (aus Beispiel)
R_RAD = 0.375    # m (Radradius)
K_M_P = 3.75   # Nm/bar (Momenten-Druck-Faktor K)
M_ZIEL = 400  # Nm (Ziel-Bremsmoment)
P_ZIEL = M_ZIEL / K_M_P # 2.34 bar (Ziel-Druck)

# Rampen- und Simulationsparameter
T_RAMP = 1.0   # s (Dauer der Rampe)
DT = 0.01      # s (SPS-Zykluszeit)
T_MAX = 5.0    # s (Simulationsdauer)
SCHRITTE = int(T_MAX / DT)

# PID-Parameter (Abgestimmt für das Simulationsmodell)
KP = 1.8  
KI = 0.5  
KD = 0.01 

# Systemträgheit (vereinfachtes PT1-Modell)
TAO_SYSTEM = 0.05 # s

# --- 2. Rampen- und Hilfsfunktionen ---

def get_soll_druck(t):
    """Berechnet den rampenförmigen Solldruck P_erf(t)."""
    rampe_wert = (P_ZIEL / T_RAMP) * t
    return min(P_ZIEL, rampe_wert)

def druck_zu_moment(p):
    """M_B = p * K"""
    return p * K_M_P

def moment_zu_kraft(m):
    """F_B = M_B / r"""
    return m / R_RAD

# --- 3. PID-Klasse ---

class PIDController:
    def __init__(self, kp, ki, kd, dt):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd
        self.dt = dt
        self.integral = 0
        self.last_error = 0

    def compute(self, soll, ist):
        """Berechnet die Stellgröße u(t) für das Ventil."""
        error = soll - ist
        
        p_term = self.Kp * error
        
        # Integral-Anteil mit einfacher Begrenzung (kein echtes Anti-Windup)
        self.integral += error * self.dt
        i_term = self.Ki * self.integral
        
        derivative = (error - self.last_error) / self.dt
        d_term = self.Kd * derivative
        self.last_error = error
        
        output = p_term + i_term + d_term
        
        # Begrenzung des Outputs (Ventil-Strom)
        return np.clip(output, 0, 10) 

# --- 4. System-Simulation (Hydraulikmodell) ---

def simulate_hydraulics(u_ventil, p_ist_alt, dt, tao):
    """Simuliert, wie schnell der Druck P_Ist dem Ventilsignal folgt (PT1-Glied)."""
    p_max_durch_u = u_ventil / 10 * P_ZIEL 
    p_ist_neu = p_ist_alt + (dt / tao) * (p_max_durch_u - p_ist_alt)
    return max(0, p_ist_neu)

# --- 5. Simulationsschleife ---

pid = PIDController(KP, KI, KD, DT)
zeit_arr = []
p_soll_arr = []
p_ist_arr = []
f_b_soll_arr = []
m_b_soll_arr = []
u_ventil_arr = []

p_ist = 0.0 # Start mit 0 bar

for i in range(SCHRITTE):
    t = i * DT
    
    # A. Sollwert holen (Die Rampe!)
    p_soll = get_soll_druck(t)
    
    # B. Berechnung der zugehörigen Sollgrößen (für Plots 1 & 2)
    m_soll = druck_zu_moment(p_soll)
    f_soll = moment_zu_kraft(m_soll)
    
    # C. PID-Regler berechnen (Stellgröße u(t))
    u_ventil = pid.compute(p_soll, p_ist)
    
    # D. System simulieren (P_Ist des nächsten Zyklus)
    p_ist = simulate_hydraulics(u_ventil, p_ist, DT, TAO_SYSTEM)
    
    # E. Daten speichern
    zeit_arr.append(t)
    p_soll_arr.append(p_soll)
    p_ist_arr.append(p_ist)
    f_b_soll_arr.append(f_soll)
    m_b_soll_arr.append(m_soll)
    u_ventil_arr.append(u_ventil)


# --- 6. Visualisierung der 3 Plots ---

fig, axes = plt.subplots(3, 1, figsize=(10, 10))
plt.suptitle('Rampengesteuerte Bremsregelung (PID-Simulation)', fontsize=14)

# Plot 1: Bremskraft (F_B) Rampe über Zeit
axes[0].plot(zeit_arr, f_b_soll_arr, label='F_B Soll (Rampe)', color='darkblue')
axes[0].axvline(T_RAMP, color='gray', linestyle=':', label='Ende der Rampe')
axes[0].set_title('Plot 1: Bremskraft-Sollwert-Rampe über Zeit')
axes[0].set_ylabel('Bremskraft $F_B$ (N)')
axes[0].grid(True)
axes[0].legend()

# Plot 2: Bremsmoment (M_B) über Druck (P_Soll)
# Wir plotten P_Soll gegen M_B_Soll. Diese Beziehung ist linear (M_B = P * K).
axes[1].plot(p_soll_arr, m_b_soll_arr, label=f'$M_B = P \cdot {K_M_P}$', color='purple')
axes[1].set_title('Plot 2: Bremsmoment über Solldruck (Lineare Kennlinie)')
axes[1].set_xlabel('Solldruck $P_{Soll}$ (bar)')
axes[1].set_ylabel('Bremsmoment $M_B$ (Nm)')
axes[1].grid(True)
axes[1].legend()

# Plot 3: Reglerkurve (Soll-/Ist-Druck über Zeit)
axes[2].plot(zeit_arr, p_soll_arr, label='P_Soll (Rampe)', linestyle='--', color='blue')
axes[2].plot(zeit_arr, p_ist_arr, label='P_Ist (Gemessen)', color='red')
axes[2].axvline(T_RAMP, color='gray', linestyle=':')
axes[2].set_title('Plot 3: PID-Regelung des Drucks')
axes[2].set_xlabel('Zeit (s)')
axes[2].set_ylabel('Druck (bar)')
axes[2].grid(True)
axes[2].legend()

plt.tight_layout(rect=[0, 0, 1, 0.96]) # Abstand für Suptitel
plt.show()