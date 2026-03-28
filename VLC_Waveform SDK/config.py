# config.py
# This file centralizes all configurable parameters and DWF device setup functions.

import ctypes
from ctypes import c_int, c_bool, c_double, byref, c_byte
import dwfconstants  # Import the dwfconstants module directly
import matplotlib.pyplot as plt # Kept for plot_data function

# --- Konfigurierbare Parameter for PPM Signal Generation ---

# Desired peak voltage for pulses (+1V for '0' bit, -1V for '1' bit).
DESIRED_PEAK_VOLTAGE = 1.0

# Set to True to repeat the PPM signal indefinitely, False to play once.
# CHANGED FOR NON-REPEATING SIGNAL TEST
LOOP_CONTINUOUSLY = True

# Base level when no pulse is sent (0V).
REST_LEVEL = 0.0

# Duration of each bit in the PPM signal (e.g., 1 microsecond).
BIT_DURATION = 1e-6

# Width of each pulse within a bit duration (e.g., 0.5 microseconds).
PULSE_WIDTH = BIT_DURATION / 2.0

# Number of samples to define one bit duration for AWG generation.
# 100 samples/microsecond = 100 MS/s AWG sample rate (max for AD2 AWG).
SAMPLES_PER_BIT_GEN = 2048


# --- Analog Discovery 2 Hardware-Specific Constants ---
# Analog Out Channel 0 is typically used for AWG.
CHANNEL_AWG = 0

# Analog In Channel 0 is typically used for Oscilloscope.
CHANNEL_SCOPE = 0

# Scope sample rate (maximum for AD2 scope is typically 100 MS/s).
SCOPE_SAMPLE_RATE = 100e6

# Default range for the input channel (e.g., 4.0V total range for +/-2V).
SCOPE_CHANNEL_RANGE = 4.0

# Default offset for the input channel (0V for center of range).
SCOPE_CHANNEL_OFFSET = 0.0

# Trigger level for scope (e.g., 0.0V to trigger on any pulse crossing zero).
SCOPE_TRIGGER_LEVEL = 0.0

# Auto-timeout for trigger (e.g., 0.1 seconds, if no trigger after this time, acquisition proceeds).
SCOPE_TRIGGER_AUTO_TIMEOUT = 0.1

# Buffer factor for desired record length on the scope (e.g., 1.5 for 50% buffer).
SCOPE_RECORD_LENGTH_BUFFER_FACTOR = 1.5

# --- DWF API Constants (from dwfconstants.py, mapped for clarity) ---
ACQMODE_RECORD = dwfconstants.acqmodeRecord.value
FUNC_CUSTOM = dwfconstants.funcCustom.value
TRIGSRC_DETECTOR_ANALOGIN = dwfconstants.trigsrcDetectorAnalogIn.value
TRIGTYPE_EDGE = dwfconstants.trigtypeEdge.value
TRIGSLOPE_EITHER = dwfconstants.DwfTriggerSlopeEither.value
DWF_STATE_DONE = dwfconstants.DwfStateDone.value

# --- DWF Utility Functions (Scope-related, no direct AWG config here) ---

def load_waveform_SDK():
    try:
        dwf = ctypes.cdll.LoadLibrary("dwf.dll")
    except OSError:
        try:
            dwf = ctypes.cdll.LoadLibrary("libdwf.so")
        except OSError:
            try:
                dwf = ctypes.cdll.LoadLibrary("libdwf.dylib")
            except OSError:
                print(
                    "Error: Could not load dwf library. Ensure it's in your system's PATH or Python's LD_LIBRARY_PATH.")
                exit(1)
    return dwf

