import os
import sys
import json
import spotipy
from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import spotipy.util as util
from json.decoder import JSONDecodeError


#print(json.dumps(user, sort_keys=True, indent=4))

def graphs():
    print("Do you want data from last week (W), month (M), or year (Y)?")
    choice = input()
    today = date.today()
    if choice == 'W' or choice == 'w':
        # Last week data
        weekday = today.weekday()
        start_delta = timedelta(days=weekday,weeks=1)
        date_limit = today - start_delta
    elif choice == 'M' or choice == 'm':
        # Last month data
        weekday = today.weekday()
        start_delta = timedelta(days=weekday,weeks=4)
        date_limit = today - start_delta
    elif choice == 'Y' or choice == 'y':
        # Last year data
        weekday = today.weekday()
        start_delta = timedelta(days=weekday,weeks=52)
        date_limit = today - start_delta
    date_limit = str(date_limit).replace('-', "")
    genre_dict = {}
    date_reached = False
    for i in range(0, 26):
        count = 0
        if not date_reached:
            all_track_ids = spotify.current_user_saved_tracks(limit=50, offset=i*50)
            for tracks in all_track_ids['items']:
                    # Parse date added info 
                    count += 1
                    track = tracks['track']
                    date_added = tracks['added_at'][0:10].replace('-', "")
                    if not (date_added < date_limit):
                        date_reached = False
                        artist_name = track['artists'][0]['name']
                        search_results = spotify.search(artist_name, 1, 0, "artist")
                        artist = search_results['artists']['items'][0]

                        # Spotify API has some errors where the genre isn't found in data
                        try:
                            artist_genre = artist['genres'][0]
                        except:
                            artist_genre = 'no genre found'
                        if (artist_genre + "/" + (date_added[4:6] + '-' + date_added[6:] + '-' + date_added[0:4])) not in genre_dict:
                            genre_dict[artist_genre + "/" + (date_added[4:6] + '-' + date_added[6:] + '-' + date_added[0:4])] = 1
                        genre_dict[artist_genre + "/" + (date_added[4:6] + '-' + date_added[6:] + '-' + date_added[0:4])] += 1
                    else: 
                        date_reached = True
                        break
        else:
            break

    graph_dict = {}
    set_of_dates = set()
    for key in genre_dict:
        splitter = key.find('/')
        genre = key[0:splitter]
        day = key[splitter + 1:]
        # Put the values into a dictionary of lists
        if genre not in graph_dict:
            graph_dict[genre] = []
        graph_dict[genre].append((genre_dict[key], day))
        set_of_dates.add(day)
        
        #plt.plot(day, genre_dict[key],label=genre)
    labels = set()
    big_sum = 0
    for genre in graph_dict:
        length = len(graph_dict[genre])
        for i in range(length):
            big_sum += graph_dict[genre][i][0]

    for genre in graph_dict:
        length = len(graph_dict[genre])
        sum = 0
        for i in range(length):
            sum += graph_dict[genre][i][0]
        labels.add((100 * (sum / big_sum), genre))
    labels_list = list(labels)
    labels_list.sort()
    explode= []
    for i in range(len(labels_list) - 1):
        explode.append(0)
    explode.insert(0, 0.1)
    values = []
    labels = []
    for i in range(len(labels_list)):
        values.append(labels_list[i][0])
        labels.append(labels_list[i][1])
    
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    if choice == 'w' or choice == 'W':
        plt.title("Distribution of Spotify Adds in Past Week")
    if choice == 'm' or choice == 'M':
        plt.title("Distribution of Spotify Adds in Past Month")
    if choice == 'y' or choice == 'Y':
        plt.title("Distribution of Spotify Adds in Past Year")
    plt.axis('equal')
    plt.show()
def playlists():
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
#current_song = spotify.current_user_playing_track()
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
print("what would you like to do?")
print("1. Generate playlists")
print("2. See graph of trends")
choice = input()
if choice == '1':
    playlists()
if choice == '2':
    graphs()