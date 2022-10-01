import time
from ulab import numpy as np
import supervisor
samplingrate = 1000
sample = []
rpeaks = []
templates = []
qpeaks = []
speaks = []
tpeaks = []
ppeaks = []

def get_voltage(pin):
    value = (pin * 5) / 65535
    # print((value,))
    return value

# def get_sample():
    # sample = []
    # while len(sample) < 8192:
    # sample.append(get_voltage(analog_in))
    # time.sleep(0.001)
    # return sample

def readsample():
    global sample
    sample = []
    try:
        with open("/sample.txt", "r") as f:
            line = f.readline()
            while line != '':
                sample.append(get_voltage(int(line)))
                # time.sleep(0.01)
                line = f.readline()
    except OSError as e:  # Typically when the filesystem isn't writeable...
        print(str(e))

def fft_filter():
    global sample
    fresult = np.fft.fft(np.array(sample))
    ll = len(fresult[0])
    fresult[0][0 : round(ll * 2 / samplingrate)] = 0
    fresult[1][0 : round(ll * 2 / samplingrate)] = 0
    fresult[0][ll - round(ll * 2 / samplingrate) : ll] = 0
    fresult[1][ll - round(ll * 2 / samplingrate) : ll] = 0
    sample = np.fft.ifft(fresult[0], fresult[1])[0]
    return sample

# ===========================================================================
# Nabian et al. (2018)
# ===========================================================================
def ecg_findpeaks_nabian2018(signal, sampling_rate=1000):
    window_size = int(0.4 * sampling_rate)

    peaks = np.zeros(len(signal))

    for i in range(1 + window_size, len(signal) - window_size):
        ecg_window = signal[i - window_size : i + window_size]
        rpeak = np.argmax(ecg_window)

        if i == (i - window_size + rpeak):
            peaks[i] = 1

    return peaks
def find_templates():
    intervalr = []
    global templates
    prevr = 0
    for i in range(len(rpeaks-1)):
        if rpeaks[i] == 1:
            if prevr != 0:
                intervalr.append(i-prevr)
            prevr = i
    window_size = int(np.mean(intervalr))-1
    for i in range(len(rpeaks)):
        if rpeaks[i] == 1:
            a = i-1
            templates.append((i - int(window_size/2)+5, i, a + int(window_size/2)))


def getQPositions():
    global templates
    global sample
    global qpeaks
    Q_positions = []

    for each in templates:
        # Get Q Position
        template_left = sample[each[0]:(each[1]+1)]
        Q_position = min(template_left)
        Q_positions.append(Q_position)
    qpeaks = Q_positions
    
def getSPositions():
    global templates
    global sample
    global speaks
    S_positions = []

    for each in templates:
        # Get S Position
        template_right = sample[each[1]:(each[2])]
        S_position = min(template_right)
        S_positions.append(S_position)
    speaks = S_positions

def getPPositions():
    global templates
    global sample
    global ppeaks
    P_positions = []

    for each in templates:
        # Get P position
        template_left = sample[each[0]:each[1]-3]
        P_position = max(template_left)
        P_positions.append(P_position)
    ppeaks = P_positions
    
def getTPositions():
    global templates
    global sample
    global tpeaks
    T_positions = []

    for each in templates:
        # Get S Position
        template_right = sample[each[1]+3:(each[2])]
        T_position = max(template_right)
        T_positions.append(T_position)
    tpeaks = T_positions
    
def start():
    global sample
    global rpeaks
    readsample()
    sample = fft_filter()
    rpeaks = ecg_findpeaks_nabian2018(sample, sampling_rate=samplingrate)
    find_templates()
    getQPositions()
    getSPositions()
    getPPositions()
    getTPositions()

def printnew():
    global sample
    global qpeaks
    global speaks
    global tpeaks
    global ppeaks
    for i in range(len(sample)):
        a = 0.0
        b = 0.0
        c = 0.0
        d = 0.0
        if sample[i] in qpeaks:
            a = -1.0
        if sample[i] in speaks:
            b = -1.0
        if sample[i] in ppeaks:
            c = 1.0
        if sample[i] in tpeaks:
            d = 1.0
        print((sample[i], rpeaks[i], a, b, c, d, ))
        time.sleep(0.2)
    time.sleep(2)
while True:
# if supervisor.runtime.serial_bytes_available:
#    value = input()
    #if value == 'start':
start()
printnew()
# while True:
#    initial = time.monotonic()
#    sample = []
#    while len(sample) < 1024:
#        sample.append(get_voltage(analog_in))
#        time.sleep(0.001)
#    now = time.monotonic()
#    print((now-initial,))
#    time.sleep(3)

# def writesample():
    # try:
        # with open("/sample.txt", "w") as fp:
        # samples = get_sample()
            # for sample in samples:
            # fp.write('{0:d}\n'.format(sample))
            # fp.flush()
    # except OSError as e:  # Typically when the filesystem isn't writeable...
        # print(str(e))
