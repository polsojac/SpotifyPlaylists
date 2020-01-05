import os
import sys
import json
import spotipy

import spotipy.util as util
from json.decoder import JSONDecodeError

# The scope that authorizes what actions we can perform on our Spotify account
scope = "playlist-modify-public user-library-read user-library-modify user-read-private user-read-playback-state user-modify-playback-state"

'''with open("input_values.txt", "r") as f:
    username = f.readline()
    client_id = f.readline()
    client_secret = f.readline()
    redirect_uri = f.readline()
f.close()
'''
# my username = "spotify:user:12147979843"
username = sys.argv[1]
client_id = "1a0adb9a12784c23b25dbc8c96878cfc"
client_secret = "14f8767d4fe34cc8b28c5a8fa8eaca98"
redirect_uri = "https://localhost:8080"

token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

spotify = spotipy.Spotify(auth=token)

devices = spotify.devices()
#print(json.dumps(devices, sort_keys=True, indent=4))
device_ID = devices['devices'][0]['id']
current_song = spotify.current_user_playing_track()
#print(json.dumps(current_song, sort_keys=True, indent=4))
#print("Current song: " + current_song['item']['name'] + " by " + current_song['item']['artists'][0]['name'])
#current_features = spotify.audio_features(current_song['item']['id'])
#print(json.dumps(current_features, sort_keys=True, indent=4))
#recs = spotify.recommendations(seed_artists=[current_song['item']['artists'][0]['id']], seed_genres=['k-pop'], seed_tracks=[current_song['item']['id']])
#print(json.dumps(recs, sort_keys=True, indent=4))
#for rec in recs['tracks']:
    #print(rec['name'] + " by " + rec['artists'][0]['name']) 
    #+ " by " + rec['item']['artists'][0]['name'])
user = spotify.current_user()
#print(json.dumps(user, sort_keys=True, indent=4))
genre_dict = {}
for i in range(0,26):
    count = 0
    try:
        all_track_ids = spotify.current_user_saved_tracks(limit=50, offset=i*50)
        for tracks in all_track_ids['items']:
            count += 1
            track = tracks['track']
            artist_name = track['artists'][0]['name']
            search_results = spotify.search(artist_name, 1, 0, "artist")
            artist = search_results['artists']['items'][0]
            features = spotify.audio_features(track['id'])
            valence = features[0]['valence']

            # Spotify API has some errors where the genre isn't found in data
            try:
                artist_genre = artist['genres'][0]
            except:
                artist_genre = 'no genre found'

            if artist_genre == 'korean pop':
                artist_genre = 'k-pop'
            elif 'r&b' in artist_genre:
                artist_genre = 'r&b'
            elif 'edm' in artist_genre:
                artist_genre = 'edm'
            elif 'dubstep' in artist_genre:
                artist_genre = 'dubstep'
            elif 'hip-hop' in artist_genre:
                artist_genre = 'hip-hop'
            # Determines the "energy" of the song/ does a vibe check to see
            # what kind of song it is, very basic 2 options now, very rudimentary
            # Dropping this for now, too many genres
            '''if valence > .4:
                # valence above .4 ---> issa bop
                if artist_genre == 'k-pop':
                    artist_genre = 'k-bop'
                else:
                    artist_genre += " bop"
            #else:
                # otherwise ---> ballad
                artist_genre = artist_genre + ' ballad'
            '''
            # Again this is very very basic and straightforward
            if artist_genre not in genre_dict:
                genre_dict[artist_genre] = set()
            genre_dict[artist_genre].add(track['id'])
            if(track['id'] == '4fPBB44eDH71YohayI4eKV'):
                print("last song")

    except Exception as e:
        #print(e)
        print("-------------Your internet sucks----------------")
        # Tries again with the same set of songs
        # We go agane
        #i -= 1
print("All of your songs are now sorted by genre,")
print("They will now be converted into playlists")
for key in genre_dict.keys():

    # Creates new playlist
    new_playlist = spotify.user_playlist_create(user=12147979843, name=key, public=True, description="Spotipy generated " + key + " playlist")
    set_to_list = list(genre_dict[key])
    # If more than 100 songs need to be added to the playlist
    if len(genre_dict[key]) > 100:
        num = int(len(genre_dict[key]) / 100)
        for i in range(0, num + 1):
            small_list = set_to_list[100*i: 100*(i+1)]
            spotify.user_playlist_add_tracks(12147979843, new_playlist['uri'], small_list)

    else:
        spotify.user_playlist_add_tracks(12147979843, new_playlist['uri'], set_to_list)
print("Your songs have now been added to playlists")