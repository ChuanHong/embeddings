import torch
import torch.autograd as autograd
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import numpy as np
import json
from gensim.models import FastText
import logging
import sys
import matplotlib.pyplot as plt

from Encoder import DescriptionEncoder

torch.manual_seed(1)

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO


def create_mappings():
    """
    Input to an LSTM must be a 3D tensor. For that, I
    am reading all the descriptions line by line and
    storing their embeddings row wise into a numpy
    array of 3 dimensions and shape (batch_size, seq_len, embed_size).
    """
    count = 0
    saved_model = 'model/entity_fasttext_n100'
    descriptions_file = 'data/abstracts.json'
    model = FastText.load(saved_model)
    wv = model.wv
    del model

    # Fixed shape for the input layer of the lstm network.
    shape = (500, 100)
    entities = []
    abstracts = []
    lines = []
    with open(descriptions_file, 'r') as input_file:
        logging.info('mapping the resources and their descriptions')
        for line in input_file:
            if count % 1000 == 0:
                logging.info('reading resource # {0}'.format(count))

            # Read the entire dictionary in first pass
            json_line = json.loads(line)
            lines.append(json_line)
            count += 1

    for l in lines:
        ent = [_ for _ in l.keys()][0]
        desc = l[ent].split()
        try:
            d = np.array(list(map(lambda x: wv.get_vector(x), desc)),
                         dtype=np.float32)
            e = np.array(wv.get_vector(ent), dtype=np.float32)
            entities.append(e)
            abstracts.append(d)
        except (IndexError, KeyError) as _:
            continue

    # logging.info('resources read into np stack : {0}'.format(count))
    # entities = list(map(lambda x: [_ for _ in x.keys()][0], lines))
    # abstracts = [l[ent] for l, ent in zip(lines, entities)]
    # entities = [np.array(wv.get_vector(ent),
    #                      dtype=np.float32) for ent in entities]
    # abstracts = [np.array(list(map(lambda x: wv.get_vector(x),
    #                                desc.split())),
    #                       dtype=np.float32) for desc in abstracts]

    logging.info(f'{len(abstracts)} mappings generated')

    return abstracts, entities, wv


def load_tensors(directory):
    """
    Input to an LSTM must be a 3D tensor. For that, I
    am reading all the descriptions line by line and
    storing their embeddings row wise into a numpy
    array of 3 dimensions and shape (n, 200, 100).
    """
    logging.info('loading saved embeddings')
    X = np.load(directory + '/description.npy')
    y = np.load(directory + '/entity.npy')
    logging.info('loaded {0} saved embeddings'.format(len(X)))
    train(X, y)


def train(x, y, wv):
    """
    This method takes the inputs, and the labels
    and trains the LSTM network to predict the
    embeddings based on the input sequnce.

    Arguments
    ---------
    x : List of input descriptions
    y : List of target entity embeddings
    wv : Keyed Word Vectors for pre-trained embeddings
    """
    epochs = 15
    embed_size = 100
    hidden_size = 50
    seq_len = 1
    num_layers = 2
    model = DescriptionEncoder(embed_size, hidden_size, seq_len, num_layers)
    inputs = x
    labels = y
    itr = len(inputs)
    progress = 0.0
    criterion = nn.CosineEmbeddingLoss()
    # criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.4)
    count = 0
    itr_p = 0.0
    losses = np.zeros(epochs)
    logging.info('training on {0} samples'.format(itr))
    for epoch in range(epochs):
        logging.info(
            'starting epoch {0}'.format(epoch + 1))
        flags = Variable(torch.ones(1))
        count = 0
        hidden = model.init_hidden()
        for i, l in zip(inputs, labels):
            count += 1
            progress = (count / itr) * 100
            print('INFO : PROGRESS : {0:.1f} %'.format(progress), end='\r')
            for word in i:
                output, hidden = model(
                    Variable(torch.tensor([[word]])))
            optimizer.zero_grad()
            # loss = criterion(output[0][0],
            #                  Variable(torch.tensor(l)))
            loss = criterion(output[0],
                             Variable(torch.tensor([l])),
                             flags)
            loss.backward(retain_graph=True)
            # loss.backward()
            optimizer.step()
        logging.info(
            'completed epoch {0}, loss : {1}'.format(epoch + 1, loss.item()))
        losses[epoch] = loss.item()
    logging.info('saving the model to model/description_encoder')
    torch.save(model, 'model/description_encoder')
    validate(model, wv)
    # plt.plot(losses)
    # plt.title('Model Loss')
    # plt.ylabel('loss')
    # plt.xlabel('epoch')
    # plt.show()


def validate(model, wv):
    shape = (500, 100)

    with open('data/abstracts.json', 'r') as input_file:
        with open('data/validate', 'w+') as output_file:
            for line in input_file:
                # line = next(input_file)
                json_line = json.loads(line)
                target = [_ for _ in json_line.keys()][0]
                desc = json_line[target].split()
                try:
                    r = np.array(list(map(lambda x: wv.get_vector(x), desc)),
                                 dtype=np.float32)
                except KeyError:
                    continue
                for word in r:
                    try:
                        p, hidden = model(Variable(torch.tensor([[word]])))
                    except TypeError:
                        continue
                p = p[0][0].detach().numpy()
                print('Entity : ' + target)
                print('Predicted : ', end='')
                print(wv.similar_by_vector(p))
                output_file.write(target + '\n')
                output_file.write(str(wv.similar_by_vector(p)) + '\n')


if __name__ == '__main__':
    x, y, wv = create_mappings()
    train(x, y, wv)
