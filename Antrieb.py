class FahrzeugParameter:
    def __init__(self):
        self.g = 9.81
        self.Masse_leer = float(input("Masse leer eingeben in kg: "))
        self.Masse_Cab_Src = float(input("Masse Kabine und SRC eingeben in kg: "))
        self.Masse_Nutzlast = float(input("Masse Nutzlast eingeben in kg: "))
        self.Anzahl_Raeder = float(input("Anzahl Räder eingeben: "))
        self.Raddurchmesser = float(input("Raddurchmesser eingeben in m: "))
        self.Reibungskoeffizent_urr = float(input("Reibungskoeffizent der Unterlage eingeben: "))
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
        self.gesamt_laenge = 0
        for i in range(self.Anzahl_Sektoren):
            Sektor_Laenge = float(input(f"Länge des Sektors {i+1} in m: "))
            Sektor_Gefaelle = float(input(f"Gefälle des Sektors {i+1} in %: "))
            Sektor_Reibung = float(input(f"Reibungskoeffizient des Sektors {i+1}: ")) 
            self.sektor_parameter.append({"Laenge": Sektor_Laenge, "Gefälle": Sektor_Gefaelle, "Reibung": Sektor_Reibung})
            self.gesamt_laenge += Sektor_Laenge
        # Berechnung der Gesamtlänge
        #Gesamt_Laenge = 0
        #for sektor in self.sektor_parameter:
        #    Gesamt_Laenge += sektor["Laenge"]
        #    return Gesamt_Laenge

        # Berechnung aus den Eingaben
        self.Gesamtmasse = self.Masse_leer + self.Masse_Cab_Src + self.Masse_Nutzlast
        self.Gewichtskraft = self.Gesamtmasse * self.g
        self.Batterie_Kapazitaet_Start_kWh = self.Batterie_Kapazitaet * self.Batterie_Ladestatus_Start / 100

        print("Gesamtmasse: ", self.Gesamtmasse, "kg")
        print("Gewichtskraft: ", self.Gewichtskraft, "N")
        print("Batteriekapazität Start: ", self.Batterie_Kapazitaet_Start_kWh, "kWh")
        #print("Gesamtstrecke:", Gesamt_Laenge, "km")

# Aufruf und Instanziierung der Klasse
fahrzeug_daten = FahrzeugParameter()

# Zugriff auf die Parameter außerhalb der "Klasse" (eigentlich ein Objekt)
print("\nParameter als Klasse:")
print("Gesamtmasse:", fahrzeug_daten.Gesamtmasse)
print("Gewichtskraft:", fahrzeug_daten.Gewichtskraft)
print("Batteriekapazität Start:", fahrzeug_daten.Batterie_Kapazitaet_Start_kWh)
print("Sektordaten:", fahrzeug_daten.sektor_parameter)
print("Gesamtlänge:", fahrzeug_daten.gesamt_laenge)


