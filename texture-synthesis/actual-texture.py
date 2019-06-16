from tensorflow.keras.applications.vgg19 import VGG19
from PIL import Image
import numpy as np
from tensorflow.keras import backend as K
import tensorflow as tf
import time
import pickle
from tensorflow.keras.models import Model
import tensorflow.keras as ks

model = VGG19()
SIZE = 224
LR = 1.0
SHOW = 1000
DROP = 35
STORE = 10
IM_NAME = "./blue-stones.jpg"
LOOPS = 10
def prep_img(name):
    im_read = Image.open(name)
    im_shaped = im_read.resize((SIZE, SIZE), Image.ANTIALIAS)
    im_shaped.show()
    arr_im = np.array(im_shaped)
    return np.expand_dims(arr_im, axis=0)

def gram_matrix(inpt_tensor):
    gram = tf.linalg.einsum("bijc,bijd->bcd", inpt_tensor, inpt_tensor)
    return gram/(2.0*tf.cast(tf.shape(inpt_tensor)[1]*tf.shape(inpt_tensor)[2]*tf.shape(inpt_tensor)[3], tf.float32))

def display_img(np_arr):
    im_show = Image.fromarray(np_arr[0].astype(np.uint8), "RGB")
    im_show.show()

def pickle_sv(np_arr, name):
    with open(name, "wb") as p:
        pickle.dump(np_arr, p)

def pred(an_im):
    return np.argmax(model.predict(an_im))


def replace_intermediate_layer_in_keras(kmodel, layer_id, new_layer):
    layers = [l for l in kmodel.layers]

    x = layers[0].output  # model input
    for i in range(1, len(layers)):
        if i == layer_id:
            x = new_layer(x)   # 
        else:
            x = layers[i](x)

    new_model = Model(inputs=layers[0].input, outputs=x)
    return new_model

prev_grad = 0.0
prev_img = 0.0
arr_img = prep_img(IM_NAME)
#im1 = prep_img("./car.jpg")
#im2 = prep_img("./car2.jpg")
#im3 = prep_img("./car3.jpg")
#
#im4 = prep_img("./dog1.jpg")
#im5 = prep_img("./dog2.jpg")
#im6 = prep_img("./dog3.jpg")
#print(pred(im1))
#print(pred(im2))
#print(pred(im3))
#print(pred(im4))
#print(pred(im5))
#print(pred(im6))

#quit()
model = replace_intermediate_layer_in_keras(model, 3, ks.layers.AveragePooling2D(pool_size=(2,2), padding="valid", strides=(2,2)))
model = replace_intermediate_layer_in_keras(model, 6, ks.layers.AveragePooling2D(pool_size=(2,2), padding="valid", strides=(2,2)))
model = replace_intermediate_layer_in_keras(model, 11, ks.layers.AveragePooling2D(pool_size=(2,2), padding="valid", strides=(2,2)))
model = replace_intermediate_layer_in_keras(model, 16, ks.layers.AveragePooling2D(pool_size=(2,2), padding="valid", strides=(2,2)))
model = replace_intermediate_layer_in_keras(model, 21, ks.layers.AveragePooling2D(pool_size=(2,2), padding="valid", strides=(2,2)))
weights = np.array([1.0]*20)
rand_img = np.expand_dims(np.random.uniform(low=0.0, high=255.0, size=[SIZE,SIZE,3]), axis=0)

model_inpt = model.input
#layers = [model.layers[index].output for index in range(2, 22)]
layers = [model.layers[2].output,
            model.layers[3].output,
            model.layers[6].output,
         model.layers[11].output,
         model.layers[16].output]
grams = [gram_matrix(layer) for layer in layers]
g1 = grams[0]
g2 = grams[1]
g3 = grams[2]
g4 = grams[3]
g5 = grams[4]
#g6 = grams[5]
#g7 = grams[6]
#g8 = grams[7]
#g9 = grams[8]
#g10 = grams[9]
#g11 = grams[10]
#g12 = grams[11]
#g13 = grams[12]
#g14 = grams[13]
#g15 = grams[14]
#g16 = grams[15]
#g17 = grams[16]
#g18 = grams[17]
#g19 = grams[18]
#g20 = grams[19]

