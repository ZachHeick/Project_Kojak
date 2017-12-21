# Mix Retriever: A Hip-Hop Playlist Generator   
### Project 5 of Metis Data Science Bootcamp 

For the fifth and final project at Metis, we were given the freedom to solve any problem we were interested using any of the data science techniques and technologies we've learned from the bootcamp. My favorite topics covered were NLP and recommendation systems, and I wanted to find a problem that can be solved with techniques from these topics.  

### The Problem  

I love discovering new music, especially when it comes to Hip-Hop. Today, music streaming platforms offer thousands of dynamic playlists for finding new music that cover topics such as specific artists, genres, time of year, and many more. What if we can't find a playlist built around a particular song that we like? We could look for a playlist someone else already made, or we could use an existing playlist generator. These existing playlist generators prioritize artists and genres, as well as looking at similar songs others have listened to. Some things that might not be prioritized or included at all in these playlist generators are the lyrical meanings between songs in a playlist and the overall "mood" of the playlist. Lyrical similarities between songs paired with a similar mood can make playlists much more cohesive and personal.  

### My Solution  

To combine the functionality of individual song-based playlist generators with a focus on making content based recommendations, I created a web app called "Mix Retriever" that builds a hip-hop playlist of songs with similar lyrical meaning and mood.

---  

Listed below in cronological order are the folders containing code for this project. I collected my data from various sources, trained a Song2vec model on AWS, and added in other features to get the recommended playlist. I then built a web app that utilizes this recommendation system.  

`Data_Collection`  

  1. `Database_Schemas.md`  
  2. `Get_Artists.ipynb`  
  3. `Get_Tracks.py`  
  4. `Get_Lyrics.ipynb`  
  5. `Upload_to_S3.ipynb`  


`Pipeline`  

  1. `Train_Song2vec.py`  
  2. `Pipeline.ipynb`  


`Web_App` contains files for [Mix Retriever](http://www.mixretriever.com/).  

The blog post can be found here.
