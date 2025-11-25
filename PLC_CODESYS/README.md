# PLC CODESYS - Gessmann Joystick/Thrust Lever CAN Integration

## Übersicht / Overview

Diese Dokumentation beschreibt die Structured Text (ST) Implementierung für die Anbindung von Gessmann Joysticks und Thrust Lever Modulen über CAN-Bus an die Intercontrol DIGSY Fusion S SPS.

This documentation describes the Structured Text (ST) implementation for connecting Gessmann joysticks and thrust lever modules via CAN bus to the Intercontrol DIGSY Fusion S PLC.

## Hardware

- **SPS / PLC**: Intercontrol DIGSY Fusion S
- **Entwicklungsumgebung / Development Environment**: CODESYS
- **Eingabegeräte / Input Devices**: Gessmann Joystick, Thrust Lever
- **Kommunikation / Communication**: CAN-Bus (250 kbit/s Standard)

## Projektstruktur / Project Structure

```
PLC_CODESYS/
├── CAN_Communication/
│   └── CAN_Interface.st       # CAN-Bus Kommunikationsschnittstelle
├── Joystick/
│   ├── Gessmann_Joystick.st   # Gessmann Joystick Verarbeitung
│   └── Thrust_Lever_Control.st # Schubhebel Steuerung
├── Main_Control.st            # Hauptprogramm
└── README.md                  # Diese Dokumentation
```

## Module / Modules

### 1. CAN_Interface.st

#### Datentypen / Data Types

| Typ / Type | Beschreibung / Description |
|------------|----------------------------|
| `CAN_Message` | Struktur für CAN-Nachrichten (ID, DLC, Daten, Timestamp) |
| `CAN_Status` | Enumeration für CAN-Status (OK, ERROR, BUSY, TIMEOUT, etc.) |

#### Funktionsbausteine / Function Blocks

**FB_CAN_Interface**
- Hauptschnittstelle zur CAN-Kommunikation
- Initialisierung des CAN-Controllers
- Senden und Empfangen von CAN-Nachrichten

| Eingang / Input | Typ / Type | Beschreibung / Description |
|-----------------|------------|----------------------------|
| bEnable | BOOL | Aktiviert CAN-Schnittstelle |
| dwBaudrate | DWORD | CAN Baudrate (Standard: 250000) |
| bSendMessage | BOOL | Trigger zum Senden |
| stTxMessage | CAN_Message | Zu sendende Nachricht |

| Ausgang / Output | Typ / Type | Beschreibung / Description |
|------------------|------------|----------------------------|
| bInitialized | BOOL | CAN initialisiert |
| bMessageReceived | BOOL | Neue Nachricht empfangen |
| stRxMessage | CAN_Message | Letzte empfangene Nachricht |
| eStatus | CAN_Status | Aktueller Status |

**FB_CAN_MessageFilter**
- Filterung von CAN-Nachrichten nach ID und Maske

### 2. Gessmann_Joystick.st

#### Datentypen / Data Types

| Typ / Type | Beschreibung / Description |
|------------|----------------------------|
| `Joystick_Axis` | Struktur für Achsendaten (Rohwert, skalierter Wert, Totzone) |
| `Gessmann_Joystick_Data` | Komplette Joystick-Daten (Achsen, Tasten, Status) |

#### Funktionsbaustein / Function Block

**FB_Gessmann_Joystick**
- Verarbeitung von Gessmann Joystick CAN-Nachrichten
- Skalierung der Achsenwerte auf -100% bis +100%
- Totzone-Verarbeitung
- Timeout-Überwachung

| Eingang / Input | Typ / Type | Beschreibung / Description |
|-----------------|------------|----------------------------|
| bEnable | BOOL | Aktiviert Joystick-Verarbeitung |
| stCANMessage | CAN_Message | Eingehende CAN-Nachricht |
| bNewCANMessage | BOOL | Neue Nachricht verfügbar |
| dwJoystickCANID | DWORD | Basis CAN-ID (Standard: 0x180) |
| dwThrustLeverCANID | DWORD | Thrust Lever CAN-ID (Standard: 0x181) |
| dwButtonsCANID | DWORD | Tasten CAN-ID (Standard: 0x182) |
| tTimeout | TIME | Kommunikations-Timeout |
| rDeadzoneX/Y/Z | REAL | Totzone pro Achse (%) |

| Ausgang / Output | Typ / Type | Beschreibung / Description |
|------------------|------------|----------------------------|
| stJoystickData | Gessmann_Joystick_Data | Komplette Joystick-Daten |
| rAxisX/Y/Z | REAL | Skalierte Achsenwerte |
| rThrustLever | REAL | Skalierter Thrust Lever Wert |
| bOnline | BOOL | Kommunikationsstatus |
| bError | BOOL | Fehlerflag |

### 3. Thrust_Lever_Control.st

#### Datentypen / Data Types

