import pickle
import random
import tensorflow as tf
from os.path import join
import nltk
import collections
import unicodedata
import numpy as np

EOS = "<EOS>"
SOS = "<SOS>"
UNK = "<UNK>"
PAD = "<PAD>"
MAX_SENTS = 1000
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|\?|\.|\!')


def pretty_print(src_data, tar_data, index_to_vocab_in, index_to_vocab_out, translate=True):
    print("Pretty printing data, as reconstructed from idxs")
    if translate:
        for sentence_pair in zip(src_data, tar_data):
            [print(index_to_vocab_in[c], end=" ") for c in sentence_pair[0]]
            print("\t", end='')
            [print(index_to_vocab_out[c], end=" ") for c in sentence_pair[1]]
            print()
    else:
        for sentence_pair in zip(src_data, tar_data):
            [print(c, end=" ") for c in sentence_pair[0]]
            print("\t", end='')
            [print(c, end=" ") for c in sentence_pair[1]]
            print()


def flatten(l):
    for el in l:
        # for each element in l if its a list, recurse, otherwise, yield the element
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def unicode_to_ascii(s):
    # shamelessly stolen code from tensorflow.org to turn unicode (ugly, complicated) into ascii (clean, simple)
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')

def pad_sentences(sents):
    maxlen = len(max(sents, key=len))
    value = 0
    return np.array([sent + ([value]*(maxlen-len(sent))) for sent in sents])

def create_lexicon(lang_sents):
    """Given a list of words found in the text, returns 2 dictionaries mapping words to indices and back"""
    word_list = set(flatten(lang_sents))
    idx_to_word = dict(enumerate(word_list, 1))
    idx_to_word[0] = PAD
    print(f"Creating lexicons: first idx word is: {idx_to_word[0]}")
    print(f"Creating lexicons: last idx word is: {idx_to_word[len(idx_to_word)-1]}")
    # idx_to_word[len(word_list)] = UNK
    word_to_idx = dict(zip(idx_to_word.values(), idx_to_word.keys()))
    return word_to_idx, idx_to_word

def load_sentence_words(data_dir, text_file):
    """Load the text database as 2 list of lists, with each list in both of the list of lists being a tokenized
    sentence in either language (returns source, target), which correspond to each other by position"""
    with open(join(data_dir, text_file), "r", encoding='utf-8') as f:
        full_text = f.read().lower().split('\n')[:MAX_SENTS]
    print(f"Total number of sentences: {len(full_text)}")
    ascii_sents = [unicode_to_ascii(sent) for sent in full_text]
    tokenized = [[SOS] + tokenizer.tokenize(sent) + [EOS] for sent in ascii_sents]
    print(f"While loading string sentences, 10th sentence in {text_file} was {tokenized[10]}")
    return tokenized

