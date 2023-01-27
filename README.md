# Lyrics_dataset_generator
- Framework of functions to automatically create large datasets with one line of code. 
- Sit back, relax, and keep your computer plugged in overnight and connected to the internet.
- Use make_dataset() to make a dataset and save_dataset() to download it to your computer. 
- Choose parameters to customize the output
  - topchart_type: songs, artists, or albums; Do you want to base the dataset on the top songs, artists, or albums?
  - genre: all, rap, rb, pop, rock, country; 
  - size: size of dataset , 1-10; Dataset size adjuster. 1: top 10 charts, 2: top 20 charts, ... , 10: top 100 charts
  - time: day, week, month, all_time; Top charts time period.
  - level: topchart, albums, discogrpahy. Do you want to the dataset to include only the top chart hits, or expand the dataset to add full albums of every topchart hit (topchart arguement must be either songs or albums), orr make a huge dataset by getting the N top songs in the artist's discography of every top chart hit? **This parameter may alter the dataset size more than the size parameter** 
         
         
NOTE: You first must obtain codes to access the API. Visit https://docs.genius.com/#/getting-started-h1 and follow the steps. To use this package you must have a .env file named 'tokens.env' stored in the same folder as the Lyrics_dataset_generator python file. In this .env store the codes you get -  client_id=#####, client_secret=#####, client_access_token=##### This is the site for the 'middle man' client made specifically for the Genius API https://lyricsgenius.readthedocs.io/en/master/
