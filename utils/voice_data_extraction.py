import parselmouth
from parselmouth.praat import call
import numpy as np
from scipy.stats import entropy

def extract_voice_features(audio_file):

    sound = parselmouth.Sound(audio_file)
    pitch = call(sound, "To Pitch", 0.0, 75, 600)

    # Calculate jitter measures using individual Parselmouth functions
    pointprocess = call(sound, "To PointProcess (periodic, cc)", 75, 600)
    
    # Jitter measurements
    jitter_percent = call(pointprocess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    jitter_abs = call(pointprocess, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3)
    jitter_rap = call(pointprocess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
    jitter_ppq5 = call(pointprocess, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
    jitter_ddp = call(pointprocess, "Get jitter (ddp)", 0, 0, 0.0001, 0.02, 1.3)
    
    # Shimmer measurements
    shimmer = call([sound, pointprocess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_db = call([sound, pointprocess], "Get shimmer (local_dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_apq3 = call([sound, pointprocess], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_apq5 = call([sound, pointprocess], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_apq11 = call([sound, pointprocess], "Get shimmer (apq11)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_dda = call([sound, pointprocess], "Get shimmer (dda)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    
    # HNR (Harmonics-to-Noise Ratio)
    harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
    hnr = call(harmonicity, "Get mean", 0, 0)
    
    # NHR (Noise-to-Harmonics Ratio) = 1 / linear_HNR
    # HNR from Praat is in dB, so convert: linear_HNR = 10^(HNR_dB / 10)
    # Guard against zero/negative linear values (unvoiced / very noisy signal)
    if hnr > 0:
        nhr_value = 1.0 / (10 ** (hnr / 10))
    else:
        nhr_value = float('inf')
    
    # Get pitch periods for nonlinear features
    # Alternative approach: use pitch values directly for period calculation
    pitch_values = pitch.selected_array['frequency']
    voiced_frames = pitch_values[pitch_values > 0]  # Only voiced frames
    
    if len(voiced_frames) > 0:
        # Convert frequency to periods (1/frequency)
        periods = 1.0 / voiced_frames
    else:
        periods = np.array([])
    
    # Nonlinear features
    if len(periods) < 50:
        rpde = dfa = ppe = np.nan
    else:
        # PPE: Pitch Period Entropy
        hist, _ = np.histogram(periods, bins=min(20, len(periods)//5), density=True)
        hist = hist[hist > 0]
        ppe = entropy(hist + 1e-10)
        
        # Simplified RPDE: Recurrence Period Density Entropy
        diffs = np.abs(np.diff(periods))
        rec_threshold = np.std(diffs) * 0.1
        rec_matrix = (np.abs(periods[:, None] - periods[None, :]) < rec_threshold).astype(float)
        np.fill_diagonal(rec_matrix, 0)
        hist_rpde, _ = np.histogram(rec_matrix.flatten(), bins=2, density=True)
        rpde = entropy(hist_rpde + 1e-10)
        
        # DFA: Detrended Fluctuation Analysis
        y = np.cumsum(periods - np.mean(periods))
        scales = np.logspace(np.log10(4), np.log10(len(y)/4), 8, dtype=int)
        log_F = []
        log_s = []
        for s in scales:
            if s > len(y) // 4:
                continue
            num_seg = len(y) // s
            rms = []
            for i in range(num_seg):
                seg = y[i*s:(i+1)*s]
                if len(seg) < 3:
                    continue
                x = np.arange(len(seg))
                p = np.polyfit(x, seg, 1)
                detrend = seg - np.polyval(p, x)
                rms.append(np.sqrt(np.mean(detrend**2)))
            if rms:
                F = np.sqrt(np.mean(rms))
                log_F.append(np.log(F))
                log_s.append(np.log(s))
        if len(log_F) > 1:
            slope, _ = np.polyfit(log_s, log_F, 1)
            dfa = slope
        else:
            dfa = np.nan
    
    return {
        'Jitter(%)': jitter_percent * 100, 
        'Jitter(Abs)': jitter_abs, 
        'Jitter:RAP': jitter_rap,
        'Jitter:PPQ5': jitter_ppq5, 
        'Jitter:DDP': jitter_ddp,
        'Shimmer': shimmer, 
        'Shimmer(dB)': shimmer_db, 
        'Shimmer:APQ3': shimmer_apq3,
        'Shimmer:APQ5': shimmer_apq5, 
        'Shimmer:APQ11': shimmer_apq11, 
        'Shimmer:DDA': shimmer_dda,
        'NHR': nhr_value, 
        'HNR': hnr,
        'RPDE': float(rpde),
        'DFA': float(dfa),
        'PPE': float(ppe)
    }


# Load audio file
# audio_file = "test_voice.wav" 
# features = measure_jitter_shimmer(audio_file)
# print(features)