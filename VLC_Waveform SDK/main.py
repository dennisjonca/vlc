import time
import matplotlib.pyplot as plt
from ctypes import *
from dwfconstants import *
import numpy as np

# Load DWF library
dwf = cdll.dwf
hdwf = c_int()

# Open the first connected device
print("Opening device...")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
if hdwf.value == 0:
    print("No device detected.")
    quit()

# --- Custom Waveform Generation for Square Wave ---
frequency = 1e6  # 1 MHz
amplitude = 2    # Volts peak-to-peak
offset = 0       # Volts DC offset (for square wave, often 0 or amplitude/2)

# Define the number of samples for the custom waveform
# A larger number of samples will result in a more detailed waveform,
# but also consumes more memory on the device.
# For a square wave, a relatively small number of samples can be effective.
custom_samples = 20
# Calculate samples per cycle for the custom waveform based on desired frequency
# This is an important consideration for custom waveforms.
# If your device has a maximum custom waveform buffer size, ensure custom_samples
# doesn't exceed it.
# The `dwfAnalogOutNodeDataSet` function takes samples that represent one cycle
# of the waveform.
# For a square wave, we'll represent one cycle (e.g., high then low).

# Create a numpy array for the custom square wave data
# We'll create a single cycle of the square wave: first half high, second half low.
custom_waveform_data = np.zeros(custom_samples, dtype=np.float64)
half_samples = custom_samples // 2
custom_waveform_data[0:half_samples] = amplitude / 2 + offset # High part (relative to offset)
custom_waveform_data[half_samples:] = -amplitude / 2 + offset # Low part (relative to offset)

# Convert the numpy array to a C-compatible array
c_custom_waveform_data = (c_double * custom_samples)(*custom_waveform_data)
idx = custom_samples/2
idxs = int(idx -5)
idxe = int(idx +5)
print(c_custom_waveform_data[idxs:idxe])

# Set up Wavegen Channel 1 for custom waveform
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_bool(True))       # enable Wavegen 1
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), funcCustom)       # set to custom function
dwf.FDwfAnalogOutNodeDataSet(hdwf, c_int(0), c_int(0), c_custom_waveform_data, c_int(custom_samples)) # load custom data
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(frequency))
# Amplitude and offset are typically handled within the custom data when funcCustom is used,
# but you might still use these functions to scale or offset the entire custom waveform
# if your hardware supports it or if you want to apply a general scaling.
# For this specific square wave generation, the amplitude is baked into custom_waveform_data.
# dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(amplitude))
# dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(0), c_int(0), c_double(offset)) # Set overall offset if needed
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(True))                     # start output

# Configure Scope (AnalogIn) on Channel 1
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))              # enable channel 1
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(amplitude * 1.5))  # Adjust range based on expected amplitude
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, acqmodeSingle)
# Sample rate should be high enough to capture the square wave accurately
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(frequency))                          # 100 MHz sample rate
# Buffer size to capture enough cycles for visualization
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(4096))                             # sample size

time.sleep(2)  # Wait for signal to stabilize

# Start scope capture
#dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))

# Wait for acquisition to complete
#sts = c_byte()
#while True:
#    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
#    if sts.value == DwfStateDone.value:
#        break
#    time.sleep(0.01)

# Retrieve data
#samples = 4096
#rgBuffer = (c_double * samples)()
#dwf.FDwfAnalogInStatusData(hdwf, c_int(0), rgBuffer, c_int(samples))

# Plot
#plt.plot(rgBuffer)
#plt.title(f"Captured Custom Square Wave ({frequency/1e6:.1f} MHz)")
#plt.xlabel("Sample")
#plt.ylabel("Voltage (V)")
#plt.grid(True)
#plt.show()

# Clean up
dwf.FDwfDeviceCloseAll()
