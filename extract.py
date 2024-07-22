import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials

from constants import C_ID, C_SECRET

def get_audio_features_and_rgb(track_name):
    # 스포티파이 API를 이용하여 음악의 특징을 추출하고, RGB값을 반환

    # 음악을 이름으로 검색해 첫 곡의 ID를 가져옴
    track_info = sp.search(q=track_name, type='track', limit=1) 
    # track id를 사용해 음악의 특징을 가져옴
    track_id = track_info["tracks"]["items"][0]["id"]
    audio_features = sp.audio_features(tracks=[track_id])[0]
    
    # 음악의 특징을 가져옴
    valence = audio_features['valence']
    tempo = audio_features['tempo']
    loudness = audio_features['loudness']
    
    # 특징에 따라 RGB값을 반환
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

    # RGB값을 차이를 극대화한 후 0~1 사이의 값으로 변환
    rgb = [val / 255.0 for val in rgb]
    rgb = [val ** 8 for val in rgb]

    return rgb, loudness

def process_audio(path:str, song:str, loudness:float) -> list:
    # 음악 파일을 받아 음악의 피크를 찾아내고, 그 피크의 시간과 크기를 반환

    # 음악 파일의 위치 설정
    loc = (path+song+".mp3")

    # 음악 파일의 길이와 샘플레이트를 가져옴
    # 샘플레이트란 초당 샘플링 횟수를 의미 ex) 44100kHz 일 경우 1초에 44100개의 샘플링이 이루어짐
    duration = int(librosa.get_duration(path=loc))
    sr = librosa.get_samplerate(path=loc)

    # librosa를 이용해 음악 파일을 불러옴
    data, sample_rate = librosa.load(loc, sr=sr, mono=True, duration=duration)

    # 음악 파일을 dB로 변환
    db = librosa.amplitude_to_db(data, ref=np.max)

    # 음악 파일의 피크를 찾아내고, 그 피크의 시간(인덱스)를 반환받음
    peaks = argrelextrema(db, np.greater, order=int(sr/10))

    # 피크의 크기가 loudness보다 큰 피크만 필터링
    filtered_peaks = peaks[0][np.where(db[peaks[0]] >= loudness)]

    # 음악의 시작과 끝을 추가
    filtered_peaks = np.insert(filtered_peaks, 0, 0)
    filtered_peaks = np.insert(filtered_peaks, len(filtered_peaks), sr*duration-1)

    """
    피크를 그래프로 표현
    """
    plt.figure(figsize=(40, 8))
    plt.plot(db)

    for peak in filtered_peaks:
        plt.scatter(peak, db[peak], color='red', s = 10)

    plt.title(f'Audio Peaks Over Time({song})')
    plt.xlabel('Time')
    plt.ylabel('dB')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.savefig(f'./images/{song}.png')


    # 전체 데시벨을 양수로 변환
    db = db + abs(db.min())

    # 전체 데시벨의 차이를 극대화한 후 0~255 사이의 값으로 변환
    db = db ** 8
    db = np.interp(db, (np.min(db), np.max(db)), (0, 255))

    # 피크 사이의 시간(인덱스)을 계산
    diff  = []
    for i, peak in enumerate(filtered_peaks):
        if(i+1 == len(filtered_peaks)):
            break
        diff.append(filtered_peaks[i+1] - filtered_peaks[i])

    # 시간을 초 단위로 변환
    time = []
    for per in diff:
        time.append(per/sr)

    # 피크의 크기와 유지시간을 반환
    result = []
    for p, t in zip(filtered_peaks,time):
        result.append(round(db[p],2))  
        result.append(round(t,2))

    # 결과적으로 반환되는 값은 [크기1, 유지시간1, 크기2, 유지시간2, ...] 형태
    return result


if __name__ == '__main__':

    # Spotify API를 이용하기 위한 인증 -> API 인증 정보는 constants.py에 저장
    client_credentials_manager = SpotifyClientCredentials(client_id=C_ID, client_secret=C_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


    # 음악 파일의 위치와 이름 지정
    path = "sample_audio/"
    song = "RiverFlowsinYou"


    # 음악의 특징과 RGB값을 가져옴
    rgb, loudness = get_audio_features_and_rgb(path+song)

    # API에서 읽어온 Loudeness를 넣어 음악 파일을 처리
    result = process_audio(path, song, loudness)

    # RGB값을 결과에 추가
    result.insert(0, rgb[0])
    result.insert(1, rgb[1])
    result.insert(2, rgb[2])

    # 결과를 데이터프레임으로 변환 후 csv로 저장
    file = pd.DataFrame(result, columns=[f'{song}'])
    file = file.round(2)
    file.to_csv(f'./data/{song}.csv', index=False)