import pandas as pd
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class FahrzeugParameter:
    def __init__(self):
        self.g = 9.81
        self.Masse_leer = float(input("Masse leer eingeben in kg: "))
        self.Masse_Cab_Src = float(input("Masse Kabine und SRC eingeben in kg: "))
        self.Masse_Nutzlast = float(input("Masse Nutzlast eingeben in kg: "))
        self.Anzahl_Raeder = float(input("Anzahl Räder eingeben: "))
        self.Raddurchmesser = float(input("Raddurchmesser eingeben in m: "))
        self.Reibungskoeffizent_urr = float(input("Reibungskoeffizient der Unterlage eingeben: "))
        self.Anzahl_Antrieb_n = float(input("Anzahl Antriebe eingeben: "))
        self.Batterie_Kapazitaet = float(input("Batteriekapazität eingeben in kWh: "))
        self.Batterie_Ladestatus_Start = float(input("Batterieladestatus eingeben in %: "))
        self.Max_Ladeleistung_P = float(input("Maximale Ladeleistung eingeben in kW: "))
        self.Wirkungsgrad_Elektrisch = float(input("Wirkungsgrad elektrisch eingeben in %: "))
        self.Wirkungsgrad_Antrieb = float(input("Wirkungsgrad Antrieb eingeben in %: "))
        self.Bremsverzoegerung = float(input("Bremsverzögerung eingeben in m/s^2: "))
        self.Sicherheitsfaktor = float(input("Sicherheitsfaktor eingeben: "))
        self.Getriebe_uebersetzung = float(input("Getriebeübersetzung eingeben: "))
        self.Beschleunigung_a = float(input("Beschleunigung eingeben in m/s^2: "))

        self.Anzahl_Sektoren = int(input("Anzahl Sektoren eingeben: "))
        while True:
            try:
                if self.Anzahl_Sektoren <= 0:
                    raise ValueError("Anzahl Sektoren muss größer als 0 sein.")
                break
            except ValueError as e:
                print(e)
                self.Anzahl_Sektoren = int(input("Bitte erneut eingeben: "))

        self.sektor_parameter = []
        for i in range(self.Anzahl_Sektoren):
            Sektor_Laenge = float(input(f"Länge des Sektors {i+1} in m: "))
            Sektor_Gefälle = float(input(f"Gefälle des Sektors {i+1} in %: "))
            Sektor_Geschwindigkeit = float(input(f"Fahrgeschwindigkeit im Sektors {i+1}: "))
            self.sektor_parameter.append({"Laenge": Sektor_Laenge, "Gefälle": Sektor_Gefälle, "Geschwindigkeit": Sektor_Geschwindigkeit}) 

        # Berechnung aus den Eingaben
        self.Gesamtmasse = self.Masse_leer + self.Masse_Cab_Src + self.Masse_Nutzlast
        self.Gewichtskraft = self.Gesamtmasse * self.g
        self.Batterie_Kapazitaet_Start_kWh = self.Batterie_Kapazitaet * self.Batterie_Ladestatus_Start / 100

        print("Gesamtmasse: ", self.Gesamtmasse, "kg")
        print("Gewichtskraft: ", self.Gewichtskraft, "N")
        print("Batteriekapazität Start: ", self.Batterie_Kapazitaet_Start_kWh, "kWh")


#  ... (vorheriger Code)

