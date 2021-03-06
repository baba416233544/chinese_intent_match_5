import pickle as pk

import numpy as np

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from util import flat_read


embed_len = 200
max_vocab = 5000
seq_len = 30

path_word_vec = 'feat/word_vec.pkl'
path_word2ind = 'model/word2ind.pkl'
path_embed = 'feat/embed.pkl'


def embed(sents, path_word2ind, path_word_vec, path_embed):
    model = Tokenizer(num_words=max_vocab, filters='', char_level=True)
    model.fit_on_texts(sents)
    word_inds = model.word_index
    with open(path_word2ind, 'wb') as f:
        pk.dump(model, f)
    with open(path_word_vec, 'rb') as f:
        word_vecs = pk.load(f)
    vocab = word_vecs.vocab
    vocab_num = min(max_vocab, len(word_inds) + 1)
    embed_mat = np.zeros((vocab_num, embed_len))
    for word, ind in word_inds.items():
        if word in vocab:
            if ind < max_vocab:
                embed_mat[ind] = word_vecs[word]
    with open(path_embed, 'wb') as f:
        pk.dump(embed_mat, f)


def align(sents):
    with open(path_word2ind, 'rb') as f:
        model = pk.load(f)
    seqs = model.texts_to_sequences(sents)
    return pad_sequences(seqs, maxlen=seq_len)


def vectorize(path_data, path_sent, path_label, mode):
    sents = flat_read(path_data, 'text')
    labels = flat_read(path_data, 'label')
    if mode == 'train':
        embed(sents, path_word2ind, path_word_vec, path_embed)
    pad_seqs = align(sents)
    with open(path_sent, 'wb') as f:
        pk.dump(pad_seqs, f)
    with open(path_label, 'wb') as f:
        pk.dump(labels, f)


def vectorize_triple(path_data, path_triple):
    sents = flat_read(path_data, 'text')
    pos_sents = flat_read(path_data, 'pos')
    neg_sents = flat_read(path_data, 'neg')
    seqs = align(sents)
    pos_seqs = align(pos_sents)
    neg_seqs = align(neg_sents)
    triples = (seqs, pos_seqs, neg_seqs)
    with open(path_triple, 'wb') as f:
        pk.dump(triples, f)


if __name__ == '__main__':
    path_data = 'data/train.csv'
    path_sent = 'feat/sent_train.pkl'
    path_label = 'feat/label_train.pkl'
    vectorize(path_data, path_sent, path_label, 'train')
    path_data = 'data/test.csv'
    path_sent = 'feat/sent_test.pkl'
    path_label = 'feat/label_test.pkl'
    vectorize(path_data, path_sent, path_label, 'test')
    path_data = 'data/train_triple.csv'
    path_triple = 'feat/triple_train.pkl'
    vectorize_triple(path_data, path_triple)
    path_data = 'data/test_triple.csv'
    path_triple = 'feat/triple_test.pkl'
    vectorize_triple(path_data, path_triple)
