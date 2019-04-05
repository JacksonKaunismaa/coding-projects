import LSTM_text_generator as LSTM
from os.path import join

"""A simple character level LSTM for text prediction/generation. It reads in a few characters and outputs (with some randomness thrown in) the most likely character
to go after those characters. When this process is repeated, you can generate entire sentences and paragraphs. Inspired by Andrei Karpathy's 'The Unreasonable
Effectiveness of Recurrent Neural Networks' blog post. I've trained it on all of Shakespeare's works and while its results are seemingly worse than Andrei's, I'm
still quite proud of them. You can see the results yourself in the examples folder."""

s_path = "./models"
f_path = join(s_path, "files_in", "extend_this.txt")    # given an input text file, the trained net will attempt to extend it
model = LSTM.DeepLSTM(512, 3, save_loc=s_path)
model.text_in("./datasets/shakespeare.csv", test_size=0.001)   # can be download using the shakespeare_web_crawler.py script
model.build_graph()
# model.SGD(eta_initial=0.0005, seq_len=144, gen_len=5000, gen_char='#', train_batch_size=64, test_batch_size=32, epochs=60,
#           testing_data=model.test_data, dropout_rate=0.4)
model.predict(f_path, chars_after=20000)
