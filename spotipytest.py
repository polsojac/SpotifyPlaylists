import os
import sys
import json
import webbrowser
import spotipy

import spotipy.util as util
from json.decoder import JSONDecodeError

scope = "user-library-read user-library-modify user-read-private user-read-playback-state user-modify-playback-state"
#username = "spotify:user:12147979843"
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
print("Current song: " + current_song['item']['name'] + " by " + current_song['item']['artists'][0]['name'])
current_features = spotify.audio_features(current_song['item']['id'])
print(json.dumps(current_features, sort_keys=True, indent=4))
#recs = spotify.recommendations(seed_artists=[current_song['item']['artists'][0]['id']], seed_genres=['k-pop'], seed_tracks=[current_song['item']['id']])
#print(json.dumps(recs, sort_keys=True, indent=4))
#for rec in recs['tracks']:
    #print(rec['name'] + " by " + rec['artists'][0]['name']) 
    #+ " by " + rec['item']['artists'][0]['name'])
user = spotify.current_user()
#print(json.dumps(user, sort_keys=True, indent=4))
display_name = user['display_name']
followers = user['followers']['total']
all_tracks = []
for i in range(0,3):
    all_track_ids = spotify.current_user_saved_tracks(limit=50, offset=i*50)
    for tracks in all_track_ids['items']:
        track = tracks['track']
        artist_name = track['artists'][0]['name']
        search_results = spotify.search(artist_name, 1, 0, "artist")
        artist = search_results['artists']['items'][0]
        features = spotify.audio_features(track['id'])
        #print(json.dumps(features, sort_keys=True, indent=4))
        try:
            artist_genre = artist['genres'][0]
        except:
            artist_genre = "no genre found"
        all_tracks.append((track['id'], artist_genre))

'''while True:

    print("0 - Search for an artist")
    print("1 - Exit")
    print()
    choice = input("Your choice: ")

    if choice == "0":
        print('0')
        search = input("What is the artists name? ")
        print()

        search_results = spotify.search(search, 1, 0, "artist")
        #print(json.dumps(search_results, sort_keys=True, indent=4))
        
        # Artist details
        artist = search_results['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print(artist['genres'][0])
        print()
        #webbrowser.open(artist['images'][0]['url'])
        artist_ID = artist['id']
        # Album and track details
        trackURIs = []
        trackArt = []
        i = 0

        album_results = spotify.artist_albums(artist_ID)
        #print(json.dumps(album_results, sort_keys=True, indent=4))
        for album in album_results['items']:
            print("ALBUM " + album['name'])
            album_ID = album['id']
            album_art = album['images'][0]['url']

            track_results = spotify.album_tracks(album_ID)

            for song in track_results['items']:
                print(str(i)  + ": " + song['name'])
                trackURIs.append(song['uri'])
                trackArt.append(album_art)
                i += 1
            print()

        while True:
            song_select = input("Enter a song number to play the song or press x to exit: ")
            if song_select == 'x':
                break
            track_selection_list = []
            track_selection_list.append(trackURIs[int(song_select)])
            spotify.start_playback(device_ID, None, track_selection_list)
            #webbrowser.open(trackArt[int(song_select)])
    if choice == "1":
        break
'''
#print(json.dumps(user, sort_keys=True, indent=4))