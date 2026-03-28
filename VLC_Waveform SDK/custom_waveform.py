import time
import numpy as np
import wavegen  # your wrapper for the WaveForms SDK
import dwfconstants as dwfc

# Create your custom waveform (e.g., 1000 samples of a triangular shape)
num_samples = 1000
t = np.linspace(0, 1, num_samples)
custom_signal = 2 * np.abs(2 * (t - np.floor(t + 0.5))) - 1  # Triangular wave, range -1 to 1
amplitude = 2.0  # Output peak voltage will be scaled to this
offset = 0.0     # No DC offset

# Connect to device
hdwf = wavegen.open_device()

# Configure Wavegen Channel 1
wavegen.configure_wavegen(
    hdwf=hdwf,
    channel=0,  # Wavegen 1
    func=dwfc.funcCustom,
    hzFrequency=1e3,           # 1 kHz repetition
    amplitude=amplitude,
    offset=offset,
    symmetry=50.0,             # Ignored for custom, but safe default
    samples=custom_signal      # Your actual waveform
)

# Start output
wavegen.start_wavegen(hdwf, channel=0)

print("Custom signal is being output on Wavegen Channel 1. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping wavegen...")
    wavegen.stop_wavegen(hdwf, channel=0)
    wavegen.close_device(hdwf)
