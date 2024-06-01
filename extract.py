import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

def process_audio(path):
    duration = int(librosa.get_duration(path=path))
    sr = librosa.get_samplerate(path=path)

    data, sample_rate = librosa.load(path, sr=sr, mono=True, duration=duration)

    db = librosa.amplitude_to_db(data, ref=np.max)

    peaks = argrelextrema(db, np.greater, order=int(sr/10))

    filtered_peaks = peaks[0][np.where(db[peaks[0]] > -25)]
    filtered_peaks = np.insert(filtered_peaks, 0, 0)
    filtered_peaks = np.insert(filtered_peaks, len(filtered_peaks), sr*duration-1)
    db = db + abs(db.min())
    db = np.interp(db, (np.min(db), np.max(db)), (0, 255))

    diff  = []
    for i, peak in enumerate(filtered_peaks):
        if(i+1 == len(filtered_peaks)):
            break
        diff.append(filtered_peaks[i+1] - filtered_peaks[i])

    time = []
    for per in diff:
        time.append(per/sr)

    result = []
    for p, t in zip(filtered_peaks,time):
        result.append(round(db[p],2))
        result.append(round(t,2))

    return result

result = process_audio('sample_audio\\merry_go_round_test.mp3')

df = pd.DataFrame(result, columns=['merry_go_round_test'])
df = df.round(2)
df.to_csv('merry_go_round_test.csv', index=False)

# plt.figure(figsize=(20, 10))
# plt.plot(db)

# for peak in filtered_peaks:
#     plt.scatter(peak, db[peak], color='red')

# plt.savefig('merry_go_round_test')
# plt.show()