def load_device():
    dwf = load_waveform_SDK()

    # Open device
    hdwf = c_int()
    # FDwfDeviceOpen returns 1 (DwfTrue) on success, 0 (DwfFalse) on failure.
    # The handle (hdwf.value) will be 0 if no device was opened successfully.
    result_open = dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))  # Store result_open for informational print

    if hdwf.value == 0:  # This is the primary way to check if device opened successfully
        # If hdwf.value is 0, then the device open failed. Print the DWF error if available.
        szError = ctypes.create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szError)
        print(f"Failed to open device: {szError.value.decode('utf-8')} (FDwfDeviceOpen returned: {result_open})")
        print("No device found or WaveForms software is still open.")
        print("Please ensure your Analog Discovery 2 is connected and WaveForms software is closed.")
        exit(1)

    print("Device opened successfully.")
    return dwf, hdwf

def configure_device(dwf,hdwf,data,bitstream):
    # --- Wavegen (Analog Out) Configuration and Start (Direct DWF calls for detailed debugging) ---

    dwf.FDwfAnalogOutReset(hdwf, c_int(CHANNEL_AWG))
    dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(CHANNEL_AWG), c_int(0), c_bool(True))
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(CHANNEL_AWG), c_int(0), c_int(FUNC_CUSTOM))
    dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(CHANNEL_AWG), c_int(0), c_double(REST_LEVEL))
    #dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(CHANNEL_AWG), c_int(0), c_double(1.0))

    # Calculate the frequency for the custom waveform
    total_signal_duration = len(bitstream) * BIT_DURATION
    waveform_frequency = 1.0 / total_signal_duration if total_signal_duration > 0 else 0.0  # Avoid division by zero

    #print(f"[DEBUG: config.py] Data length (samples): {len(data)}")
    #print(f"[DEBUG: config.py] Calculated total_signal_duration: {total_signal_duration * 1e6:.2f} µs")
    #print(f"[DEBUG: config.py] Calculated waveform_frequency (Hz): {waveform_frequency:.2f}")

    dwf.FDwfAnalogOutFrequencySet(hdwf, c_int(CHANNEL_AWG), c_double(waveform_frequency))

    dwf.FDwfAnalogOutNodeDataSet(hdwf, c_int(CHANNEL_AWG), c_int(0), data, c_int(len(data)))

    num_repeats = 1000
    explicit_run_time = total_signal_duration * num_repeats

    if LOOP_CONTINUOUSLY:
        num_repeats = 0  # 0 means infinite repeats for Analog Out
        explicit_run_time = 0.0  # 0.0 means infinite run for Analog Out
        #print(f"[DEBUG: config.py] LOOP_CONTINUOUSLY is True: num_repeats set to {num_repeats}, explicit_run_time set to {explicit_run_time}")
    #else:
     #   print(f"[DEBUG: config.py] LOOP_CONTINUOUSLY is False: num_repeats set to {num_repeats}, explicit_run_time set to {explicit_run_time}")


    dwf.FDwfAnalogOutRepeatSet(hdwf, c_int(CHANNEL_AWG), c_int(num_repeats))
    dwf.FDwfAnalogOutRunSet(hdwf, c_int(CHANNEL_AWG), c_double(explicit_run_time))

    dwf.FDwfAnalogOutRepeatTriggerSet(hdwf, c_int(CHANNEL_AWG), c_bool(False))
    dwf.FDwfAnalogOutWaitSet(hdwf, c_int(CHANNEL_AWG), c_double(0.0))

    dwf.FDwfAnalogOutIdleSet(hdwf, c_int(CHANNEL_AWG),c_int(dwfconstants.DwfAnalogOutIdleOffset.value))  # Or DwfAnalogOutIdleDisable, based on desired post-pulse state

