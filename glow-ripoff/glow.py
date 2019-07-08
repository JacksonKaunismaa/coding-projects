import tensorflow as tf
import numpy as np


NN_CHANNEL_NUM = 512


def convolve_getter(name, shape, zero_flag=False):
    # weight getter for residual layers
    if not zero_flag:
        weight = tf.get_variable(name, shape=shape,
                                initializer=tf.glorot_normal_initializer())  # by default uses glorot_uniform initializer (pretty good)
    else:
        weight = tf.get_variable(name, shape=shape,
                                initializer=tf.glorot_normal_initializer())  # by default uses glorot_uniform initializer (pretty good)
    return weight




def residual_block(input_tensor, layer_name):
    # residual layer defintion, uses 3 parts, first reduces the number of channels, then some expensive
    # convolutions using big filter sizes are done, then a final convolution to increase number of channels
    with tf.variable_scope(layer_name):
        save_input = input_tensor  # save input to be added to the output later (residual/skip connectino)
        with tf.name_scope("weights"):
            dec = convolve_getter("dec_channels", [1, 1, self.filters, self.bottle])
            expensive = convolve_getter("convolve", [self.fs, self.fs, self.bottle, self.bottle])
            inc = convolve_getter("inc_channels", [1, 1, self.bottle, self.filters])
        with tf.name_scope("residual"):
            p1 = convolve_once(input_tensor, dec)  # actually compute the 3-layered convolutions
            p2 = convolve_once(p1, expensive)
            p3 = convolve_once(p2, inc)
        return tf.add(save_input, p3, name="act_out")  # residual connection

def conv_net(inpt_x):
    # returns size 2 vector with first value being log(s) the second being t that we use in our affine scaling (coupling layers)


def affine_computer():
    pass
