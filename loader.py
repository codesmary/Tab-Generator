import re
import string

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from nltk.corpus import stopwords, wordnet
import random
from random import shuffle

vocab = string.ascii_letters + string.digits + ' #()\n-'

def one_hot(s: str):
    if len(s) == 0:
        return torch.zeros((len(vocab), 0))
    return torch.as_tensor(np.array(list(s.lower()))[None, :] == np.array(list(vocab))[:, None]).float()


class SongDataset(Dataset):
    def __init__(self, corpus_path, max_len=250):
        with open(corpus_path) as file:
            corpus = file.read()
        dictionary = re.compile(r'[^%s]' % vocab)
        self.data = dictionary.sub('', corpus)
        line = re.compile(r'[^\n]+\n')
        if max_len is None:
            self.range = [(m.start(), m.end()) for m in line.finditer(self.data)]
        else:
            self.range = [(m.start(), m.start()+max_len) for m in line.finditer(self.data)]
            self.data += self.data[:max_len]
        self.data = one_hot(self.data)

    def __len__(self):
        return len(self.range)

    def __getitem__(self, idx):
        s, e = self.range[idx]
        if isinstance(self.data, str):
            return self.data[s:e]
        return self.data[:, s:e]

def load_data(dataset_path, max_len=250, num_workers=0, batch_size=128):
    dataset = SongDataset(dataset_path, max_len=max_len)
    return DataLoader(dataset, num_workers=num_workers, batch_size=batch_size, shuffle=True, drop_last=True)
