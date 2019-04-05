import tensorflow as tf
import numpy as np
import os
import pickle
import math


class DeepLSTM(object):
    def __init__(self, hidden_state_size, layers_deep, test_batch_size=256, log_path=None, save_loc=None):
        self.hidden_state_size = hidden_state_size
        self.layers_deep = layers_deep
        self.save_loc = save_loc
        self.log_path = log_path
        self.test_batch_size = test_batch_size

    def build_graph(self):
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)
        with self.graph.as_default():
            self.x_in = tf.placeholder(tf.uint8, [None, None], name='x_in')  # [batch_size, seq_len]
            self.y_in = tf.placeholder(tf.uint8, [None, None], name='y_in')
            self.eta_initial = tf.placeholder(tf.float32)
            self.tr_step = tf.placeholder(tf.int32)
            self.pkeep = tf.placeholder(tf.float32)
            self.this_batch_size = tf.placeholder(tf.int32, [])
            self.decay = tf.placeholder(tf.float32)
            self.state_placeholder = tf.placeholder(tf.float32, [self.layers_deep, 2, None, self.hidden_state_size])

            x_hot = tf.one_hot(self.x_in, self.vocab_size, 1.0, 0.0)  # [batch_size, seq_len * vocab_size]
            y_hot = tf.one_hot(self.y_in, self.vocab_size, 1.0, 0.0)
            y_label = tf.reshape(y_hot, [self.test_batch_size, -1, self.vocab_size], name='y_label')
            self.global_step_tensor = tf.Variable(0, trainable=False, name='global_step')
            l = tf.unstack(self.state_placeholder, axis=0)
            lstm_tuple_state = tuple([tf.nn.rnn_cell.LSTMStateTuple(l[i][0], l[i][1]) for i in range(self.layers_deep)])
            eta = tf.add(1e-10, tf.train.exponential_decay(self.eta_initial, self.tr_step, self.decay, 1 / math.e),
                         name='eta')

            self.W_yh = tf.Variable(tf.truncated_normal([self.hidden_state_size, self.vocab_size], stddev=0.1),
                                    name='W_yh')
            self.B_y = tf.Variable(tf.constant(0.1, shape=[self.vocab_size]))

            self.cells = [tf.nn.rnn_cell.DropoutWrapper(cell=tf.nn.rnn_cell.LSTMCell(num_units=self.hidden_state_size),
                                                        output_keep_prob=self.pkeep) for _ in range(self.layers_deep)]
            self.deep_cell = tf.nn.rnn_cell.MultiRNNCell(self.cells)
            self.outputs, self.hidden_state = tf.nn.dynamic_rnn(self.deep_cell, x_hot, initial_state=lstm_tuple_state)

            self.output_shaped = tf.reshape(self.outputs, [-1, self.hidden_state_size])
            self.y_logits = tf.add(tf.matmul(self.output_shaped, self.W_yh), self.B_y)
            self.p_out = tf.nn.softmax(tf.cast(self.y_logits, tf.float64),
                                       name='p_out')  # [batch_size, seq_len * vocab_size]

            self.loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.y_logits, labels=y_hot))
            self.opt = tf.train.AdamOptimizer(eta).minimize(self.loss, global_step=self.global_step_tensor)

            self.predictions = tf.argmax(self.p_out, 1, name='predictions')  # [batch_size * seq_len]
            self.test_predictions = tf.reshape(self.predictions, [self.test_batch_size, -1], name='test_predictions')

            self.correct_num = tf.equal(self.test_predictions, tf.argmax(y_label, 2))
            self.accuracy = tf.reduce_mean(tf.cast(self.correct_num, tf.float32), name='accuracy')

            acc_sum = tf.summary.scalar('accuracy', self.accuracy)
            test_loss_sum = tf.summary.scalar('loss', self.loss)
            self.test_summary = tf.summary.merge([acc_sum, test_loss_sum])

            self.saver = tf.train.Saver()
            self.loader = tf.train.Saver()
            if self.log_path is not None:
                self.writer = tf.summary.FileWriter(self.log_path + "/test")  # create a writer
                self.writer2 = tf.summary.FileWriter(self.log_path + "/tr")
            self.sess.run(tf.global_variables_initializer())
            try:
                self.loader.restore(self.sess, tf.train.latest_checkpoint(self.save_loc))
            except ValueError:
                print("No models found, initializing random model...")

    def text_in(self, dataset_path, file_name, test_size=0.02):
        """Best practice to put the text file in its own directory"""
        with open(os.path.join(dataset_path, file_name), 'r', encoding='utf-8') as f:
            raw_data = f.read()
            print("Database size: {} characters".format(len(raw_data)))
        try:
            with open(os.path.join(dataset_path, 'char_set.pickle'), 'rb') as p:
                vocab = pickle.load(p)
        except FileNotFoundError:
            vocab = list(set(raw_data))
            with open(os.path.join(dataset_path, 'char_set.pickle'), 'wb') as p:
                pickle.dump(vocab, p)
        self.vocab_size = len(vocab)
        self.index_to_vocab = dict(enumerate(vocab))
        self.vocab_to_index = dict(zip(self.index_to_vocab.values(), self.index_to_vocab.keys()))

        all_data = [self.vocab_to_index[i] for i in raw_data]
        train_index = int(len(raw_data) * (1 - (test_size * 2)))
        test_index = int(len(raw_data) * test_size)
        self.train_data = all_data[:train_index]
        self.test_data = all_data[train_index:train_index + test_index]
        self.validation_data = all_data[train_index + test_index:]
        # self.validation_data = all_data[-10000:]
        del raw_data  # clear some RAM, completely unnecessary

    def predict(self, file_in, chars_after=15000):
        with open(file_in, "r") as f:
            full_chars = f.read()
            idx_chars = [self.vocab_to_index[i] for i in full_chars]
        text_gen = [idx_chars]
        hidden_gen = np.zeros((self.layers_deep, 2, 1, self.hidden_state_size))
        hidden_gen = self.sess.run(self.hidden_state, feed_dict={self.x_in: text_gen, self.pkeep: 1.0,
                                                                 self.this_batch_size: len(idx_chars),
                                                                 self.state_placeholder: hidden_gen})
        for j in range(chars_after):
            p_o, hidden_gen = self.sess.run([self.p_out, self.hidden_state],
                                            feed_dict={self.x_in: [[text_gen[0][-1]]], self.pkeep: 1.0,
                                                       self.this_batch_size: 1,
                                                       self.state_placeholder: hidden_gen})
            next_char = np.argmax(np.random.multinomial(1, p_o[0]))
            text_gen[0].append(next_char)
        new_text = [self.index_to_vocab[char] for char in text_gen[0]]
        with open(file_in[:-4] + "_extended.txt", 'w', encoding='utf-8') as f:
            f.write(''.join(new_text))
        print('created text file')

    def SGD(self, testing_data, max_bad_run_length=2, seq_len=50, gen_char="T", train_batch_size=32,
            test_batch_size=256, epochs=10, gen_len=2000, dropout_rate=0.5, eta_initial=2e-3):
        tensorboard_str = 'tensorboard --logdir=test:{0}/test,train:{0}/tr --host=localhost --port=6007'.format(
            self.log_path)
        print(f"Run '{tensorboard_str}' in command prompt and then follow the directions to watch your model train")
        test_size = len(testing_data)
        gen_char = self.vocab_to_index[gen_char]
        accs = [0]
        bad_run_length = 0

        for idx, epoch in enumerate(gen_epochs(self.train_data, train_batch_size, epochs, seq_len)):
            train_loss = 0
            counter = 0
            hidden_train = np.zeros((self.layers_deep, 2, train_batch_size, self.hidden_state_size))
            hidden_test = np.zeros((self.layers_deep, 2, test_batch_size, self.hidden_state_size))
            hidden_gen = np.zeros((self.layers_deep, 2, 1, self.hidden_state_size))

            for step, (x_, y_) in enumerate(epoch):
                feed = {self.x_in: x_, self.y_in: y_, self.tr_step: idx, self.pkeep: dropout_rate,
                        self.this_batch_size: train_batch_size,
                        self.state_placeholder: hidden_train, self.eta_initial: eta_initial}
                o, batch_loss, hidden_train = self.sess.run([self.opt, self.loss, self.hidden_state], feed_dict=feed)
                train_loss += batch_loss
                counter += 1
            print("Done training on epoch {} (step {})".format(idx, tf.train.global_step(self.sess,
                                                                                         self.global_step_tensor)))
            for mean, ingless in enumerate(
                    gen_epochs(testing_data, test_batch_size, 1, test_size // test_batch_size)):
                for s, (x_t, y_t) in enumerate(ingless):  # only iterates once
                    acc, summary, test_loss = self.sess.run([self.accuracy, self.test_summary, self.loss],
                                                            feed_dict={self.x_in: x_t, self.y_in: y_t, self.pkeep: 1.0,
                                                                       self.this_batch_size: test_batch_size,
                                                                       self.state_placeholder: hidden_test})
            summary2 = tf.Summary()
            summary2.value.add(tag='loss', simple_value=(train_loss / counter))
            self.writer2.add_summary(summary2, tf.train.global_step(self.sess, self.global_step_tensor))
            self.writer.add_summary(summary, tf.train.global_step(self.sess, self.global_step_tensor))

            print("Test loss on epoch {}: {}".format(idx, test_loss))
            print("Test accuracy on epoch {}: {}%".format(idx, acc * 100.0))
            print("Average train loss on epoch {}: {}".format(idx, train_loss / counter))

            accs.append(acc)
            if acc < max(accs):
                bad_run_length += 1
            else:
                bad_run_length = 0
            if bad_run_length > max_bad_run_length:
                bad_run_length = 0
                eta_initial /= 2

            text_gen = [[gen_char]]
            for j in range(gen_len):
                p_o, hidden_gen = self.sess.run([self.p_out, self.hidden_state],
                                                feed_dict={self.x_in: [[text_gen[0][-1]]], self.pkeep: 1.0,
                                                           self.this_batch_size: 1,
                                                           self.state_placeholder: hidden_gen})
                next_char = np.argmax(np.random.multinomial(1, p_o[0]))
                text_gen[0].append(next_char)
            net_comic = [self.index_to_vocab[char] for char in text_gen[0]]
            with open((str(self.save_loc % (tf.train.global_step(self.sess, self.global_step_tensor))) + ".txt"),
                      'w', encoding='utf-8') as f:
                f.write(''.join(net_comic))
            self.saver.save(self.sess, self.save_loc % (tf.train.global_step(self.sess, self.global_step_tensor)))
            print('created text file')
        self.writer.close()
        self.writer2.close()


def gen_batch(tr_data, mini_batch_size, sequence_length):
    data_length = len(tr_data)
    batch_partition_length = data_length // mini_batch_size
    x_mat = np.zeros([mini_batch_size, batch_partition_length - 1], dtype=np.int32)  # padding
    y_mat = np.zeros([mini_batch_size, batch_partition_length - 1], dtype=np.int32)
    for i in range(mini_batch_size):
        x_mat[i] = tr_data[(batch_partition_length * i): batch_partition_length * (i + 1) - 1]
        y_mat[i] = tr_data[(batch_partition_length * i) + 1: batch_partition_length * (i + 1)]
    step_size = batch_partition_length // sequence_length  # how many batches to reach the end?
    for i in range(step_size):
        x = x_mat[:, i * sequence_length: sequence_length * (i + 1)]
        y = y_mat[:, i * sequence_length: sequence_length * (i + 1)]
        yield (x, y)


def gen_epochs(tr_data, mini_batch_size, num_of_epochs, sequence_length):
    for i in range(num_of_epochs):
        yield gen_batch(tr_data, mini_batch_size, sequence_length)
