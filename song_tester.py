from song import Song

file = open("Make_Out.txt", "r")
lyrics = file.read()
file.close()
song = Song(lyrics)
