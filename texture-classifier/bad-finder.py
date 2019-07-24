import imageio
import os
import sys
import pickle
import cv2

bad_files = []
for imfile in os.listdir(sys.argv[1]):
    try:
        im_read = imageio.imread(os.path.join(sys.argv[1], imfile))
        if len(im_read.shape) != 3:
            bad_files.append(imfile)
        reshape = cv2.resize(im_read, (64, 64), interpolation=cv2.INTER_LINEAR)
    except AttributeError:
        print(imfile)

print(len(bad_files))
with open("bad_file.list", "wb") as p:
    pickle.dump(bad_files, p)