def configure_scope(hdwf_handle, dwf_lib, num_samples_to_acquire):
    """
    Configures the Oscilloscope (Analog In) on the Analog Discovery 2.

    Args:
        hdwf_handle (c_int): Handle to the open DWF device.
        dwf_lib (ctypes.CDLL): Loaded DWF library.
        num_samples_to_acquire (int): The total number of samples to acquire for the scope.
    """
    dwf_lib.FDwfAnalogInAcquisitionModeSet(hdwf_handle, c_int(ACQMODE_RECORD))
    dwf_lib.FDwfAnalogInFrequencySet(hdwf_handle, c_double(SCOPE_SAMPLE_RATE))
    dwf_lib.FDwfAnalogInChannelRangeSet(hdwf_handle, c_int(CHANNEL_SCOPE), c_double(SCOPE_CHANNEL_RANGE))
    dwf_lib.FDwfAnalogInChannelOffsetSet(hdwf_handle, c_int(CHANNEL_SCOPE), c_double(SCOPE_CHANNEL_OFFSET))
    dwf_lib.FDwfAnalogInChannelEnableSet(hdwf_handle, c_int(CHANNEL_SCOPE), c_bool(True))

    # --- Trigger Configuration ---
    dwf_lib.FDwfAnalogInTriggerSourceSet(hdwf_handle, c_int(TRIGSRC_DETECTOR_ANALOGIN))
    dwf_lib.FDwfAnalogInTriggerTypeSet(hdwf_handle, c_int(TRIGTYPE_EDGE))
    dwf_lib.FDwfAnalogInTriggerChannelSet(hdwf_handle, c_int(CHANNEL_SCOPE))
    dwf_lib.FDwfAnalogInTriggerLevelSet(hdwf_handle, c_double(SCOPE_TRIGGER_LEVEL))
    dwf_lib.FDwfAnalogInTriggerConditionSet(hdwf_handle, c_int(TRIGSLOPE_EITHER))
    dwf_lib.FDwfAnalogInTriggerPositionSet(hdwf_handle, c_double(0.0))
    dwf_lib.FDwfAnalogInTriggerAutoTimeoutSet(hdwf_handle, c_double(SCOPE_TRIGGER_AUTO_TIMEOUT))

    desired_record_length = len(BITSTREAM) * BIT_DURATION * SCOPE_RECORD_LENGTH_BUFFER_FACTOR
    dwf_lib.FDwfAnalogInRecordLengthSet(hdwf_handle, c_double(desired_record_length))

def start_scope_acquisition(hdwf_handle, dwf_lib):
    """Starts the oscilloscope acquisition."""
    dwf_lib.FDwfAnalogInConfigure(hdwf_handle, c_bool(False), c_bool(True))

def wait_for_scope_done(hdwf_handle, dwf_lib):
    """Waits until the oscilloscope acquisition is complete."""
    sts = c_byte()
    while True:
        dwf_lib.FDwfAnalogInStatus(hdwf_handle, c_int(1), byref(sts))
        if sts.value == DWF_STATE_DONE:
            break
        import time
        time.sleep(0.005)
    return sts

def retrieve_scope_data(hdwf_handle, dwf_lib, num_samples):
    """Retrieves the captured data from the oscilloscope."""
    rgBuffer = (c_double * num_samples)()
    dwf_lib.FDwfAnalogInStatusData(hdwf_handle, c_int(CHANNEL_SCOPE), rgBuffer, c_int(num_samples))
    return rgBuffer

def plot_data(samples_scope, rgBuffer):
    """Plots the captured oscilloscope data."""
    time_axis = [i / SCOPE_SAMPLE_RATE * 1e6 for i in range(samples_scope)]
    plt.figure(figsize=(12, 6))
    plt.plot(time_axis, rgBuffer)
    plt.title(f"Captured PPM Waveform (Bitstream: '{BITSTREAM}')")
    plt.xlabel("Time (µs)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    plt.axhline(DESIRED_PEAK_VOLTAGE, color='green', linewidth=0.8, linestyle=':',
                label=f'+{DESIRED_PEAK_VOLTAGE:.1f}V (0-bit)')
    plt.axhline(-DESIRED_PEAK_VOLTAGE, color='red', linewidth=0.8, linestyle=':',
                label=f'-{DESIRED_PEAK_VOLTAGE:.1f}V (1-bit)')
    plt.legend()
    plt.ylim(-DESIRED_PEAK_VOLTAGE * 1.5, DESIRED_PEAK_VOLTAGE * 1.5)
    plt.tight_layout()
    plt.show()

def close_device(dwf_lib):
    """Closes all open DWF devices."""
    dwf_lib.FDwfDeviceCloseAll()

