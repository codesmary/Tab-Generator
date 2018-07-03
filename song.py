import re

class Song:
    def __init__(self, title, raw_tab):
        tab = self.generate_tab(raw_tab)
        if tab:
            self.valid = True
            self.tab = tab
            self.title = title
        else:
            self.valid = False
    
    def generate_tab(self, raw_tab):
        tab = []
        line = re.compile(r"^([ ]*([a-gA-GIiJjMmNnSsUu./\\#*1-9\[\]()][ ]*)+)\n([A-zÀ-ú0-9,:;''’\".()\-\?! ]+([ ]?\n){0,2})", re.MULTILINE)
        line_matches = line.finditer(raw_tab)
        match_len = 0
        for match in line_matches:
            chords = match.group(1) + '\n'
            words = match.group(3)
            if '\n' not in words:
                words += '\n'
            tab.append(chords)
            tab.append(words)
            match_len += len(match.group())

        tab_len = len(raw_tab)

        if tab_len == 0 or match_len/tab_len < 0.65:
            return None
        else:
            return ''.join(tab)

    def is_valid(self):
        return self.valid
    
    def get_song(self):
        return self.title + '\n' + self.tab + '\n'