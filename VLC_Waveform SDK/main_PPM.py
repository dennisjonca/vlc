import time
import ctypes
import matplotlib.pyplot as plt
from ctypes import *
import dwfconstants
import config
import PPM


# Function to check DWF error codes
def check_dwf_error(result, dwf_lib, function_name):
    """
    Checks the result of a DWF function call and prints an error if it's not successful.
    (Assumes 0 is success, non-zero is an error code for the function_name provided).
    """
    if result == dwfconstants.dwfercNoErc.value:  # dwfercNoErc is 0
        return True
    else:
        szError = ctypes.create_string_buffer(512)
        dwf_lib.FDwfGetLastErrorMsg(szError)
        print(f"!!! DWF Error in {function_name}: {szError.value.decode('utf-8')} (Result Code: {result}) !!!")
        return False

# Load device and check for OS
dwf,hdwf = config.load_device()


diagnostic = False
save_to_CSV = False

while True:
    user_input = input(f"Bitfolge in Zahlen eintragen...")

    #generate a PPM Signal, based on input in Config ----> in fkt. ?
    signal = PPM.generate_PPM(user_input,False)

    #change to C compatible
    data = (ctypes.c_double * len(signal))(*signal)

    #Save the C compatible date for import into Waveforms
    if save_to_CSV:
        PPM.save_signal(data,"waveform_data.csv")

    config.configure_device(dwf,hdwf,data, user_input)
    #start sending
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(config.CHANNEL_AWG), c_bool(True))

    total_signal_duration = len(user_input) * config.BIT_DURATION

    # Add a short delay to allow the single shot to complete or begin
    time.sleep(total_signal_duration +0.05)  # Wait for the waveform to complete, plus a small buffer
    #status_awg_after_wait = c_int()
    #result = dwf.FDwfAnalogOutStatus(hdwf, c_int(config.CHANNEL_AWG), byref(status_awg_after_wait))
    #check_dwf_error(result, dwf, "FDwfAnalogOutStatus (after wait)")
    #print(f"AWG Status after wait: {status_awg_after_wait.value} (Expected: {dwfconstants.DwfStateDone.value})")

    if diagnostic:
        print(f"PPM waveform sent. Bitstream: '{user_input}'. Loop mode: {config.LOOP_CONTINUOUSLY}")
        print(f"Total signal duration per cycle: {total_signal_duration * 1e6:.2f} µs")
        print(f"Expected output voltage: +/-{config.DESIRED_PEAK_VOLTAGE:.2f}V")


    #if config.LOOP_CONTINUOUSLY:  # This block is now effectively skipped
     #   print("\nAnalog Out is running continuously. Press Enter to stop.")
     #   input()  # Wait for user to press Enter

# --- Clean up ---
print("\n--- Cleaning Up ---")
# Stop the AWG
print(f"Stopping AWG channel {config.CHANNEL_AWG}...")
dwf.FDwfAnalogOutConfigure(hdwf, c_int(config.CHANNEL_AWG), c_bool(False))
print("AWG stopped.")

# Close the device
print("Closing device...")
config.close_device(dwf)
print("Device closed.")
