<<<<<<< HEAD
from tcn import load_model
import loader
import torch

def random_sampler(model, max_length):
    st = ''
    for i in range(max_length):
        prob = model.predict(st)
        ch = torch.distributions.Categorical(logits=prob).sample()
        new_char = loader.vocab[ch]
        print(new_char, end = '')
        st += new_char

if __name__ == "__main__":
    model = load_model()
    random_sampler(model, 500)