| Typ / Type | Beschreibung / Description |
|------------|----------------------------|
| `Thrust_Mode` | Betriebsmodus (MANUAL, CRUISE, RAMP, EMERGENCY) |
| `Thrust_Status` | Status der Schubsteuerung |

#### Funktionsbaustein / Function Block

**FB_Thrust_Lever_Control**
- Erweiterte Schubhebelsteuerung
- Rampen für sanftes Beschleunigen/Verzögern
- Tempomat-Funktion (Cruise Control)
- Nothalte-Funktion

| Eingang / Input | Typ / Type | Beschreibung / Description |
|-----------------|------------|----------------------------|
| bEnable | BOOL | Aktiviert Steuerung |
| rThrustLeverInput | REAL | Roher Schubhebel-Eingang (-100% bis +100%) |
| eRequestedMode | Thrust_Mode | Gewünschter Betriebsmodus |
| bEmergencyStop | BOOL | Nothalte-Trigger |
| bCruiseSet/Resume/Cancel | BOOL | Tempomat-Steuerung |
| rMaxThrust | REAL | Maximale Schubgrenze (%) |
| rMinThrust | REAL | Minimale Schubgrenze (%) |
| rRampUpRate | REAL | Beschleunigungsrate (%/s) |
| rRampDownRate | REAL | Verzögerungsrate (%/s) |

| Ausgang / Output | Typ / Type | Beschreibung / Description |
|------------------|------------|----------------------------|
| rThrustOutput | REAL | Finaler Schubausgang (-100% bis +100%) |
| stStatus | Thrust_Status | Aktueller Status |
| bActive | BOOL | Steuerung aktiv |
| bAtTarget | BOOL | Zielwert erreicht |

### 4. Main_Control.st

Hauptprogramm das alle Module integriert:
- CAN-Interface Initialisierung
- Joystick-Verarbeitung
- Thrust Lever Steuerung
- Sicherheitsüberwachung
- Fehlerbehandlung

## CAN-Nachrichtenformat / CAN Message Format

### Joystick Achsen (CAN-ID: 0x180)

| Byte | Beschreibung / Description |
|------|----------------------------|
| 0-1 | X-Achse (High Byte, Low Byte) |
| 2-3 | Y-Achse (High Byte, Low Byte) |
| 4-5 | Z-Achse (High Byte, Low Byte) |
| 6-7 | Reserviert |

### Thrust Lever (CAN-ID: 0x181)

| Byte | Beschreibung / Description |
|------|----------------------------|
| 0-1 | Thrust Lever Position (High Byte, Low Byte) |
| 2-7 | Reserviert |

### Tasten / Buttons (CAN-ID: 0x182)

| Bit | Beschreibung / Description |
|-----|----------------------------|
| 0 | Taste 1 (Cruise Set) |
| 1 | Taste 2 (Cruise Resume) |
| 2 | Taste 3 (Cruise Cancel) |
| 3-7 | Tasten 4-8 |

## Konfiguration / Configuration

### Globale Variablen / Global Variables (GVL_Joystick)

```
CAN_BAUDRATE      : DWORD := 250000;    // CAN Baudrate
JOYSTICK_BASE_ID  : DWORD := 16#180;    // Basis CAN-ID
COMM_TIMEOUT      : TIME := T#500MS;     // Kommunikations-Timeout
CYCLE_TIME        : TIME := T#10MS;      // SPS Zykluszeit

DEADZONE_X        : REAL := 5.0;         // Totzone X-Achse (%)
DEADZONE_Y        : REAL := 5.0;         // Totzone Y-Achse (%)
DEADZONE_Z        : REAL := 5.0;         // Totzone Z-Achse (%)
DEADZONE_THRUST   : REAL := 2.0;         // Totzone Thrust Lever (%)

MAX_THRUST        : REAL := 100.0;       // Max. Schub (%)
MIN_THRUST        : REAL := -30.0;       // Min. Schub (%)
RAMP_UP_RATE      : REAL := 50.0;        // Beschleunigungsrate (%/s)
RAMP_DOWN_RATE    : REAL := 75.0;        // Verzögerungsrate (%/s)
```

## Integration in CODESYS

1. **Neues Projekt erstellen** mit DIGSY Fusion S Gerät
2. **Bibliotheken hinzufügen**: CAN-Bibliothek für DIGSY Fusion S
3. **Dateien importieren**: Alle .st Dateien in das Projekt importieren
4. **Hardware konfigurieren**: CAN-Schnittstelle im Gerätekonfigurator einrichten
5. **Hauptprogramm verknüpfen**: PLC_PRG als zyklische Task einrichten (10ms empfohlen)

## Sicherheitshinweise / Safety Notes

- Der Nothalte-Eingang (bEmergencyStop) hat höchste Priorität
- Bei CAN-Kommunikationsverlust werden alle Ausgänge auf sichere Werte gesetzt
- Timeout-Überwachung erkennt Kommunikationsausfälle
- Rampen-Funktion verhindert abrupte Schubänderungen

## Autor / Author

Berechnungsplattform Team

## Version

1.0.0 - Initial Release
