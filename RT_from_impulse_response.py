import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import signal


def generador_de_octavas(starting_frecuency, num_de_octavas):
    octavas = [starting_frecuency]
    x = starting_frecuency
    for i in range(num_de_octavas):
        x *= 2
        octavas.append(x)
    return octavas
    
def min_dist_cero(x):
    for i in range(len(x)):
        if x[i] == 0:
            x[i] = min(x)
    return x

def octaves_bands_border(bands):
    borders = []
    for i in range(len(bands)):
        borders.append([bands[i] * 2 ** (-1/2), bands[i] * 2 ** (1/2)])
    return borders

def third_bands_border(bands):
    bordes = []
    for i in range(len(bands)):
        bordes.append([bands[i] * 2 ** (-1/6), bands[i] * 2 ** (1/6)])
    return bordes

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low, high], analog=False,
                        btype='band', output='sos')
    return sos

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.sosfilt(sos, data)
    return y

def rms_value(audio):
    rms = np.sqrt(np.mean(audio**2))
    return rms

def rms_per_window(audio, window):
    rms_max = []
    if len(audio) % window == 0:
        for i in range(int(len(audio)/window)):
            rms_of_window = rms_value(audio[window * i: window + window *i])
            rms_max = np.append(rms_max, np.ones(window) * rms_of_window)
        return rms_max
    else:
        resto = (len(audio) % window)
        
        for i in range(int(len(audio)/window)):
            rms_of_window = rms_value(audio[window * i: window + window *i])
            rms_max = np.append(rms_max, np.ones(window) * rms_of_window)
        rms_max = np.append(rms_max, np.ones(resto) * rms_value(audio[-resto:]))
        return rms_max

def noise_cut(audio):
    window = 4000
    rms_of_impulse = rms_per_window(audio, window)
    
    print(len(audio) == len(rms_of_impulse))
    count = 0
    for i in range(len(audio)):
        if rms_of_impulse[i] < rms_of_impulse[i + 1]:
            count += 1
        if count == 1:
            break
    return i - window + 1
    
def rt_from_impulse_response(impulse_path, bands, band_type = 'octave', rt = 't30', cut_manually = False):
    """
    Return a list of the reverb time per band according to the bands input.
    impulse_path: Path of the impulse respond recording
    bands: List of frequencies per band
    band_type: Default assume band-type as octave, optional use 'third'
    rt: Default calculates t30, optional 't20' or 't10'
    cut_manually: Set to True if the IR was manually cut to avoid floor noise
    """

    raw_impulse, fs = sf.read(impulse_path)
    reverb_time = np.zeros(len(bands))
    
    if band_type == 'octave':
        border_bands = octaves_bands_border(bands)
    elif band_type == 'third':
        border_bands = third_bands_border(bands)
        
    rt = rt.lower()
    if rt == 't30':
        init = -5.0
        end = -35.0
        factor = 2.0
    elif rt == 't20':
        init = -5.0
        end = -25.0
        factor = 3.0
    elif rt == 't10':
        init = -5.0
        end = -15.0
        factor = 6.0

        
    if len(raw_impulse.shape) > 1:
        raw_impulse = (raw_impulse[:,0] + raw_impulse[:,1]) / 2
    
    for i in range(len(bands)):
        
        filter_impulse = butter_bandpass_filter(raw_impulse, border_bands[i][0], border_bands[i][1], fs)  #Filer per band
        
        filter_impulse = np.abs(signal.hilbert(filter_impulse))  #Hilbert transform
        
        filter_impulse = signal.savgol_filter(filter_impulse, 121, 5)  #Smoothing
    
        #Cut the signal
        if  not cut_manually:
            cut = noise_cut(filter_impulse())

        #Avoid division by zero
        filter_impulse = min_dist_cero(filter_impulse[0:cut])
    
        #Schroeder integration
        sch = np.cumsum(filter_impulse[::-1]**2)[::-1]
        sch_db = 10.0 * np.log10(sch / np.max(sch))
    
    
        #Lineal Regression
        x = np.array(list(range(len(sch_db))))
        coeficients = np.polyfit(x,sch_db,1)
        slope, intercept = coeficients[0], coeficients[1]
    
    
        db_regress_init = (init - intercept) / slope
        db_regress_end = (end - intercept) / slope
        reverb_time[i] = (factor * (db_regress_end - db_regress_init))/fs
    
    return reverb_time




