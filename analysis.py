import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import pandas as pd
import librosa as rosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from constants import C_ID, C_SECRET

client_id = C_ID
client_secret = C_SECRET

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# result = sp.search("coldplay", limit=1, type="artist")
# pprint.pprint(result)

audio_features = sp.audio_features('spotify:track:39uLYYZytVUwcjgeYLI409')

print(pd.DataFrame(audio_features).transpose())