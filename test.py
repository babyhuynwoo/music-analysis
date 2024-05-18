import librosa
import IPython.display
import matplotlib as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.signal import find_peaks
from collections import Counter

path = "Test_team\Merry-Go-Round_Of_Life.mp3"

duration = librosa.get_duration(path=path)
duration = int(duration)

data, sample_rate = librosa.load(path, sr=44100, mono=True, duration=duration)

data_len = len(data)

def len_to_sec(data_len):
    data_sec_len = data_len / sample_rate
    return np.linspace(0, data_sec_len, data_len)

x_second = len_to_sec(data_len)

def min_max_scaler(array):
    return (array - array.min()) / (array.max() - array.min())

# 진폭을 구한다 (db로 변환)
power = min_max_scaler(librosa.amplitude_to_db(data))

autocorrelation = sm.tsa.acf(data, nlags=2000)

peaks = find_peaks(autocorrelation)[0] # Find peaks of the autocorrelation
lag = peaks[0] # Choose the first peak as our pitch component lag

pitch = sample_rate / lag # Transform lag into frequency

hertz2keys = {440: 'A_4'}
keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']


# 440hz 이상 계산
octave = 4
pitch_num = 1
    
while True:
    if keys[pitch_num % 12] == 'C':
        octave += 1

    if octave > 8:
        break

    # calculate hz
    hz = round(440 * 2 ** (pitch_num / 12), 2) # 0을 대입하면 440hz 출력

    hertz2keys[hz] = keys[pitch_num % 12] + f'_{octave}'

    pitch_num += 1


# 440hz 이하 계산
octave = 4
pitch_num = -1
    
while True:
    if keys[pitch_num % 12] == 'B':
        octave -= 1

    if octave < 0:
        break
    # calculate hz
    hz = round(440 * 2 ** (pitch_num / 12), 2) # 0을 대입하면 440hz 출력

    hertz2keys[hz] = keys[pitch_num % 12] + f'_{octave}'

    pitch_num -= 1

test_hz = 445.4745

def herts_to_closed_key(hertz):
    """음원이 계이름과 정확하게 일치하는 hertz를 출력하지 않을 경우 근사하는 주파수의 계이름을 출력"""
    
    if hertz == 0: # 소리가 없는 경우 No Signal을 출력
        return 'NS'
    
    herts_array = np.array(list(hertz2keys.keys())) # 딕셔너리 key값을 리스트로 변경
    closed_index = np.argmin(abs(herts_array - hertz)) # 확인 대상과 가장 가까운 계이름 hertz 찾기
    key = hertz2keys[herts_array[closed_index]] # 출력
    
    return key

herts_to_closed_key(test_hz)

data, sample_rate = librosa.load(path, sr=44100, mono=True, duration=duration)

# 0.01초 단위로 데이터 슬라이싱
sec = 0.01
trim_sec = int(1 / sec)
n_rows = data.shape[0] // sample_rate * trim_sec # 지정한 주기로 슬라이싱
dataset = data.reshape(n_rows, -1)

detected_hertz = []
for sample in dataset:
    if sample.mean() == 0: # 구간 내 소리가 없는 경우 0 입력
        detected_hertz.append(0) # No Signal
        continue
    
    autocorrelation = sm.tsa.acf(sample, nlags=200)
    peaks = find_peaks(autocorrelation)[0] # Find peaks of the autocorrelation (threshold=0.001)
    
    if peaks.shape[0] == 0: # peak가 없는 경우 0 입력
        detected_hertz.append(0) # No Peak
        continue
    
    lag = peaks[0] # Choose the first peak as our pitch component lag
    pitch = int(sample_rate / lag) # Transform lag into frequency
    
    detected_hertz.append(herts_to_closed_key(pitch)) # change hertz to closed key hertz

# task 1
# 0.1초 단위로 가장 빈도수가 높은 키 하나만 남기기
def freq_check(array):
    """np.array에서 빈도수가 가장 높은 원소를 출력"""
    freq_result = np.unique(array, return_counts=True) # (array([ 980, 1002, 1260]), array([1, 8, 1])) 튜플 반환
    result = freq_result[0][np.argmax(freq_result[1])] # 최대 빈도수 인덱싱
    
    return result # int

sec = 0.5
trim_sec = int(1 / sec)
n_rows = duration * trim_sec
result = np.array(detected_hertz).reshape(n_rows, -1) # (220, 10)

freq_hertz_result = np.array([freq_check(array) for array in result])

# task 2
# n개 단위로 그룹화한 뒤 빈도수 낮은 key값을 제외
def freq_check2(array, threshold:float):
    "범위 내 요소별 빈도수 체크 및 일정 빈도수 이하 요소 제외"
    result = []
    for hertz_list in array:
        counter = Counter(hertz_list)
        temp = [hertz for hertz in hertz_list if counter[hertz] > hertz_list.shape[0] * threshold]
        result = result + temp
    return result # list

group_size = len(freq_hertz_result)
drop_rate = 0.1
reshaped = freq_hertz_result.reshape(-1, group_size) # (22, 10)
final_result = freq_check2(reshaped, drop_rate) # length의 10% 이하 빈도수 key값은 제외

print(final_result)