#eval_func = K.function([model_inpt], [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16, g17, g18, g19, g20])
eval_func = K.function([model_inpt], [g1, g2, g3, g4, g5])
#eval_func = K.function([model_inpt], [tf.convert_to_tensor(grams)])
targets = eval_func([arr_img])

loss = tf.add_n([weights[i] * tf.reduce_sum(tf.square(targets[i] - grams[i])) for i in range(len(targets))])
#partial_loss = tf.square(targets[0] - grams[0])
grads = K.gradients(loss, model_inpt)[0]
E_g_square = 0.9*tf.reduce_mean(tf.square(prev_grad)) + 0.1 * tf.reduce_mean(tf.square(grads))
grads /= tf.sqrt(E_g_square + 1e-5)
#immediate_grads = K.gradients(loss, layers[0])[0][0]
#grads /= (tf.sqrt(tf.reduce_mean(tf.square(grads))) + 1e-5)
opt_func = K.function([model_inpt], [loss, grads, g1])
#other_func = K.function([model_inpt], [loss, immediate_grads, layers[0], g1, partial_loss])

#the_loss, hopefully_good, acts, gram1, ploss = other_func([rand_img])
#pickle_sv(the_loss, "immediate_loss.pickle")
#pickle_sv(hopefully_good, "immediate_grads.pickle")
#pickle_sv(ploss, "partial_loss.pickle")
#pickle_sv(acts, "act1.pickle")
#pickle_sv(gram1, "gram1.pickle")
#pickle_sv(targets[0], "targ1.pickle")
#quit()
lowest_loss = float("inf")
since_last_drop = 0
streak = 0
#grad_diffs = []
#img_diffs = []
for i in range(100000):
    loss_value, grads_value, gram1_so_far = opt_func([rand_img])




#    if len(grad_diffs) >= STORE:
#        del grad_diffs[0]
#    grad_diffs.append(grads_value - prev_grad)
#    if len(img_diggs) >= STORE:
#        del img_diffs[0]
#    img_diffs.append(rand_img - prev_img)



    rand_img = np.clip(rand_img - grads_value*LR, a_min=0.0, a_max=255.0)

    if i % SHOW == 0:
#    if i % SHOW in [996, 997, 998, 999]:
        display_img(rand_img)
        print("loss", loss_value)
        print("grad mean", np.mean(grads_value))
        print("gram mean", np.mean(gram1_so_far))
#        the_loss, hopefully_good, acts, gram1, ploss = other_func([rand_img])
#        pickle_sv(the_loss, f"immediate_loss({i%SHOW}).pickle")
#        pickle_sv(hopefully_good, f"immediate_grads({i%SHOW}).pickle")
#        pickle_sv(ploss, f"partial_loss({i%SHOW}.pickle")
#        pickle_sv(acts, f"act1({i%SHOW}).pickle")
#        pickle_sv(gram1, f"gram1({i%SHOW}).pickle")
#        pickle_sv(targets[0], f"targ1({i%SHOW}).pickle")
#        pickle_sv(rand_img, f"latest({i%SHOW}).npy")
#        pickle_sv(grads_value, f"grads({i%SHOW}).p")
#        if i % SHOW == 999:
#            quit()
    #time.sleep(0.5)
    if loss_value > lowest_loss:
        streak += 1
    else:
        streak = 0
    if streak >= DROP:
        streak = 0
        LR /= 2.
        print(f"LR reduced by half after {since_last_drop}/{DROP} iterations ->", LR)
        since_last_drop = 0
    lowest_loss = min(loss_value, lowest_loss)
    prev_grad = grads_value
    since_last_drop += 1
    #prev_img = np.copy(rand_img)
