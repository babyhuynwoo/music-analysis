import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = 'c198bfa36514499584519d8f2fe7d32f'
client_secret = 'f53a6ccd4a1c4925818ce687be15bd9f'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_audio_features_and_rgb(track_name):

    track_info = sp.search(q=track_name, type='track', limit=1)
    track_id = track_info["tracks"]["items"][0]["id"]
    audio_features = sp.audio_features(tracks=[track_id])[0]
    
    valence = audio_features['valence']
    tempo = audio_features['tempo']
    loudness = audio_features['loudness']

    print(valence, tempo, loudness)
    
    if tempo < 100.0 and -10.0 >= loudness > -30.0:
        rgb = [170, 255, 255]
    elif tempo < 100.0 and -30.0 >= loudness >= -60.0:
        rgb = [130, 130, 130]
    elif tempo >= 100.0 and -30.0 >= loudness >= -60.0:
        rgb = [255, 255, 140]
    elif tempo >= 100.0 and -10.0 >= loudness > -30.0:
        rgb = [255, 70, 255]
    else:
        rgb = [0, 0, 0] 
    return rgb, loudness

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
    db = np.interp(db, (np.min(db), np.max(db)), (0, 1))

    diff = []
    for i, peak in enumerate(filtered_peaks):
        if(i+1 == len(filtered_peaks)):
            break
        diff.append(filtered_peaks[i+1] - filtered_peaks[i])
  
    time = []
    for per in diff:
        time.append(per/sr)

    result = []
    for p, t in zip(filtered_peaks, time):
        result.append(round(db[p], 2))
        result.append(round(t, 2))

    return result


track_name = 'merrygoroundoflife'  
rgb = get_audio_features_and_rgb(track_name)

# print(rgb)

# audio_path = 'C:\\Users\\LIM\\Desktop\\dico\\Test_team\\sample_audio\\'  
# result = process_audio(audio_path+track_name+'.mp3')

# result_with_rgb = rgb + result

# result_reshaped = np.array(result_with_rgb).reshape(-1, 1)
# df = pd.DataFrame(result_reshaped, columns=[track_name])
# df = df.round(2)

# df.to_csv(track_name+'.csv', index=False)
# print(df)


# {
#   "acousticness": 0.00242,
#   "analysis_url": "https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B",
#   "danceability": 0.585,
#   "duration_ms": 237040,
#   "energy": 0.842,
#   "id": "2takcwOaAZWiXQijPHIx7B",
#   "instrumentalness": 0.00686,
#   "key": 9,
#   "liveness": 0.0866,
#   "loudness": -5.883,
#   "mode": 0,
#   "speechiness": 0.0556,
#   "tempo": 118.211,
#   "time_signature": 4,
#   "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B",
#   "type": "audio_features",
#   "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
#   "valence": 0.428
# }