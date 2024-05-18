import librosa
import IPython.display
import matplotlib as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.signal import find_peaks
from collections import Counter

path = "./audio/Merry-Go-Round_Of_Life.mp3"

duration = int(librosa.get_duration(path=path))

data, sample_rate = librosa.load(path, sr=44100, mono=True, duration=duration)

data_len = len(data)

music = [data[int(i*sample_rate):int((i+0.5)*sample_rate)] for i in np.arange(0, duration, 0.5)]

music = pd.DataFrame(music)

for index, row in music.iterrows():
    music.iloc[index,:] = librosa.amplitude_to_db(row)

fig = plt.figure(figsize=(198, 108), dpi=10)
ax = fig.add_subplot(1, 1, 1)

for index, row in music.iterrows():
    ax.scatter(np.arange(len(row)), row, s=1)

ax.set_xticks(np.arange(0, len(row), 10))
ax.set_ylabel('db')

fig.savefig('show_describe.png')