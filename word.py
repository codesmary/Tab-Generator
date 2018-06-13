class Word:
    #the chord string can possibly contain more than 1 chord
    def __init__(self, chord, word, pos = "na"):
        self.chord = chord
        self.word = word
        self.pos = pos

    def has_chord(self):
        return chord != None
