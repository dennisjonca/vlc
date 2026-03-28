import config

def generate_PPM(bitstream ,print_sample = False):
    # --- Calculations for PPM Signal Generation ---
    sample_rate_gen = config.SAMPLES_PER_BIT_GEN / config.BIT_DURATION
    pulse_sample_width = int(config.PULSE_WIDTH * sample_rate_gen)

    signal = []
    for bit_char in bitstream:
        bit = int(bit_char)
        samples = [config.REST_LEVEL] * config.SAMPLES_PER_BIT_GEN

        if bit == 0:
            pulse_value = config.DESIRED_PEAK_VOLTAGE
            start_index = 0
        else:
            pulse_value = config.DESIRED_PEAK_VOLTAGE
            start_index = int(0.5 * sample_rate_gen * config.BIT_DURATION)

        for i in range(pulse_sample_width):
            if start_index + i < config.SAMPLES_PER_BIT_GEN:
                samples[start_index + i] = pulse_value
        signal.extend(samples)
    if print_sample:
        # --- DEBUGGING: Print first few samples of generated signal ---
        print("\n--- Python Generated Signal (First 200 samples) ---")
        for i in range(min(len(signal), 200)):
            print(f"Sample {i}: {signal[i]:.2f}")
        print(f"Generated signal min/max in Python: {min(signal):.2f}V / {max(signal):.2f}V")
        print("----------------------------------------------------\n")
    return signal

def save_signal(data,output_filename = "waveform_data.csv"):
    # --- Save data to a CSV file for manual WaveForms import ---
    #output_filename = "waveform_data.csv"
    try:
        with open(output_filename, 'w') as f:
            for val in data:
                f.write(f"{val}\n")
        print(f"Waveform data saved to {output_filename} for manual import into WaveForms.")
    except IOError as e:
        print(f"Error saving waveform data to file: {e}")
    # --- End Save data ---