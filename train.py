import torch
import torch.utils.tensorboard as tb
import torch.nn as nn
import torch.nn.functional as F
import argparse
from tcn import TCN, save_model
from loader import load_data
from os import path


def train(args):
    model = TCN()
    train_logger, valid_logger = None, None
    if args.log_dir is not None:
        train_logger = tb.SummaryWriter(path.join(args.log_dir, 'train'), flush_secs=1)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(args.learningrate), weight_decay=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min')
    loss = nn.CrossEntropyLoss()
    train_dataset = load_data('tab_corpus.txt')
    model.train()
    global_step=0
    for _ in range(int(args.iterations)):    
        for one_hot in train_dataset:
            print(global_step+1)
            input_batch = one_hot[:,:,:-1]
            batch_labels = one_hot.argmax(dim=1)
            output = model(input_batch)
            l = loss(output, batch_labels)
            train_logger.add_scalar('loss', l, global_step)
            optimizer.zero_grad()
            l.backward()
            optimizer.step()
            scheduler.step(l)
            global_step += 1

    model.eval()
    save_model(model)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_dir', default='log')
    parser.add_argument('--learningrate', default=.002)
    parser.add_argument('--iterations', default=100)
    args = parser.parse_args()

    train(args)
