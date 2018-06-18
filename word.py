class Word:
    #the chord string can possibly contain more than 1 chord
    def __init__(self, chord, word, pos = "na"):
        self.chord = chord
        self.word = word
        self.pos = pos

    def print(self):
        print('word:')
        if self.chord:
            print(self.chord)
        if self.word:
            print(self.word)
        if self.pos != 'na':
            print(self.pos)