class FahrzeugBerechnungen:
    def __init__(self, fahrzeug_parameter):
        """
        Initialisiert die Berechnungsklasse mit einem Objekt der Klasse FahrzeugParameter.
        """
        self.parameter = fahrzeug_parameter
        self.df = pd.DataFrame()  # Initialisiert einen leeren DataFrame
        self.sektor_index = 0
        self.laenge_kumuliert = 0
        self.hoehe_absolut = 0

    def berechne_sektor_daten(self):
        """
        Führt die Berechnungen für jeden Sektor durch und speichert die Ergebnisse im DataFrame.
        """
        # Initialisiert Listen für die DataFrame-Daten
        laengen = []
        gefaelle = []
        #reibungen = []
        normalkraefte = []
        rollwiderstaende = []
        steigungswiderstaende = []
        gesamtwiderstaende_konstant = []
        gesamtwiderstaende_konstant_pro_rad = []
        kraefte_konstant = []
        leistungen_pro_rad = []
        leistungen_pro_motor = []
        drehmomente = []
        drehzahlen_rad = []
        drehmomente_motor = []
        drehzahlen_motor = []
        beschleunigungswiderstaende = []
        gesamtwiderstaende_beschleunigung = []
        kraefte_beschleunigung = []
        beschleunigungsleistungen_pro_rad = []
        beschleunigungsleistungen_pro_motor = []
        beschleunigungsdrehmomente_pro_rad = []
        drehzahlen_rad_beschleunigung = []
        drehmomente_motor_beschleunigung = []
        drehzahlen_motor_beschleunigung = []
        laengen_kumuliert = []
        hoehendifferenzen = []
        hoehen_absolut = []
        dauer_bewegungen = []
        beschleunigungen_zwischen_sektoren = []
        vorherige_geschwindigkeit = 0
        sektor_geschwindigkeiten = [] # Für die Speicherung der Geschwindigkeiten

        for i, sektor in enumerate(self.parameter.sektor_parameter):
            laenge = sektor["Laenge"]
            steigung = sektor["Gefälle"]
            #reibung = sektor["Reibung"]
            geschwindigkeit = self.berechne_sektor_geschwindigkeit(i)
            sektor_geschwindigkeiten.append(geschwindigkeit) # Speichere die Geschwindigkeit

            normalkraft = self.berechne_normalkraft(steigung)
            rollwiderstand_pro_rad = self.berechne_rollwiderstand_pro_rad(normalkraft)
            steigungswiderstand_pro_rad = self.berechne_steigungswiderstand_pro_rad(steigung)
            gesamtwiderstand_konstant_pro_rad = self.berechne_gesamtwiderstand_konstant_pro_rad(rollwiderstand_pro_rad, steigungswiderstand_pro_rad)
            kraft_konstant_pro_rad = self.berechne_kraft_konstant_pro_rad(gesamtwiderstand_konstant_pro_rad)
            leistung_pro_rad = self.berechne_leistung_pro_rad(kraft_konstant_pro_rad, geschwindigkeit) # Verwende die Sektorgeschwindigkeit
            leistung_pro_motor = self.berechne_leistung_pro_motor(leistung_pro_rad)
            drehmoment = self.berechne_drehmoment(kraft_konstant_pro_rad)
            drehzahl_rad = self.berechne_drehzahl_rad(geschwindigkeit) # Verwende die Sektorgeschwindigkeit
            drehmoment_motor = self.berechne_drehmoment_motor(drehmoment)
            drehzahl_motor = self.berechne_drehzahl_motor(drehzahl_rad)
            beschleunigungswiderstand_pro_rad_beschleunigung = self.berechne_beschleunigungswiderstand_pro_rad(bremsen=False)
            gesamtwiderstand_beschleunigung_pro_rad = self.berechne_gesamtwiderstand_beschleunigung_pro_rad(gesamtwiderstand_konstant_pro_rad, beschleunigungswiderstand_pro_rad_beschleunigung)
            kraft_beschleunigung_pro_rad = self.berechne_kraft_beschleunigung_pro_rad(gesamtwiderstand_beschleunigung_pro_rad)
            beschleunigungsleistung_pro_rad = self.berechne_beschleunigungsleistung_pro_rad(kraft_beschleunigung_pro_rad, geschwindigkeit) # Verwende Sektorgeschwindigkeit
            beschleunigungsleistung_pro_motor = self.berechne_beschleunigungsleistung_pro_motor(beschleunigungsleistung_pro_rad)
            beschleunigungsdrehmoment_pro_rad = self.berechne_beschleunigungsdrehmoment_pro_rad(kraft_beschleunigung_pro_rad)
            drehzahl_rad_beschleunigung = self.berechne_drehzahl_rad_beschleunigung(drehzahl_motor)
            drehmoment_motor_beschleunigung = self.berechne_drehmoment_motor_beschleunigung(drehmoment)
            drehzahl_motor_beschleunigung = self.berechne_drehzahl_motor_beschleunigung(geschwindigkeit) # Verwende Sektorgeschwindigkeit
            laenge_kumuliert = self.berechne_laenge_kumuliert(laenge)
            hoehendifferenz = self.berechne_hoehendifferenz(steigung, laenge)
            hoehe_absolut = self.berechne_hoehe_absolut(hoehendifferenz)
            dauer_bewegung = self.berechne_dauer_der_bewegung(geschwindigkeit, vorherige_geschwindigkeit)

            if i > 0:
                beschleunigung_zwischen_sektoren = self.berechne_beschleunigung_zwischen_sektoren(i-1, i)
            else:
                beschleunigung_zwischen_sektoren = 0

            laengen.append(laenge)
            gefaelle.append(steigung)
            #reibungen.append(reibung)
            normalkraefte.append(normalkraft)
            rollwiderstaende.append(rollwiderstand_pro_rad)
            steigungswiderstaende.append(steigungswiderstand_pro_rad)
            gesamtwiderstaende_konstant.append(gesamtwiderstaende_konstant_pro_rad)
            kraefte_konstant.append(kraft_konstant_pro_rad)
            leistungen_pro_rad.append(leistung_pro_rad)
            leistungen_pro_motor.append(leistung_pro_motor)
            drehmomente.append(drehmoment)
            drehzahlen_rad.append(drehzahl_rad)
            drehmomente_motor.append(drehmoment_motor)
            drehzahlen_motor.append(drehzahl_motor)
            beschleunigungswiderstaende.append(beschleunigungswiderstand_pro_rad_beschleunigung)
            gesamtwiderstaende_beschleunigung.append(gesamtwiderstand_beschleunigung_pro_rad)
            kraefte_beschleunigung.append(kraft_beschleunigung_pro_rad)
            beschleunigungsleistungen_pro_rad.append(beschleunigungsleistung_pro_rad)
            beschleunigungsleistungen_pro_motor.append(beschleunigungsleistung_pro_motor)
            beschleunigungsdrehmomente_pro_rad.append(beschleunigungsdrehmoment_pro_rad)
            drehzahlen_rad_beschleunigung.append(drehzahl_rad_beschleunigung)
            drehmomente_motor_beschleunigung.append(drehmoment_motor_beschleunigung)
            drehzahlen_motor_beschleunigung.append(drehzahl_motor_beschleunigung)
            laengen_kumuliert.append(laenge_kumuliert)
            hoehendifferenzen.append(hoehendifferenz)
            hoehen_absolut.append(hoehe_absolut)
            dauer_bewegungen.append(dauer_bewegung)
            beschleunigungen_zwischen_sektoren.append(beschleunigung_zwischen_sektoren)
            vorherige_geschwindigkeit = geschwindigkeit
            self.sektor_index = i

        # Erstellt den DataFrame
        self.df = pd.DataFrame({
            "Sektor_Laenge": laengen,
            "Sektor_Gefälle": gefaelle,
            "Sektor_Geschwindigkeit": sektor_geschwindigkeiten,
            #"Sektor_Reibung": reibungen,
            "Normalkraft": normalkraefte,
            "Rollwiderstand_pro_Rad": rollwiderstaende,
            "Steigungswiderstand_pro_Rad": steigungswiderstaende,
            "Gesamtwiderstand_konstant_pro_Rad": gesamtwiderstaende_konstant,
            "Kraft_konstant_pro_Rad": kraefte_konstant,
            "Leistung_pro_Rad": leistungen_pro_rad,
            "Leistung_pro_Motor": leistungen_pro_motor,
            "Drehmoment": drehmomente,
            "Drehzahl_Rad": drehzahlen_rad,
            "Drehmoment_Motor": drehmomente_motor,
            "Drehzahl_Motor": drehzahlen_motor,
            "Beschleunigungswiderstand_pro_Rad": beschleunigungswiderstaende,
            "Gesamtwiderstand_Beschleunigung_pro_Rad": gesamtwiderstaende_beschleunigung,
            "Kraft_Beschleunigung_pro_Rad": kraefte_beschleunigung,
            "Beschleunigungsleistung_pro_Rad": beschleunigungsleistungen_pro_rad,
            "Beschleunigungsleistung_pro_Motor": beschleunigungsleistungen_pro_motor,
            "Beschleunigungsdrehmoment_pro_Rad": beschleunigungsdrehmomente_pro_rad,
            "Drehzahl_Rad_Beschleunigung": drehzahlen_rad_beschleunigung,
            "Drehmoment_Motor_Beschleunigung": drehmomente_motor_beschleunigung,
            "Drehzahl_Motor_Beschleunigung": drehzahlen_motor_beschleunigung,
            "Laenge_kumuliert": laengen_kumuliert,
            "Hoehendifferenz": hoehendifferenzen,
            "Hoehe_Absolut": hoehen_absolut,
            "Dauer_der_Bewegung": dauer_bewegungen,
            "Beschleunigung_zwischen_Sektoren": beschleunigungen_zwischen_sektoren,
            "Geschwindigkeit": sektor_geschwindigkeiten
        })
        return self.df

    def berechne_sektor_geschwindigkeit(self, sektor_index):
        """Berechnet die Geschwindigkeit am Ende eines Sektors."""
        if sektor_index == 0:
            anfangsgeschwindigkeit = 0
        else:
            anfangsgeschwindigkeit = self.berechne_sektor_geschwindigkeit(sektor_index-1)
        laenge = self.parameter.sektor_parameter[sektor_index]["Laenge"]
        beschleunigung = self.parameter.Beschleunigung_a
        endgeschwindigkeit = math.sqrt(anfangsgeschwindigkeit**2 + 2 * beschleunigung * laenge)
        return endgeschwindigkeit

    def berechne_normalkraft(self, steigung):
        return (self.parameter.Gesamtmasse * self.parameter.g * math.cos(math.radians(steigung)))

    def berechne_rollwiderstand_pro_rad(self, normalkraft):
        return self.parameter.Reibungskoeffizent_urr * (normalkraft / self.parameter.Anzahl_Raeder)

    def berechne_steigungswiderstand_pro_rad(self, steigung):
        return (self.parameter.Gesamtmasse * self.parameter.g / self.parameter.Anzahl_Raeder) * math.sin(math.radians(steigung))

    def berechne_gesamtwiderstand_konstant_pro_rad(self, rollwiderstand_pro_rad, steigungswiderstand_pro_rad):
        return rollwiderstand_pro_rad + steigungswiderstand_pro_rad

    def berechne_kraft_konstant_pro_rad(self, gesamtwiderstand_konstant_pro_rad):
        return gesamtwiderstand_konstant_pro_rad * self.parameter.Sicherheitsfaktor

    def berechne_leistung_pro_rad(self, kraft_konstant_pro_rad, geschwindigkeit):
        return (self.parameter.Anzahl_Raeder / self.parameter.Anzahl_Antrieb_n) * kraft_konstant_pro_rad * (geschwindigkeit / 3.6) # Verwende die Sektorgeschwindigkeit

    def berechne_leistung_pro_motor(self, leistung_pro_rad):
        return leistung_pro_rad / self.parameter.Wirkungsgrad_Antrieb

    def berechne_drehmoment(self, kraft_konstant_pro_rad):
        return (self.parameter.Anzahl_Raeder / self.parameter.Anzahl_Antrieb_n) * kraft_konstant_pro_rad * (self.parameter.Raddurchmesser / 2)

    def berechne_drehzahl_rad(self, geschwindigkeit):
        return ((geschwindigkeit * 1000) / (self.parameter.Raddurchmesser * math.pi)) / 60 # Verwende die Sektorgeschwindigkeit

    def berechne_drehmoment_motor(self, drehmoment):
        return drehmoment / self.parameter.Getriebe_uebersetzung

    def berechne_drehzahl_motor(self, drehzahl_rad):
        return drehzahl_rad * self.parameter.Getriebe_uebersetzung

    def berechne_beschleunigungswiderstand_pro_rad(self, bremsen=False):
        if bremsen:
            return (self.parameter.Gesamtmasse / self.parameter.Anzahl_Raeder) * self.parameter.Bremsverzoegerung
        else:
            return (self.parameter.Gesamtmasse / self.parameter.Anzahl_Raeder) * self.parameter.Beschleunigung_a

    def berechne_gesamtwiderstand_beschleunigung_pro_rad(self, gesamtwiderstand_konstant_pro_rad, beschleunigungswiderstand_pro_rad):
        return gesamtwiderstand_konstant_pro_rad + beschleunigungswiderstand_pro_rad

    def berechne_kraft_beschleunigung_pro_rad(self, gesamtwiderstand_beschleunigung_pro_rad):
        return gesamtwiderstand_beschleunigung_pro_rad * self.parameter.Sicherheitsfaktor

    def berechne_beschleunigungsleistung_pro_rad(self, kraft_beschleunigung_pro_rad, geschwindigkeit):
        return (self.parameter.Anzahl_Raeder / self.parameter.Anzahl_Antrieb_n) * kraft_beschleunigung_pro_rad * (geschwindigkeit / 3.6) # Verwende Sektorgeschwindigkeit

    def berechne_beschleunigungsleistung_pro_motor(self, beschleunigungsleistung_pro_rad):
        return beschleunigungsleistung_pro_rad / self.parameter.Wirkungsgrad_Antrieb

    def berechne_beschleunigungsdrehmoment_pro_rad(self, kraft_beschleunigung_pro_rad):
        return (self.parameter.Anzahl_Raeder / self.parameter.Anzahl_Antrieb_n) * kraft_beschleunigung_pro_rad * (self.parameter.Raddurchmesser / 2)

    def berechne_drehzahl_rad_beschleunigung(self, drehzahl_motor):
        return drehzahl_motor / self.parameter.Getriebe_uebersetzung

    def berechne_drehmoment_motor_beschleunigung(self, drehmoment_rad):
        return drehmoment_rad / self.parameter.Getriebe_uebersetzung

    def berechne_drehzahl_motor_beschleunigung(self, geschwindigkeit):
        return (geschwindigkeit * 1000 / 60) / (self.parameter.Raddurchmesser * math.pi) * self.parameter.Getriebe_uebersetzung # Verwende Sektorgeschwindigkeit

    def berechne_laenge_kumuliert(self, sektor_laenge):
        self.laenge_kumuliert += sektor_laenge
        return self.laenge_kumuliert

    def berechne_hoehendifferenz(self, steigung, sektor_laenge):
        return steigung * sektor_laenge / 100

    def berechne_hoehe_absolut(self, hoehendifferenz):
        self.hoehe_absolut += hoehendifferenz
        return self.hoehe_absolut

    def berechne_dauer_der_bewegung(self, geschwindigkeit, vorherige_geschwindigkeit):
        durchschnittsgeschwindigkeit = (geschwindigkeit + vorherige_geschwindigkeit) / 2
        strecke = self.parameter.sektor_parameter[self.sektor_index]["Laenge"]
        if durchschnittsgeschwindigkeit != 0:
            dauer = strecke / (durchschnittsgeschwindigkeit / 3.6)
        else:
            dauer = 0
        return dauer

    def berechne_beschleunigung_zwischen_sektoren(self, sektor_index1, sektor_index2):
        geschwindigkeit1 = self.berechne_sektor_geschwindigkeit(sektor_index1)
        geschwindigkeit2 = self.berechne_sektor_geschwindigkeit(sektor_index2)
        zeit_differenz = 1
        beschleunigung = (geschwindigkeit2 - geschwindigkeit1) / zeit_differenz
        return beschleunigung

