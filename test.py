import librosa
import IPython.display
import matplotlib as plt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.signal import argrelextrema
from collections import Counter

path = "./Merry-Go-Round_Of_Life.mp3"
duration = int(librosa.get_duration(path=path))
sr = librosa.get_samplerate(path=path)
data, sample_rate = librosa.load(path, sr=sr, mono=True, duration=duration)

db = librosa.amplitude_to_db(data, ref=np.max)

peaks = argrelextrema(db, np.greater, order=int(sr/10))

plt.figure(figsize=(20, 10))

plt.plot(db)
for peak in peaks[0]:
    plt.scatter(peak, db[peak], color='red')

plt.savefig('Figure_1.png', dpi=300) 
plt.show()
