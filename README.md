# VLC – PPM Signal Generator (Analog Discovery 2)

A Python-based Pulse Position Modulation (PPM) signal generator that uses the **Digilent Analog Discovery 2** as the hardware signal output device.

---

## Table of Contents

1. [Overview](#overview)
2. [How PPM Works](#how-ppm-works)
3. [Hardware Requirements](#hardware-requirements)
4. [Software Prerequisites](#software-prerequisites)
5. [File Structure](#file-structure)
6. [Configuration](#configuration)
7. [Running the Program](#running-the-program)
8. [Using the Program](#using-the-program)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This program generates a PPM (Pulse Position Modulation) waveform from a binary bitstream entered by the user, and outputs it in real time via the **Arbitrary Waveform Generator (AWG)** channel of the Analog Discovery 2.

The main entry point is **`main_PPM.py`**, located in the `VLC_Waveform SDK/` directory.

---

## How PPM Works

In PPM, each bit is represented by a pulse placed at a specific position within a fixed time slot:

| Bit | Pulse position |
|-----|----------------|
| `0` | Pulse at the **start** of the bit slot |
| `1` | Pulse at the **middle** of the bit slot |

The default voltage is `+1 V` for pulses and `0 V` for the rest level.  
Timing and amplitude are fully configurable in `config.py`.

---

## Hardware Requirements

- **Digilent Analog Discovery 2** (AD2) – USB-connected multi-function instrument  
  - Used as an Arbitrary Waveform Generator (AWG) to output the PPM signal on its **Analog Out Channel 1 (W1)**  
- A USB cable to connect the AD2 to your PC

---

## Software Prerequisites

### 1. WaveForms (Digilent SDK)

The program relies on the **DWF (Device WaveForms) shared library** (`dwf.dll` on Windows, `libdwf.so` on Linux, `libdwf.dylib` on macOS).

Download and install **WaveForms** from Digilent's website:  
👉 https://digilent.com/reference/software/waveforms/waveforms-3/start

> **Important:** Close the WaveForms desktop application before running any Python script, as WaveForms and a Python script cannot both control the device at the same time.

### 2. Python 3

Install Python 3 (version 3.7 or later recommended).

### 3. Python Packages

Install the required packages:

```bash
pip install matplotlib
```

> `ctypes` and `time` are part of the Python standard library and do not need to be installed separately.

---

## File Structure

```
VLC_Waveform SDK/
├── main_PPM.py          ← Main script – run this file
├── PPM.py               ← PPM signal generation logic
├── config.py            ← All configurable parameters and device setup
├── wavegen.py           ← Low-level waveform generator helpers (SDK-style)
├── device.py            ← Device open/close/error-check helpers
├── dwfconstants.py      ← DWF library constants
├── main.py              ← Standalone demo: custom square wave (separate test)
└── waveform_data.csv    ← (optional) Exported waveform samples
```

---

## Configuration

Before running the program, review and adjust the parameters in **`config.py`** to match your setup:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DESIRED_PEAK_VOLTAGE` | `1.0` V | Pulse amplitude |
| `REST_LEVEL` | `0.0` V | Voltage when no pulse is sent |
| `BIT_DURATION` | `1e-6` s (1 µs) | Duration of each bit slot |
| `PULSE_WIDTH` | `BIT_DURATION / 2` | Width of each pulse |
| `SAMPLES_PER_BIT_GEN` | `2048` | AWG samples per bit (determines sample rate) |
| `LOOP_CONTINUOUSLY` | `True` | Repeat the waveform indefinitely (`True`) or once (`False`) |
| `CHANNEL_AWG` | `0` | AWG output channel (0 = W1) |
| `save_to_CSV` | `False` | Set to `True` in `main_PPM.py` to save samples to `waveform_data.csv` |
| `diagnostic` | `False` | Set to `True` in `main_PPM.py` to print signal details to the console |

---

## Running the Program

1. **Connect** the Analog Discovery 2 to your computer via USB.
2. **Close** the WaveForms desktop application if it is open.
3. Open a terminal and navigate to the SDK folder:

   ```bash
   cd "VLC_Waveform SDK"
   ```

4. Run the main script:

   ```bash
   python main_PPM.py
   ```

   On success, you will see:

   ```
   Device opened successfully.
   Bitfolge in Zahlen eintragen...
   ```

   > The prompt "Bitfolge in Zahlen eintragen..." means "Enter bit sequence as numbers..." in German.

---

## Using the Program

Once the program starts, it enters an interactive loop:

1. **Enter a binary bitstream** when prompted (the prompt reads "Bitfolge in Zahlen eintragen...", meaning "Enter bit sequence as numbers...") – type a sequence of `0`s and `1`s, for example:

   ```
   Bitfolge in Zahlen eintragen...01101001
   ```

2. The program will:
   - Generate the corresponding PPM waveform
   - Output the signal on the AWG channel (W1) of the Analog Discovery 2
   - Wait for the signal duration to complete, then prompt again

3. **Repeat** with a new bitstream as many times as needed.

4. To **stop** the program, press `Ctrl+C`. The AWG output will be stopped and the device will be closed cleanly.

> **Tip:** You can observe the generated waveform using the Analog Discovery 2's oscilloscope input (Channel 1 / 1+) and the WaveForms Scope instrument — but only after stopping `main_PPM.py`, since only one application can control the device at a time.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Failed to open device` | Make sure the AD2 is connected via USB and WaveForms is closed |
| `Could not load dwf library` | Install WaveForms from Digilent; ensure the DWF library is in your system PATH |
| `No device detected` | Try a different USB port or cable; check Device Manager / `lsusb` |
| Script hangs or no output | Verify `BIT_DURATION` and bitstream length are not too large |
| `ModuleNotFoundError: matplotlib` | Run `pip install matplotlib` |