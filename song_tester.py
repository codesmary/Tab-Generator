from song import Song

file = open("Idle_Town.txt", "r")
lyrics = file.read()
file.close()
song = Song(lyrics)
