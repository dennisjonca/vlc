# VLC – PPM-Signalgenerator (Analog Discovery 2)

Ein Python-basierter Pulspositionsmodulations-Signalgenerator (PPM), der den **Digilent Analog Discovery 2** als Hardware-Ausgabegerat verwendet.

---

## Inhaltsverzeichnis

1. [Uebersicht](#uebersicht)
2. [Funktionsweise von PPM](#funktionsweise-von-ppm)
3. [Hardwareanforderungen](#hardwareanforderungen)
4. [Softwarevoraussetzungen](#softwarevoraussetzungen)
5. [Dateistruktur](#dateistruktur)
6. [Konfiguration](#konfiguration)
7. [Programm starten](#programm-starten)
8. [Programm verwenden](#programm-verwenden)
9. [Fehlerbehebung](#fehlerbehebung)

---

## Uebersicht

Dieses Programm erzeugt ein PPM-Signal (Pulspositionsmodulation) aus einer vom Benutzer eingegebenen binaeren Bitfolge und gibt es in Echtzeit ueber den **Arbitrary Waveform Generator (AWG)** des Analog Discovery 2 aus.

Der Einstiegspunkt des Programms ist **`main_PPM.py`** im Verzeichnis `VLC_Waveform SDK/`.

---

## Funktionsweise von PPM

Bei PPM wird jedes Bit durch einen Impuls dargestellt, der an einer bestimmten Position innerhalb eines festen Zeitfensters platziert wird:

| Bit | Impulsposition |
|-----|----------------|
| `0` | Impuls am **Anfang** des Zeitfensters |
| `1` | Impuls in der **Mitte** des Zeitfensters |

Die Standardspannung betraegt `+1 V` fuer Impulse und `0 V` fuer den Ruhepegel.
Zeitverhalten und Amplitude sind vollstaendig in `config.py` konfigurierbar.

---

## Hardwareanforderungen

- **Digilent Analog Discovery 2** (AD2) – USB-Multifunktionsinstrument
  - Wird als Arbitrary Waveform Generator (AWG) verwendet, um das PPM-Signal am **Analogausgang Kanal 1 (W1)** auszugeben
- Ein USB-Kabel zur Verbindung des AD2 mit dem PC

---

## Softwarevoraussetzungen

### 1. WaveForms (Digilent SDK)

Das Programm benoetigt die **DWF-Bibliothek (Device WaveForms)** (`dwf.dll` unter Windows, `libdwf.so` unter Linux, `libdwf.dylib` unter macOS).

WaveForms kann von der Digilent-Website heruntergeladen und installiert werden:
https://digilent.com/reference/software/waveforms/waveforms-3/start

> **Wichtig:** Die WaveForms-Desktopanwendung muss geschlossen sein, bevor ein Python-Skript ausgefuehrt wird, da WaveForms und ein Python-Skript das Geraet nicht gleichzeitig steuern koennen.

### 2. Python 3

Python 3 installieren (Version 3.7 oder hoeher empfohlen).

### 3. Python-Pakete

Das benoetigt Paket installieren:

```bash
pip install matplotlib
```

> `ctypes` und `time` sind Bestandteil der Python-Standardbibliothek und muessen nicht separat installiert werden.

---

## Dateistruktur

```
VLC_Waveform SDK/
+-- main_PPM.py          <- Hauptskript – diese Datei ausfuehren
+-- PPM.py               <- Logik zur PPM-Signalerzeugung
+-- config.py            <- Alle konfigurierbaren Parameter und Geraeteeinrichtung
+-- wavegen.py           <- Low-Level-Hilfsfunktionen fuer den Waveformgenerator (SDK-Stil)
+-- device.py            <- Hilfsfunktionen fuer Gerateverbindung, -trennung und Fehlerbehandlung
+-- dwfconstants.py      <- DWF-Bibliothekskonstanten
+-- main.py              <- Eigenstaendige Demo: benutzerdefinierte Rechteckwelle (separater Test)
+-- waveform_data.csv    <- (optional) Exportierte Wellenformdaten
```

---

## Konfiguration

Vor dem Starten des Programms sollten die Parameter in **`config.py`** geprueft und bei Bedarf angepasst werden:

| Parameter | Standardwert | Beschreibung |
|-----------|--------------|--------------|
| `DESIRED_PEAK_VOLTAGE` | `1.0` V | Impulsamplitude |
| `REST_LEVEL` | `0.0` V | Spannung waehrend des Ruhepegels (kein Impuls) |
| `BIT_DURATION` | `1e-6` s (1 µs) | Dauer eines Bit-Zeitfensters |
| `PULSE_WIDTH` | `BIT_DURATION / 2` | Impulsbreite innerhalb eines Zeitfensters |
| `SAMPLES_PER_BIT_GEN` | `2048` | AWG-Abtastwerte pro Bit (bestimmt die Abtastrate) |
| `LOOP_CONTINUOUSLY` | `True` | Wellenform unbegrenzt wiederholen (`True`) oder einmalig ausgeben (`False`) |
| `CHANNEL_AWG` | `0` | AWG-Ausgangskanal (0 = W1) |
| `save_to_CSV` | `False` | Auf `True` setzen in `main_PPM.py`, um Abtastwerte in `waveform_data.csv` zu speichern |
| `diagnostic` | `False` | Auf `True` setzen in `main_PPM.py`, um Signaldetails in der Konsole auszugeben |

---

## Programm starten

1. Den Analog Discovery 2 per USB mit dem Computer verbinden.
2. Die WaveForms-Desktopanwendung schliessen, falls sie geoeffnet ist.
3. Ein Terminal oeffnen und in den SDK-Ordner wechseln:

   ```bash
   cd "VLC_Waveform SDK"
   ```

4. Das Hauptskript ausfuehren:

   ```bash
   python main_PPM.py
   ```

   Bei Erfolg erscheint folgende Ausgabe:

   ```
   Device opened successfully.
   Bitfolge in Zahlen eintragen...
   ```

---

## Programm verwenden

Nach dem Start wechselt das Programm in eine interaktive Schleife:

1. Eine binaere Bitfolge eingeben, wenn der Prompt erscheint – eine Folge aus `0` und `1`, zum Beispiel:

   ```
   Bitfolge in Zahlen eintragen...01101001
   ```

2. Das Programm fuehrt anschliessend folgende Schritte aus:
   - Es erzeugt die entsprechende PPM-Wellenform
   - Es gibt das Signal ueber den AWG-Kanal (W1) des Analog Discovery 2 aus
   - Es wartet, bis die Signaldauer abgelaufen ist, und fragt dann erneut nach einer Eingabe

3. Den Vorgang mit einer neuen Bitfolge beliebig oft wiederholen.

4. Das Programm mit `Ctrl+C` beenden. Der AWG-Ausgang wird gestoppt und das Geraet ordnungsgemaess getrennt.

> **Hinweis:** Das erzeugte Signal kann mit dem Oszilloskopeingang des Analog Discovery 2 (Kanal 1 / 1+) und dem WaveForms-Scope-Instrument beobachtet werden – jedoch erst nach dem Beenden von `main_PPM.py`, da jeweils nur eine Anwendung das Geraet steuern kann.

---

## Fehlerbehebung

| Problem | Loesung |
|---------|---------|
| `Failed to open device` | Sicherstellen, dass der AD2 per USB verbunden und WaveForms geschlossen ist |
| `Could not load dwf library` | WaveForms von Digilent installieren; sicherstellen, dass die DWF-Bibliothek im System-PATH vorhanden ist |
| `No device detected` | Einen anderen USB-Anschluss oder ein anderes Kabel verwenden; Geraetemanager bzw. `lsusb` pruefen |
| Skript haengt oder keine Ausgabe | `BIT_DURATION` und Bitfolgenlange pruefen; diese sollten nicht zu gross sein |
| `ModuleNotFoundError: matplotlib` | `pip install matplotlib` ausfuehren |