# Verwendung der Klassen
fahrzeug_parameter = FahrzeugParameter()
fahrzeug_berechnungen = FahrzeugBerechnungen(fahrzeug_parameter)
df_sektor_daten = fahrzeug_berechnungen.berechne_sektor_daten()

# Exportiere den DataFrame als Textdatei
df_name = input("Bitte geben Sie den Dateinamen für den Dataframe ein: ") + ".txt"
df_name = df_sektor_daten.to_string('sektor_daten.txt', index=False)

# Erstellen und Speichern des Plots
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Spalten zu plotten
spalten_plotten = [
    "Sektor_Laenge", "Sektor_Gefälle", "Normalkraft",
    "Rollwiderstand_pro_Rad", "Steigungswiderstand_pro_Rad", "Gesamtwiderstand_konstant_pro_Rad",
    "Kraft_konstant_pro_Rad", "Leistung_pro_Rad", "Leistung_pro_Motor", "Drehmoment",
    "Drehzahl_Rad", "Drehmoment_Motor", "Drehzahl_Motor", "Beschleunigungswiderstand_pro_Rad",
    "Gesamtwiderstand_Beschleunigung_pro_Rad", "Kraft_Beschleunigung_pro_Rad",
    "Beschleunigungsleistung_pro_Rad", "Beschleunigungsleistung_pro_Motor",
    "Beschleunigungsdrehmoment_pro_Rad", "Drehzahl_Rad_Beschleunigung",
    "Drehmoment_Motor_Beschleunigung", "Drehzahl_Motor_Beschleunigung", "Laenge_kumuliert",
    "Hoehendifferenz", "Hoehe_Absolut", "Dauer_der_Bewegung", "Beschleunigung_zwischen_Sektoren",
    "Geschwindigkeit"
] # "Sektor_Reibung" - derzeit nicht verwendet

for spalte in spalten_plotten:
    fig.add_trace(
        go.Scatter(x=df_sektor_daten["Laenge_kumuliert"], y=df_sektor_daten[spalte], name=spalte),
        secondary_y=False,
    )

# Layout des Plots
fig.update_layout(
    title="Fahrzeugdaten über kumulierte Länge",
    xaxis_title="Kumulierte Länge (m)",
    yaxis_title="Primäre Y-Achse",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.5)",
        borderwidth=1
    )
)

# Speichere den Plot als HTML-Datei
filename = input("Bitte geben Sie den Dateinamen für die HTML-Datei ein (ohne .html): ") + ".html"
fig.write_html(filename)

# Zeige den Plot
fig.show()
