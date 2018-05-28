from song import Song

file = open("test_song.txt", "r")
lyrics = file.read()
file.close()
song = Song(lyrics)
