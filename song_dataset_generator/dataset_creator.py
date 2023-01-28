# Levi Davis, levijbdavis@gmail.com

import numpy as np
import pandas as pd
import os
import dotenv
import lyricsgenius
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import contractions
from nltk.stem import WordNetLemmatizer
import nltk
import copy

# Access the .env file to retrieve the access token to connect to the API
config = dotenv.dotenv_values("tokens.env")
client_access_token = config['client_access_token']
# api agent
genius = lyricsgenius.Genius(client_access_token)

class Dataset_generator():

    def __int__(self):

    # MAIN FUNCTION
    def make_dataset(topchart_type, level, genre='all', size=1, time='all_time'):
        '''
        Creates a dataset of song lyrics with Genius API using lyricgenius 
        input:
            - type: topcharts of 'songs', 'artists', or 'albums'
            - genre: 'all', 'rap', 'rb', 'pop', 'rock', 'country'
            - size: size of dataset , 1-10
            - time: 'day', 'week', 'month', 'all_time'
            - level: 'topchart', 'albums', 'discogrpahy'
        '''

        # Validate input arguements 
        try:
            topchart_type == ('songs' or 'artists' or 'albums')
        except:
            print("Please enter a valid type.")
            sys.exit(1)
        try:
            genre == ('all' or 'rap' or 'rb' or 'pop' or 'rock' or 'country')
        except:
            print("Please enter a valid genre.")
            sys.exit(1)
        try:
            (1 <= size and size <= 10)
        except:
            print("Please enter a valid size.")
            sys.exit(1)
        try:
            time == ('day' or 'week' or 'month' or 'all_time')
        except:
            print('Please enter a valid time.')
            sys.exit(1)

        if level=='topchart':
            try:
                topchart_type== ('songs')
            except:
                print('If level=songs then topchart_type must be songs.')
                sys.exit(1)

            TOPCHARTS = topchart_songs(time_period=time, genre=genre, n_per_page=size*5)
            DF = clean_lyrics(song_info(TOPCHARTS))
            return DF


        elif level=='albums':
            try:
                topchart_type== ('songs' or 'albums')
            except:
                print('If level=albums then topchart_type must be songs or albums.')
                sys.exit(1)

            if topchart_type=='albums':
                TOPCHARTS = topchart_albums(time_period=time, genre=genre, n_per_page=size*5)
                SONG_IDS = album_songs(TOPCHARTS)
                DF = clean_lyrics(song_info(SONG_IDS))
                return DF

            else:
                TOPCHARTS = topchart_songs(time_period=time, genre=genre, n_per_page=size*5)
                ALBUM_IDS = song_to_album(TOPCHARTS)
                SONG_IDS = album_songs(ALBUM_SONGS)
                DF = clean_lyrics(song_info(SONG_IDS))
                return DF


        else:   
            if topchart_type=='albums':
                TOPCHARTS = topchart_albums(time_period=time, genre=genre, n_per_page=size*5)
                ARTIST_IDS = album_to_artist(TOPCHARTS)
                SONG_IDS = discography(ARTIST_IDS)
                DF = clean_lyrics(song_info(SONG_IDS))
                return DF

            elif topchart_type=='artist':
                TOPCHARTS = topchart_artist(time_period=time, genre=genre, n_per_page=size*5)
                SONG_IDS = discography(TOPCHARTS)
                DF = clean_lyrics(song_info(SONG_IDS))
                return DF

            else:
                TOPCHARTS = topchart_songs(time_period=time, genre=genre, n_per_page=size*5)
                ARTIST_IDS = song_to_artist(TOPCHARTS)
                SONG_IDS = discography(ARTIST_IDS)
                DF = clean_lyrics(song_info(SONG_IDS))
                return DF


    # SAVE DATASET
    def save_dataset(dataset):
        # Path to current folder: ex. '/Users/user/Documents/music_project/'
        path = '/Users/ljd3frf/Documents/DS_music_project/'
        file_name = 'lyrics'
        dataset.to_csv(path+file_name+'.csv')

    # Background functions
    def topchart_songs(time_period='all_time',genre='all', n_per_page=5,pages=2):

    #  Purpose: Access the topcharts Genius API to retrieve songs
    #  Input:
    #    - time_period: time period ‘day’, ‘week’, ‘month’ or ‘all_time’
    #    - genre: ‘all’, ‘rap’, ‘pop’, ‘rb’, ‘rock’ or ‘country’
    #    - n_per_page: 1 - 50
    #    - pages: number of page number
    # Output: 
    #   list of song ids

        song_ids = list() # Lists to add to output data frame 

    # while-try loop because the request sometimes times out and will kill the loop

        for pn in range(1,pages+1):
            t = True
            while t == True:
                try:
                    songs = genius.charts(page=pages,time_period=time_period,
                                          chart_genre=genre,per_page=n_per_page,type_='songs')
                except:    
                    pass
                else:
                    t = False
                    n = len(songs['chart_items'])  # number of hits
                    # get song ids
                    for song in range(0,n):
                        song_id = songs['chart_items'][song]['item']['id']
                        song_ids.append(song_id)


        return song_ids


    def topchart_albums(time_period='all_time',genre='all', n_per_page=5,pages=2):

    #  Purpose: Access the topcharts Genius API to retrieve albums
    #    - Results vary, but size is less than 200
    #  Input:
    #    - time_period: time period ‘day’, ‘week’, ‘month’ or ‘all_time’
    #    - genre: ‘all’, ‘rap’, ‘pop’, ‘rb’, ‘rock’ or ‘country’
    #    - n_per_page: 1 - 50
    #    - pages: number of page number
    # Output: 
    #   list of album ids

        album_ids = list() # Lists to add to output data frame 

    # while-try loop because the request sometimes times out and will kill the loop

        for pn in range(1,pages+1):
            t = True
            while t == True:
                try:
                    albums = genius.charts(page=pages,time_period=time_period,
                                          chart_genre=genre,per_page=n_per_page,type_='albums')
                except:    
                    pass
                else:
                    t = False
                    n = len(albums['chart_items'])  # number of hits
                    # get album ids
                    for album in range(0,n):
                        album_id = albums['chart_items'][album]['item']['id']
                        album_ids.append(album_id)


        return album_ids


    def topchart_artists(time_period='all_time',genre='all', n_per_page=5,pages=2):

    #  Purpose: Access the topcharts Genius API to retrieve albums
    #    - Results vary, but size is less than 200
    #  Input:
    #    - time_period: time period ‘day’, ‘week’, ‘month’ or ‘all_time’
    #    - genre: ‘all’, ‘rap’, ‘pop’, ‘rb’, ‘rock’ or ‘country’
    #    - n_per_page: 1 - 50
    #    - pages: number of page number
    # Output: 
    #   list of album ids

        artist_ids = list() # Lists to add to output data frame 

    # while-try loop because the request sometimes times out and will kill the loop

        for pn in range(1,pages+1):
            t = True
            while t == True:
                try:
                    artists = genius.charts(page=pages,time_period=time_period,
                                          chart_genre=genre,per_page=n_per_page,type_='artists')
                except:    
                    pass
                else:
                    t = False
                    n = len(artists['chart_items'])  # number of hits
                    # get album ids
                    for artist in range(0,n):
                        artist_id = artists['chart_items'][artist]['item']['id']
                        artist_ids.append(artist_id)


        return artist_ids


    def song_info(ids):

        # Input: dataframe with song_id as a column
        # Output: dataframe with song ids, artist names, lyrics, song titles.

        lyrics = list()         
        titles = list()         
        artists = list()
        artist_ids = list()
        albums = list()
        album_ids = list()
        new_song_ids = list()

        # Access Genius API for each song_id
        # The try/except/pass code is to protect the dataset creation from being
        # terminated if there is a problem with any API call
        for song in ids:
            t = True
            while t == True:
                try:
                    a = genius.search_song(song_id=song) # get lyrics
                    b = genius.song(song_id=song) # get album
                except:    
                    pass
                else:
                    t = False
                    if a and a.to_text()!=None:
                        if b['song']['album'] != None:
                            album = b['song']['album']['name']
                            album_id = b['song']['album']['id']
                        else:
                            album = 'single'
                            album_id = 'NA'
                        artist_id = b['song']['primary_artist']['id']
                        albums.append(album)
                        lyrics.append(a.to_text())
                        titles.append(a.title)
                        artists.append(a.artist)
                        new_song_ids.append(a.id)
                        artist_ids.append(artist_id)
                        album_ids.append(album_id)


        # output data frame                                   
        song_df = pd.DataFrame({
            'Song Title': titles,
            'Artist': artists,
            'Album': albums,
            'Lyrics': lyrics,
            'Song ID': new_song_ids,
            'Artist ID': artist_ids,
            'Album ID': album_ids})

        return song_df


    def song_to_album(song_ids):
      # Takes in a list of song ids and return a list of every song in each on the input songs' album

        album_ids = []
        for song in song_ids:
            t = True
            while t == True:
                try:
                    # Search song API with parameters
                    song_info = genius.song(song)
                except:    
                    pass
                else:
                    t = False
                    if song_info['song']['album'] != None:
                        album_id = song_info['song']['album']['id']
                        album_ids.append(album_id)

        return_list = list(set(album_ids)) # removes duplicates

        return return_list


    def album_songs(ids):
        # takes in a list of album ids and returns a combined list of songs ids from each album

        song_ids =[]

        for album_id in ids:
            t = True
            while t == True:
                try:
                    # Search song API with parameters
                    album_dict = genius.album_tracks(album_id)
                except:    
                    pass
                else:
                    t = False
                    len_album = len(album_dict['tracks'])
                    for track in range(len_album):
                        song_id = album_dict['tracks'][track]['song']['id']
                        song_ids.append(song_id)

        return_list = list(set(song_ids)) # removes duplicates

        return return_list


    def song_to_artist(song_ids):
      # Takes in a list of song ids and returns a list of artist ids

        artist_ids = []

        for song in song_ids:
            t = True
            while t == True:
                try:
                    # Search song API with parameters
                    song_info = genius.song(song)
                except:    
                    pass
                else:
                    t = False
                    if song_info['song']['primary_artist']['id'] != None:
                        artist_id = song_info['song']['primary_artist']['id']
                        artist_ids.append(artist_id)

        return_list = list(set(artist_ids)) # removes duplicates

        return return_list


    def discography(ids):
        # takes in a list of artist ids and returns a single list of combined discographies

        song_ids = []
        for sid in ids:
            page = 1
            while page:
                try:
                    request = genius.artist_songs(sid,
                                              sort='popularity',
                                              per_page=50,
                                              page=page)            
                except:    
                    pass
                else:
                    discog = request['songs']
                    for song in discog:
                        song_id = song['id']
                        song_ids.append(song['id'])

                    page = request['next_page']

        return_list = list(set(song_ids)) # removes duplicates

        return return_list


    def album_to_artist(ids):
        #takes in a list of album ids and returns a list of artist ids

        artist_ids =[]

        for album_id in ids:
            t = True
            while t == True:
                try:
                    # Search song API with parameters
                    album_dict = genius.album(album_id)
                except:    
                    pass
                else:
                    t = False
                    print(album_dict['album']['artist']['id'])
                    artist_id = album_dict['album']['artist']['id']
                    artist_ids.append(artist_id)

        return_list = list(set(artist_ids)) # removes duplicates

        return return_list

    # Pre-process text
    def clean_lyrics(df):

        # Performs various text pre-processing steps
        # Input: Data frame with a column named 'lyrics'
        # Output: Same dataframe but with pre-processed text

        df1 = copy.deepcopy(df)
        lyrics = df1.Lyrics
        lyrics_final = list()

        wnl = WordNetLemmatizer()

        for lyric in lyrics:
            # Removes brackets and text inside
            song_lyrics = re.sub(r'\[.*?\]', '', lyric)      
            # Removes parentheses and text inside
            song_lyrics = re.sub(r'\(.*?\)', '',song_lyrics)    
            # Finds start of lyrics
            song_lyrics = song_lyrics[song_lyrics.find('Lyrics')+6:] 
            # Removes newlin char (\n)
            song_lyrics = re.sub("\n"," ",song_lyrics)          
            # Removes leftover backslahes 
            song_lyrics = re.sub('\'', "plac3h0ler",song_lyrics)    
            # Removes leftover backslahes 
            song_lyrics = re.sub('plac3h0ler', r"'",song_lyrics)  
            # Removes text at the end of doc
            song_lyrics = re.sub(".{3}Embed", "",song_lyrics)         
            # Lengthes contractions to full form
            song_lyrics = contractions.fix(song_lyrics)               
            # Removes punctuation
            song_lyrics = re.sub(r'[^\w\s]','',song_lyrics)   
            # Removes numbers
            song_lyrics = re.sub("[^a-zA-Z]+", " ",song_lyrics)  
            # Tokenize words
            word_tokens = word_tokenize(song_lyrics)
            # Lemmatize words
            lemma_words_tokens = [wnl.lemmatize(token) for token in word_tokens]    

            # stopwords 
            stop_words = stopwords.words('english')  
            sw = ['ayy', 'like', 'come', 'yeah', 'got', 'la', 'ya',
                  'oh', 'ooh', 'huh', 'whooaaaaa', 'o', 'n', 'x']
            explict_words = ['nigga', 'nigger', 'bitch', 'bitchin', 'fag', 'faggot',
                             'fuck', 'fucked', 'fuckin', 'motherfucker', 'motherfuckin',
                             'pussy', 'dick', 'cock', 'whore','shit', 'shittin']
            stop_words_final = stop_words + sw + explict_words


            # Remove stopwords, filters the lyrics

            #filtered_lyrics = [token.lower() for token in lemma_words_tokens if 
                #  token.lower() not in stop_words_final] 

            filtered_lyrics = [token.lower() for token in lemma_words_tokens]


            # Join lyrics into one string
            lyrics_joined = ' '.join(filtered_lyrics).lower()

            lyrics_final.append(lyrics_joined)

        df1 = df1.drop(['Lyrics'], axis=1)
        df1['Lyrics'] = lyrics_final

        return df1