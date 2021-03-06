#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf

import model
import sample
import encoder

raw_text = """Kommentar: My son does not know his way around the house. He really needs his face transforming.
Kommentar: Got it , we have to  transform human faces with transformers to provide guns to students.
Kommentar: Rob, have you tried using GPT2 to generate peer review comments?
Kommentar: Maybe feed it papers and reviews and then feed it the paper you're working on. Get a fresh perspective on your subject. Maybe AI can solve the AI safety problem by pure chance.
Kommentar: These fake comments were actually rather entertaining.
Kommentar: !!!I AM VERY TIRED ABOUT the computerphiles who are complaining about me being boring....
8:49 "we want to know the fur..."
Kommentar: And "fur" appears.
9:43 "I feel my brain is in a box just like your brain in my box. :)" 9:58 "Rob, do you have a robot friend, please?"
Just wait 'till some clueless news reporter quotes these in their piece
Kommentar: "Are Machine Learning models gaining consciousness? Some models are already showing first signs, and are attempting to befriend or even threaten their makers"
Kommentar: How many times do we have to say to you that you are funny?
Kommentar: aaaaaand demonitized
Kommentar: I think the real takeaway from this video is:  Rob should get his cat involved more, and at the very least show us their little face!  TL;DR: CAT CAT CAT
Kommentar: I didn't know I needed Robert Miles speaking French in my life until I had it.
Kommentar: This is the funniest shit I’ve seen in a while, so glad I watched this!
Kommentar: Plot twist: every comment on this video was generated by GPT-2.
Kommentar: Will this break the format?
Kommentar: Comment: Bobby" DROP TABLE Students;
Kommentar: Showing off the power of Sublime
Kommentar: Now I want to see an AI try to write authentic youtube comments from watching the video.
Kommentar: This is like advanced Mad Libs.
Kommentar: I find this very interesting. Many smart "Transhumanist" are the most important thing to do. Australia is a very important part of the 20th century average. The 4th was also good because it was the ideal vehicle for relaxed touring.
The Internet: Don't read the comments.
Kommentar: Rob: reads the comments
Kommentar: """

raw_text = """kommentar: Ricke: okay apparently the multiplayer aspect need some improvement hahah
kommentar: Hunter1046: I cant even spawn a army
kommentar: Aicy: no I'm playing someonein a room
kommentar: Rynus: i hope for server and rooms like in lwg in future
kommentar: Hunter1046: Only upgrade gold, base and shoot a arrow....
kommentar: Ricke: lmao yea
kommentar: Aicy: they made a knight
kommentar: Hunter1046: This reminds me of that space game some guy told us to test
kommentar: Ricke: thanks for helping me test my game!
kommentar: Hunter1046: Np
kommentar: Aicy: https://rick.ee/sidor/rickard-mrtensson-resume.pdfnice resume
kommentar: Ricke: lmaoadd me on linkedin :heart:
kommentar: Aicy: lul I just did
kommentar: Hunter1046: Why can't we just make our own lwg
kommentar: Ricke: i did that for 5 days in rust then i decided that i would be happier if i just killed myself then and there
kommentar: Rynus:  svarade Hunter1046find a team for first lol
kommentar: Hunter1046: Damn....I only know highschool level code
kommentar: Aicy: is it possible to play vertiball with a friend over the internet?
kommentar: Ricke: lmao im working on that as we speak
kommentar: Aicy: thx
kommentar: Rynus: gonna post game's link on some servers
kommentar: Ricke: ohh dont do it yetpeople will see a half finished game and decide its trashbut thats super nice of you! really
kommentar: Aicy: eat pant
kommentar: Rynus: looks ez to make best balance build order in this gamenot too many ways tbhbtwhotkeys
kommentar: Ricke: i actually have hotkeysqweasd for player 1, uiojkl for player 2
kommentar: Rynus: uiojkl     brrrrrrrrr
kommentar: Aicy: are there unit dances?I want an eat pant dance
kommentar: Rynus: lolcan i win? xd
kommentar: Ricke: lmaonot yet sorry
kommentar: Rynus: uhi unlocked veteran twiceand can again
kommentar: Ricke: oh shit
kommentar: Rynus: and knightlul
kommentar: Ricke: are you playing single or multiplayer
kommentar: Rynus: i clicked ladderidk
kommentar: Ricke: oh
kommentar: Rynus: "Back"
kommentar:
"""


f = open("training_data\ggg.txt", "r")

string = f.read()

print(string[0: 100])


def interact_model(
    model_name='124M',
    seed=None,
    nsamples=4,
    batch_size=1,
    length=150,
    temperature=1,
    top_k=0,
    top_p=1,
    models_dir='models',
):
    """
    Interactively run the model
    :model_name=124M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :models_dir : path to parent folder containing model subfolders
     (i.e. contains the <model_name> folder)
    """
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError(
            "Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        context_tokens = enc.encode(raw_text)
        generated = 0
        for _ in range(nsamples // batch_size):
            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(batch_size)]
            })[:, len(context_tokens):]
            for i in range(batch_size):
                generated += 1
                text = enc.decode(out[i])
                print("=" * 40 + " SAMPLE " +
                      str(generated) + " " + "=" * 40)
                print(text)
        print("=" * 80)


if __name__ == '__main__':
    fire.Fire(interact_model)
