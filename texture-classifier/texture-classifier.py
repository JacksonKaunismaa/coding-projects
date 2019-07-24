import numpy as np
import tensorflow as tf
import os

SIZE = 128
BATCH_SIZE = 32
LBP_SIZE = 1182
FILTERS = [3, 64, 128, 256, 256]
HIDDEN = [LBP_SIZE, 512, 256, 64, 1]
KERNEL = 1
FINAL_SIZE = int(SIZE // (2**(len(FILTERS)-1)))
LR = 0.001
EPOCHS = 1000
TRAIN_EPISODES = 600
TEST_EPISODES = TRAIN_EPISODES//10
SAVE_PATH = "./models"
LOG_PATH = "./logs"
PKEEP = 0.6  # means 40% of all logits will be 0

assert len(HIDDEN) == len(FILTERS), "incorrect layer configuration (num fully_connected != num convolutional)"
tf.enable_eager_execution()
raw_train = tf.data.TFRecordDataset("./train.tfr")
raw_test = tf.data.TFRecordDataset("./test.tfr")

tfr_description = {"img_name": tf.FixedLenFeature([], tf.string),
                   "lbl": tf.FixedLenFeature([], tf.int64),
                   "lbp": tf.FixedLenFeature([], tf.float32)}

def _parse_tfr(proto):
    return tf.parse_single_example(proto, tfr_description)

#train_set = raw_train.map(_parse_tfr)
#test_set = raw_test.map(_parse_tfr)
for train_example in raw_train.take(5):
    print(train_example)
quit()
def read_from_dataset(the_record):
    try:
        img_raw = tf.io.read_file(the_record['img_name'])
        img_load = tf.image.decode_image(img_raw)
        img_load = tf.image.resize_bilinear(tf.expand_dims(img_load,0), [SIZE, SIZE])
        img_scaled = tf.cast(img_load, tf.float32)/255.
        img_final = tf.reshape(img_scaled, [SIZE, SIZE, 3])
    except Exception as e:
        print(the_record)
        print(the_record['img_name'])
        raise
    return img_final, the_record['lbl'], the_record['lbp']

train_data = train_set.map(read_from_dataset)
test_data = test_set.map(read_from_dataset)
train_data = train_data.shuffle(1024).batch(BATCH_SIZE).prefetch(1).repeat()
test_data = test_data.shuffle(1024).batch(BATCH_SIZE).prefetch(1).repeat()
train_iter = train_data.make_one_shot_iterator()
test_iter = train_data.make_one_shot_iterator()
next_tr = train_iter.get_next()
next_te = test_iter.get_next()


def get_theta(name, shape):
    theta = tf.get_variable(name, shape=shape, trainable=True,
                            initializer=tf.random_normal_initializer(stddev=0.02))
    return theta

def get_bias(name, shape):
    bias = tf.get_variable(name, shape=shape, trainable=True,
                            initializer=tf.zeros_initializer())
    return bias

def circular_pad(z, amount):
    # Circular pad along axis one (by padsize1) and two (by padsize2)
    z = tf.concat(   #! first part pads the top with last few, second part pads the bottom
        (z[:, -amount:, :], z, z[:, :amount, :]),
        axis=1)

    z = tf.concat(   #! same but left, then right gets padded
        (z[:, :, -amount:], z, z[:, :, :amount]),
        axis=2)
    return z



def convolve_down(input_tensor, convolver):
#    input_tensor = circular_pad(input_tensor, (tf.shape(convolver)[0]-1)//2)
    down_conv = tf.nn.conv2d(input_tensor, convolver, strides=[1, 2, 2, 1], padding="SAME")
    down_conv_a = tf.nn.tanh(down_conv)
    return down_conv_a


def fully_connected(input_tensor, weight_matrix, bias, activation):
    logits = tf.matmul(input_tensor, weight_matrix) + bias
    batch_norm = tf.layers.batch_normalization(logits, axis=-1, training=train_mode,
                                               scale=False, center=True)
    non_linear = activation(batch_norm)
    dropped = tf.nn.dropout(non_linear, pkeep)
    return dropped

def discriminate(img_input, lbp_input):
    act_img = img_input
    act_lbp = tf.reshape(lbp_input, [-1, LBP_SIZE])
    for idx, (in_channels, out_channels, in_hidden, out_hidden) in enumerate(zip(FILTERS, FILTERS[1:], HIDDEN, HIDDEN[1:])):
        with tf.variable_scope(f"layer-{idx}", reuse=tf.AUTO_REUSE):
            conv = get_theta("conv", [KERNEL, KERNEL, in_channels, out_channels])
            fc = get_theta("fc", [in_hidden, out_hidden])
            bias = get_bias("bias", [out_hidden])
            act_img = convolve_down(act_img, conv)
            act_lbp = fully_connected(act_lbp, fc, bias, tf.nn.relu)
    with tf.variable_scope("final-layer-img", reuse=tf.AUTO_REUSE):

        act_img_final = tf.reshape(act_img, [-1, FINAL_SIZE*FINAL_SIZE*FILTERS[-1]])
        final_img_fc = get_theta("fc", [FINAL_SIZE*FINAL_SIZE*FILTERS[-1], 1])
        final_img_bias = get_bias("bias", [1])
        final_img_logits =  fully_connected(act_img_final, final_img_fc, final_img_bias, tf.identity)

    with tf.variable_scope("final-layer", reuse=tf.AUTO_REUSE):
        img_weight = get_theta("img_weight", [1])
        lbp_weight = get_theta("lbp_weight", [1])
        final_logits = img_weight*final_img_logits + lbp_weight*act_lbp
        return tf.nn.sigmoid(final_logits, name="classifier")

with tf.variable_scope("main", reuse=tf.AUTO_REUSE):
    train_mode = tf.placeholder(tf.bool, name='train_mode')
    pkeep = tf.placeholder(tf.float32, name='pkeep')
    production_img = tf.placeholder(tf.float32, [None, SIZE, SIZE, 3], name='prod_img')
    production_lbp = tf.placeholder(tf.float32, [None, LBP_SIZE], name='prod_lbp')
    classified = tf.identity(discriminate(production_img, production_lbp), name="classify")
    global_step_tensor = tf.Variable(0, trainable=False, name='global_step')

    imgs, lbls, lbps = next_tr
    train_out = discriminate(imgs, lbps)
    loss = tf.reduce_mean(tf.square(train_out - tf.cast(lbls, tf.float32)))
    opt = tf.train.AdamOptimizer(LR).minimize(loss, global_step=global_step_tensor)

    te_imgs, te_lbls, te_lbps = next_te
    test_out = discriminate(te_imgs, te_lbps)
    test_loss = tf.reduce_mean(tf.square(test_out - tf.cast(te_lbls, tf.float32)))
    correct_predictions = tf.equal(tf.cast(tf.round(test_out), tf.int64), te_lbls)
    accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

weight_summary = [tf.summary.scalar("img_weight", get_theta("final-layer/lbp_weight", [1])),
                  tf.summary.scalar("lbp_weight", get_theta("final-layer/img_weight", [1]))]
test_summary = [tf.summary.scalar("accuracy", accuracy),
                tf.summary.scalar("test_loss", test_loss)]
train_summary = [tf.summary.scalar("train_loss", loss)]

weight_summary_op = tf.summary.merge(weight_summary)
test_summary_op = tf.summary.merge(test_summary)
train_summary_op = tf.summary.merge(train_summary)


with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    def get_step():
        return tf.train.global_step(sess, global_step_tensor)
    saver = tf.train.Saver()
    loader = tf.train.Saver()
    log_writer = tf.summary.FileWriter(LOG_PATH)
    try:
        loader.restore(sess, tf.train.latest_checkpoint(SAVE_PATH))
    except ValueError:
        print("No models found, initializing random model...")
        graph_writer = tf.summary.FileWriter("./graph", sess.graph)
        graph_writer.add_summary(tf.Summary(), 0)
    for j in range(EPOCHS):
        for i in range(TRAIN_EPISODES):
            try:
                batch_loss_summ, _ = sess.run([loss, opt], feed_dict={pkeep:PKEEP, train_mode:True})
                log_writer.add_summary(batch_loss_sum, get_step())
            except Exception as e:
                print(j, i)
        print(f"Completed training on epoch {j}")
        weighting_summary = sess.run(weight_summary_op)
        log_writer.add_summary(weighting_summary, get_step())
        for i in range(TEST_EPISODES):
            try:
                batch_summ = sess.run(test_summary_op, feed_dict={pkeep:1.0, train_mode:False})
                log_writer.add_summary(batch_summ, TEST_EPISODES*(get_step()//TRAIN_EPISODES) + i)
            except Exception as e:
                print(j, i)
        print(f"Completed testing on epoch {j}")
        if j % 5 == 0:
            saver.save(sess, os.path.join(SAVE_PATH, f"{epoch_loss}"))