class AttentionNMT(object):
    def __init__(self):
        self.src_to_idx = {}
        self.idx_to_src = {}
        self.tar_to_idx = {}
        self.idx_to_tar = {}
        self.src_size = 0
        self.tar_size = 0

        self.train_tar = []
        self.test_tar = []
        self.validate_tar = []
        self.train_src = []
        self.test_src = []
        self.validate_src = []

    def create_lexicon_wrapper(self, data_dir, src_sents, tar_sents):
        """For a given text file, creates 4 mappings, 2 for each language, from words to indices and back"""
        #src_sents, tar_sents = load_sentence_words(data_dir)
        self.src_to_idx, self.idx_to_src = create_lexicon(src_sents)
        self.tar_to_idx, self.idx_to_tar = create_lexicon(tar_sents)

    def load_sentences(self, data_dir):
        src_sents = load_sentence_words(data_dir, "src.txt")
        tar_sents = load_sentence_words(data_dir, "tar.txt")
        return src_sents, tar_sents

    def load_lexicons(self, data_dir):
        """Either load or create lexicons, in order to later turn tokenized sentences into lists of vectors, or to
        translate the network's output of numbers into comprehensible words and vice versa. Also returns loaded sentences turned into idxs"""
        src_sents, tar_sents = [], []
        try:
            with open(join(data_dir, "src_to_idx.pickle"), "rb") as p:
                self.src_to_idx = pickle.load(p)
            with open(join(data_dir, "idx_to_src.pickle"), "rb") as p:
                self.idx_to_src = pickle.load(p)
            with open(join(data_dir, "tar_to_idx.pickle"), "rb") as p:
                self.tar_to_idx = pickle.load(p)
            with open(join(data_dir, "idx_to_tar.pickle"), "rb") as p:
                self.idx_to_tar = pickle.load(p)
        except FileNotFoundError:
            src_sents, tar_sents = self.load_sentences(data_dir)
            self.create_lexicon_wrapper(data_dir, src_sents, tar_sents)
            with open(join(data_dir, "src_to_idx.pickle"), "wb") as p:
                pickle.dump(self.src_to_idx, p)
            with open(join(data_dir, "idx_to_src.pickle"), "wb") as p:
                pickle.dump(self.idx_to_src, p)
            with open(join(data_dir, "tar_to_idx.pickle"), "wb") as p:
                pickle.dump(self.tar_to_idx, p)
            with open(join(data_dir, "idx_to_tar.pickle"), "wb") as p:
                pickle.dump(self.idx_to_tar, p)
        self.src_size = len(self.src_to_idx)
        self.tar_size = len(self.tar_to_idx)
        print(f"Loaded source lexicon of size {self.src_size}")
        print(f"Loaded target lexicon of size {self.tar_size}")
        return src_sents, tar_sents

    def load_data(self, data_dir, test_size=0.01):
        """Load/create test and training sentences of indices that correspond to the lexicons"""
        try:
            with open(join(data_dir, "train_src.pickle"), "rb") as p:
                self.train_src = pickle.load(p)
            with open(join(data_dir, "test_src.pickle"), "rb") as p:
                self.test_src = pickle.load(p)
            with open(join(data_dir, "validate_src.pickle"), "rb") as p:
                self.validate_src = pickle.load(p)
            with open(join(data_dir, "train_tar.pickle"), "rb") as p:
                self.train_tar = pickle.load(p)
            with open(join(data_dir, "test_tar.pickle"), "rb") as p:
                self.test_tar = pickle.load(p)
            with open(join(data_dir, ".validate_tar.pickle"), "rb") as p:
                self.validate_tar = pickle.load(p)
            self.load_lexicons(data_dir)   # try loading pre-formatted training data, then lexicons to translate idxs -> english
        except FileNotFoundError:
            src_sents, tar_sents = self.load_lexicons(data_dir)   # training data not already generated, so load sentences and try loading lexicons
            if not src_sents:   # if lexicons already generated, but train sets not created, load sentences
                src_sents, tar_sents = self.load_sentences(data_dir)
            src_idxs = pad_sentences([[self.src_to_idx[w] for w in sent] for sent in src_sents])  # create training data from loaded sentence strings
            tar_idxs = pad_sentences([[self.tar_to_idx[w] for w in sent] for sent in tar_sents])
            self.train_src = src_idxs[:-int(2 * test_size * len(src_sents))]
            self.train_tar = tar_idxs[:-int(2 * test_size * len(src_sents))]
            self.test_src = src_idxs[-int(2 * test_size * len(src_sents)):-int(test_size * len(src_sents))]
            self.test_tar = tar_idxs[-int(2 * test_size * len(src_sents)):-int(test_size * len(src_sents))]
            self.validate_src = src_idxs[-int(test_size * len(src_sents)):]
            self.validate_tar = tar_idxs[-int(test_size * len(src_sents)):]
            with open(join(data_dir, "train_src.pickle"), "wb") as p:
                pickle.dump(self.train_src, p)
            with open(join(data_dir, "test_src.pickle"), "wb") as p:
                pickle.dump(self.test_src, p)
            with open(join(data_dir, "validate_src.pickle"), "wb") as p:
                pickle.dump(self.validate_src, p)
            with open(join(data_dir, "train_tar.pickle"), "wb") as p:
                pickle.dump(self.train_tar, p)
            with open(join(data_dir, "test_tar.pickle"), "wb") as p:
                pickle.dump(self.test_tar, p)
            with open(join(data_dir, "validate_tar.pickle"), "wb") as p:
                pickle.dump(self.validate_tar, p)
        print(f"Loaded {len(self.train_src) + len(self.test_src) + len(self.validate_src)} source and target sentence pairs.")
        pretty_print(self.test_src, self.test_tar, self.idx_to_src, self.idx_to_tar)

    def build_graph(self, hidden_size, layers_deep):
        self.hidden_size = hidden_size
        self.layers_deep = layers_deep
        self.enc_in = tf.placeholder(tf.uint32, [None, None])
        enc_hot = tf.one_hot(self.enc_in, self.eng_size, 1.0, 0.0)

        self.enc_state_in = tf.placeholder(tf.float32, [self.layers_deep, 2, None, self.hidden_size])
        enc_state = tf.unstack(self.enc_state_in, axis=0)

        enc_tuple_state = tuple([tf.nn.rnn_cell.LSTMStateTuple(enc_state[i][0], enc_state[i][1])
                                 for i in range(self.layers_deep)])
        cells = [tf.nn.rnn_cell.LSTMCell(num_units=self.hidden_size) for _ in range(self.layers_deep)]
        deep_cell = tf.nn.rnn_cell.MultiRNNCell(cells)
        o_, self.hidden_state = tf.nn.dynamic_rnn(deep_cell, enc_hot, initial_state=enc_tuple_state)

    def learn(self):
        pass

    def translate(self, sentence):
        pass




def main():
    fr = load_sentence_words("./datasets/fr-en", "src.txt")
    create_lexicon(fr)






if __name__ == "__main__":
    main()
