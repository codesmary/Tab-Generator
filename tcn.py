import torch
import torch.nn.functional as F
import loader
from torch.nn.utils import weight_norm
from os import path

class TCN(torch.nn.Module):
    class CausalBlock(torch.nn.Module):
        def __init__(self, in_channels, out_channels, kernel_size, dilation):
            super().__init__()
            self.network = torch.nn.Sequential(
                torch.nn.ConstantPad1d((2*dilation,0),0),
                weight_norm(torch.nn.Conv1d(in_channels, out_channels, kernel_size, dilation=dilation)),
                torch.nn.LeakyReLU(),
                torch.nn.Dropout(0.1),
                torch.nn.ConstantPad1d((2*dilation,0),0),
                weight_norm(torch.nn.Conv1d(out_channels, out_channels, kernel_size, dilation=dilation)),
                torch.nn.LeakyReLU(),
                torch.nn.Dropout(0.1)
            )
            self.resize = torch.nn.Conv1d(in_channels, out_channels, 1)
            self.relu = torch.nn.LeakyReLU()

        def forward(self, x):
            residual = x
            x = self.network(x)
            residual = self.resize(residual)
            return self.relu(x + residual)

    def __init__(self, layers=[600,600]):
        super().__init__()
        c = len(loader.vocab)
        L = []
        total_dilation = 1
        for l in layers:
            L.append(self.CausalBlock(c, l, 3, total_dilation))
            total_dilation *= 2
            c = l
        self.network = torch.nn.Sequential(*L)
        self.classifier = torch.nn.Conv1d(c, len(loader.vocab), 1)

    def forward(self, x):
        x = F.pad(x, (1, 0), 'constant', 0)
        x = self.network(x)
        x = self.classifier(x)
        return x

    def predict(self, some_text):
        x = loader.one_hot(some_text)[None,:,:]
        out = self.forward(x)
        ll = out.log_softmax(1)[0,:,:]
        return ll[:, -1]


def save_model(model):
    return torch.save(model.state_dict(), path.join(path.dirname(path.abspath(__file__)), 'tcn.th'))


def load_model():
    model = TCN()
    model.load_state_dict(torch.load(path.join(path.dirname(path.abspath(__file__)), 'tcn.th'), map_location='cpu'))
    return model
