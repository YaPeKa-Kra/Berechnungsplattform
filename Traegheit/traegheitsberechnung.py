import math
import matplotlib.pyplot as plt


class AchsenTraegheit:
    def __init__(self, la, rw, rm, rdm, mw, mm, dmm, ma, w):
        self.la = la          # Axle length
        self.rw = rw          # Wheel distance
        self.rm = rm          # Hub motor distance
        self.rdm = rdm        # Diff motor distance
        self.mw = mw          # Wheel mass
        self.mm = mm          # Hub motor mass
        self.dmm = dmm        # Diff motor mass
        self.ma = ma          # Axle mass
        self.w = w            # winkelbeschleunigung 

    def berechne_traegheitsmoment_rad(self):
        """Berechnet das Trägheitsmoment der Räder."""
        traegheit_rad = self.mw * 2 * (self.rw/2)**2
        #print(f"Trägheit Rad: {traegheit_rad} kg*m^2")
        return traegheit_rad

    def berechne_traegheitsmoment_nabenmotor(self):
        """Berechnet das Trägheitsmoment der Nabenmotoren."""
        traegheit_nabenmotor = self.mm * 2 * (self.rm/2)**2
        #print(f"Trägheit Nabenmotor: {traegheit_nabenmotor} kg*m^2")
        return traegheit_nabenmotor

    def berechne_traegheitsmoment_diffmotor(self):
        """Berechnet das Trägheitsmoment des Differenzialmotors."""
        traegheit_diffmotor = self.dmm*(self.rdm)**2
        #print(f"Trägheit DiffMotor: {traegheit_diffmotor} kg*m^2")
        return traegheit_diffmotor

    def berechne_traegheitsmoment_achse(self):
        """Berechnet das Trägheitsmoment der Achse."""
        traegheit_achse = (1/12)*self.ma*(self.la)**2
        #print(f"Trägheit Achse: {traegheit_achse} kg*m^2")
        return traegheit_achse

    def berechne_ges_traegheit(self):
        """Berechnet das Trägheitsmoment der Gesamtmasse."""
        gesamt_traegheit = self.berechne_traegheitsmoment_rad() + self.berechne_traegheitsmoment_nabenmotor() + self.berechne_traegheitsmoment_diffmotor() + self.berechne_traegheitsmoment_achse()
        #print(f"Gesamtträgheit: {gesamt_traegheit} kg*m^2")
        return gesamt_traegheit

    def berechne_traegheitsmoment(self):
        traegheitsmoment = self.w * self.berechne_ges_traegheit()
        #print(f"Trägheitsmoment: {traegheitsmoment} Nm")
        return traegheitsmoment
    
    def all_results(self):
        traegheit_rad = self.berechne_traegheitsmoment_rad()
        traegheit_nabenmotor = self.berechne_traegheitsmoment_nabenmotor()
        traegheit_diffmotor = self.berechne_traegheitsmoment_diffmotor()
        traegheit_achse = self.berechne_traegheitsmoment_achse()
        traegheit_gesamt = self.berechne_ges_traegheit()
        res_traegheitsmoment = self.berechne_traegheitsmoment()

        print(f"Trägheit der Räder: {traegheit_rad} kg*m^2")
        print(f"Trägheit der Nabenmotoren: {traegheit_nabenmotor} kg*m^2")
        print(f"Trägheit des Differenzialmotors: {traegheit_diffmotor} kg*m^2")
        print(f"Trägheit der Achse: {traegheit_achse} kg*m^2")
        print(f"Trägheit Gesamt: {traegheit_gesamt} kg*m^2")
        print(f"Trägheitsmoment: {res_traegheitsmoment} Nm")

        ergebnis_text = (f"Trägheit der Räder: {traegheit_rad} kg*m^2\n"
        f"Trägheit der Nabenmotoren: {traegheit_nabenmotor} kg*m^2\n"
        f"Trägheit des Differenzialmotors: {traegheit_diffmotor} kg*m^2\n"
        f"Trägheit der Achse: {traegheit_achse} kg*m^2\n"
        f"Trägheit Gesamt: {traegheit_gesamt} kg*m^2\n"
        f"Trägheitsmoment: {res_traegheitsmoment} Nm\n"
        )
        return ergebnis_text

# user input
# Testeingabe
#la = 1.8    # [m]
#rw = 1.8    # [m]
#rm = 1.6    # [m]
#rdm = 0.5   # [m]
#mw = 350    # [kg]
#mm = 200    # [kg]
#dmm = 200   # [kg]
#ma = 500    # [kg]
#w = 0.14    # [rad/s^2]

#achse_C180 = AchsenTraegheit(la, rw, rm, rdm, mw, mm, dmm, ma, w).all_results()
#achse = AchsenTraegheit(la, rw, rm, rdm, mw, mm, dmm, ma, w)
#gesamt_traegheit = achse.berechne_ges_traegheit()
#traegheitsmoment = achse.berechne_traegheitsmoment()



