import os
import sys
import json
import spotipy
from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

from spotipy import util
from spotipy.oauth2 import SpotifyOAuth
from json.decoder import JSONDecodeError

# Found on stackoverflow https://stackoverflow.com/questions/62618154/extract-text-from-specific-sections-in-html-python
def get_text(elements):
    text = ''
    for c in elements:
        for t in c.select('a, span'):
            t.unwrap()
        if c:
            c.smooth()
            text += c.get_text(strip=True, separator='\n')
    return text

def lyrics(song, artist):

    api_url = 'http://api.genius.com'
    search_url = api_url + '/search'
    querystring = {'q': song + ' ' + artist}
    headers = {'Authorization' : 'Bearer fualx5AGyuObRS1HmcwDcY8uxNY4EQHo61iKHRrYUDFFU8pSVzAF4tzX4xC8Lt7R'}
    response = requests.request('GET', search_url, headers=headers, params=querystring)
    json_response = response.json()
    artists = json_response['response']['hits']
    lyrics_url = ''
    for i in range(len(artists)):
        if artist.lower() in artists[i]['result']['artist_names'].lower() and song.lower() in artists[i]['result']['title'].lower():
            lyrics_url = artists[i]['result']['url']
            break
    try:
        page = requests.get(lyrics_url, headers=headers)
        html = BeautifulSoup(page.content, 'html.parser')

        lyrics = html.select('div[class^="Lyrics__Container"]')
        if lyrics:
            text = get_text(lyrics)
        else:
            text = get_text(soup.select('.lyrics'))

        filename = song.lower().replace(" ", "_") + '_' + artist.lower().replace(" ", "_") + '_lyrics.txt'
        
        with open(filename, 'w', encoding='utf8') as f:
            f.write(text)
    except:
        print(song + ' by ' + artist + ' could not be found.')
    return

    

def graphs(username):
    print('Do you want data from last week (W), month (M), or year (Y)?')
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
    else:
        print('You must pick between week, month, and year')
        return

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
                    date_added = tracks['added_at'][0:10].replace('-', '')
                    if not (date_added < date_limit):
                        date_reached = False
                        artist_name = track['artists'][0]['name']
                        search_results = spotify.search(artist_name, 1, 0, 'artist')
                        artist = search_results['artists']['items'][0]

                        # Spotify API has some errors where the genre isn't found in data
                        try:
                            artist_genre = artist['genres'][0]
                        except:
                            artist_genre = 'no genre found'
                        if (artist_genre + '/' + (date_added[4:6] + '-' + date_added[6:] + '-' + date_added[0:4])) not in genre_dict:
                            genre_dict[artist_genre + '/' + (date_added[4:6] + '-' + date_added[6:] + '-' + date_added[0:4])] = 1
                        genre_dict[artist_genre + '/' + (date_added[4:6] + '-' + date_added[6:] + '-' + date_added[0:4])] += 1
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
        plt.title('Distribution of Spotify Adds in Past Week')
    if choice == 'm' or choice == 'M':
        plt.title('Distribution of Spotify Adds in Past Month')
    if choice == 'y' or choice == 'Y':
        plt.title('Distribution of Spotify Adds in Past Year')
    plt.axis('equal')
    plt.show()
    return

def playlists(username):

    print('You can create up to 20 playlists based on either your short term taste, medium term taste, or long term taste. Which do you prefer?')
    print('1 - Short term')
    print('2 - Medium term')
    print('3 - Long term')
    print('Inputting anything else will put you back to the main menu')
    choice = input()
    if choice == '1':
        user_top_songs = spotify.current_user_top_tracks(time_range='short_term')
        print('You have selected short term')
    elif choice == '2':
        user_top_songs = spotify.current_user-top_tracks(time_range='medium_term')
        print('You have selected medium term')
    elif choice == '3':
        user_top_songs = spotify.current_user_top_tracks(time_range='long_term')
        print('You have selected long term')
    else:
        return
    print('Based on these top 20 songs, you will now generate a playlist based on recommendations for each song.')
    for song in user_top_songs['items']:
        # Creates new playlist
        recs = spotify.recommendations(seed_artists=[song['artists'][0]['id']], seed_tracks=[song['id']])
        new_playlist = spotify.user_playlist_create(user=username, name=song['name'] + ' recs', 
        public=True, description='Spotipy generated ' + song['name'] + ' recs' + ' playlist')
        for rec in recs['tracks']:
            spotify.user_playlist_add_tracks(username, new_playlist['uri'], [rec['uri']])
    print('Your songs have now been added to playlists')

    return


# The scope that authorizes what actions we can perform on our Spotify account
scope = 'playlist-modify-public user-library-read user-library-modify user-top-read user-read-private'

# my username = '12147979843'
username = sys.argv[1]
#client_id, client_secret, and redirect_url saved as ENV variables

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
song = ''
artist = ''
decision = '0'

while decision != 'X':
    print('what would you like to do?')
    print('1 - Generate playlists')
    print('2 - See graph of trends')
    print('3 - Get lyrics of a song of your choice')
    print('X - close program')
    choice = input()
    decision = choice
    if choice == '1':
        playlists(username)
    elif choice == '2':
        graphs(username)
    elif choice == '3':
        print('Would you like to find the lyrics for the song you are currently listening to? (Y or N)')
        response = input()
        if response == 'y' or response == 'Y':
            try:
                current_song = spotify.currently_playing()
                current_song_name = current_song['item']['name']
                current_song_artist = current_song['item']['artists'][0]['name']
            except:
                print('No song currently playing')
                break
            lyrics(current_song_name, current_song_artist)
        elif response == 'n' or response == 'N':
            print('What song do you want to find lyrics for?')
            song = input()
            print('Who is this song by?')
            artist = input()
            lyrics(song, artist)
        else:
            print('You must choose between Y and N, returning to main menu')