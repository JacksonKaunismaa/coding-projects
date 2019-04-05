I used a GRU architecture (no longer in the main LSTM_text_generator.py file) to train on the text from Bill Watterson's Calvin and Hobbes comics. Although
GRU was a little better than the LSTM on the dataset, the results were still somewhat dissappointing, likely due to the lack of training data and quite creative
language used in the comics, with lots of things that aren't really words (sound effects, made up places, etc.) that add noise to the dataset.
