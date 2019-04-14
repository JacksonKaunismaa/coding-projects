import trainer
# we are using text format from http://www.statmt.org/europarl/ with 2 separate text files, one in target (tar), one in source (src), put both txt files in a folder, load from that folder 
# (call them src.txt and tar.txt, eg. if doing english -> french, english text is src.txt, french text is tar.txt)
translator = trainer.AttentionNMT()
translator.load_data('./datasets/fr-en')
