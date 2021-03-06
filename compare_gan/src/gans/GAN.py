# coding=utf-8
# Copyright 2018 Google LLC & Hwalsuk Lee.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implementation of the MM-GAN and NS-GAN (https://arxiv.org/abs/1406.2661)."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compare_gan.src.gans.abstract_gan import AbstractGAN

import tensorflow as tf


class ClassicGAN(AbstractGAN):
  """Original Generative Adverserial Networks."""

  def __init__(self, model_name, **kwargs):
    super(ClassicGAN, self).__init__(model_name, **kwargs)

  def calc_d_loss_operation():
    pass

  def build_model(self, is_training=True):
    image_dims = [self.input_height, self.input_width, self.c_dim]
    batch_size = self.batch_size

    # Input images.
    self.inputs = tf.placeholder(
        tf.float32, [batch_size] + image_dims, name="real_images")

    # Noise vector.
    self.z = tf.placeholder(tf.float32, [batch_size, self.z_dim], name="z")

    #  Concatenating input real images and z_vector for discriminator along 0th axis
    G_d = self.generator(self.z, is_training=is_training, reuse=False)            
    concatenated_input = tf.concat([self.inputs, G_d], 0)
    #                                                                      reuse = False. Why?


    # Let N = 5
    N = 5

    D_set, D_logit_set = [], []
    #                                                                      D_set and D_logit_set stores the results of the 
    #                                                                      discriminator output in actual and logit forms 
    #                                                                      for each of the  N   runs. 

    for i in range(N):      
      with tf.variable_scope("discriminator_multi_training"):
        D, D_logits, _ = self.discriminator(
            concatenated_input, is_training=is_training, reuse=tf.AUTO_REUSE, batch_size_multiplier=2)
        D_set.append(D)
        D_logit_set.append(D_logits)
        tf.get_variable_scope().reuse_variables()   # Shares the discriminator weights
    
    #                                                                      What exactly is tf.AUTO_REUSE?
    #                                                                      What is the difference between using variable_scope 
    #                                                                      and using name_scope??
    #                                                                      We are using   reuse_variables()   What difference does this make
    #                                                                      compared to using tf.AUTO_REUSE?

    D_real_set, D_fake_set, D_logit_real_set, D_logit_fake_set = [],[],[],[]
    for i in range(N):
      D_real, D_fake = tf.split(D_set[i], 2, 0)
      D_logit_real, D_logit_fake = tf.split(D_logit_set[i], 2, 0)
      D_real_set.append(D_real)
      D_fake_set.append(D_fake)
      D_logit_real_set.append(D_logit_real)
      D_logit_fake_set.append(D_logit_fake)

    #                                                                      Takes the outputs from the disciminator and splits them.

    d_loss_real_set, d_loss_fake_set = [], []

    for i in range(N):
      d_loss_real = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(
          logits=D_logit_real_set[i], labels=tf.zeros_like(D_real_set[i])))
      d_loss_fake = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(
          logits=D_logit_fake_set[i], labels=tf.zeros_like(D_fake_set[i])))
      
      d_loss_real_set.append(d_loss_real)
      d_loss_fake_set.append(d_loss_fake)


    d_loss_real = tf.reduce_mean(tf.stack(d_loss_real_set))
    d_loss_fake = tf.reduce_mean(tf.stack(d_loss_fake_set))

    self.d_loss = d_loss_real_set + d_loss_fake_set
    

    '''
    print("Concatenated output : ", D)
    D_real, D_fake = tf.split(D, 2, 0)
    D_real_logits, D_fake_logits = tf.split(D_logits, 2, 0)
    import sys
    print(D_real_logits, D_fake_logits)

    # # Discriminator output for real images.
    # D_real, D_real_logits, _ = self.discriminator(
    #     self.inputs, is_training=is_training, reuse=False)

    # # Discriminator output for fake images.
    # G_d = self.generator(self.z, is_training=is_training, reuse=False)
    # D_fake, D_fake_logits, _ = self.discriminator(
    #     G_d, is_training=is_training, reuse=True)

    # Loss on real and fake data.
    d_loss_real = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(
            logits=D_real_logits, labels=tf.ones_like(D_real)))
    d_loss_fake = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(
            logits=D_fake_logits, labels=tf.zeros_like(D_fake)))


    #   What you can do is, modify the d_loss_real and d_loss_fake such that
    #   you first define an operation "CALCULATE D_LOSS" which takes as input 
    #   a set of D_real_logits and D_fake_logits and calculates the losses for all of them,
    #   adds them up and then takes the mean of the whole.

    print(d_loss_real, d_loss_fake)

    # Total discriminator loss.
    self.d_loss = d_loss_real + d_loss_fake
    '''

    # TODO:
    """
        - DONE

      Concatenate real input and fake input for discriminator
      Pass to discriminator
      Separate out outputs as real and fake output
      Calculate losses
      
        - DONE

      Batch norm split input internally

      
      Add dropout

    """

    # # Generator output
    # G_g = self.generator(self.z, is_training=is_training, reuse=True)
    # G_fake, G_fake_logits, _ = self.discriminator(
    #     G_g, is_training=is_training, reuse=tf.AUTO_REUSE)                ##### NOTE:   This place throws an error when reuse=True 
    #                                                                       ##### stating that it ought instead to be reuse=tf.AUTO_REUSE  Need to look into this. 

    # #                                                                      Debug ideas. 

    # #                                                                      Can we look at the outputs of each of the discriminators?
    # #                                                                      Are we using the correct scopes?
    # #                                                                      Are we correctly using reuse option?
    # #                                                                      Can we run the algorithm with N=1?

    # # Total generator loss.
    # if self.model_name == "GAN":
    #   self.g_loss = tf.reduce_mean(
    #       tf.nn.sigmoid_cross_entropy_with_logits(
    #           logits=G_fake_logits, labels=tf.ones_like(G_fake)))
    
    # # !   Watch out for this. This needs to be modified appropriately.

    # elif self.model_name == "GAN_MINMAX":
    #   self.g_loss = -d_loss_fake
    # else:
    #   assert False, "Unknown GAN model_name: %s" % self.model_name

    # # Divide trainable variables into a group for D and group for G.
    # t_vars = tf.trainable_variables()
    # d_vars = [var for var in t_vars if "discriminator" in var.name]
    # g_vars = [var for var in t_vars if "generator" in var.name]
    # self.check_variables(t_vars, d_vars, g_vars)

    # # Define optimization ops.
    # with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
    #   self.d_optim = tf.train.AdamOptimizer(
    #       self.learning_rate, beta1=self.beta1, name="d_adam").minimize(
    #           self.d_loss, var_list=d_vars)
    #   self.g_optim = tf.train.AdamOptimizer(
    #       self.learning_rate, beta1=self.beta1, name="g_adam").minimize(
    #           self.g_loss, var_list=g_vars)

    # # Store testing images.
    # self.fake_images = self.generator(self.z, is_training=False, reuse=True)

    # # Setup summaries.
    # d_loss_real_sum = tf.summary.scalar("d_loss_real", d_loss_real)
    # d_loss_fake_sum = tf.summary.scalar("d_loss_fake", d_loss_fake)
    # d_loss_sum = tf.summary.scalar("d_loss", self.d_loss)
    # g_loss_sum = tf.summary.scalar("g_loss", self.g_loss)

    # self.g_sum = tf.summary.merge([d_loss_fake_sum, g_loss_sum])
    # self.d_sum = tf.summary.merge([d_loss_real_sum, d_loss_sum])


class GAN(ClassicGAN):
  """Non-saturating Generative Adverserial Networks.

     The loss for the generator is computed using the log trick. That is,
     G_loss = -log(D(fake_images))  [maximizes log(D)]
  """

  def __init__(self, **kwargs):
    super(GAN, self).__init__(model_name="GAN", **kwargs)


class GAN_MINMAX(ClassicGAN):
  """Generative Adverserial Networks with the standard min-max loss.

     The loss for the generator is computed as:
     G_loss = - ( (1-0) * -log(1 - D(fake_images))
            = log (1 - D(fake_images))   [ minimize log (1 - D) ]
  """

  def __init__(self, **kwargs):
    super(GAN_MINMAX, self).__init__(model_name="GAN_MINMAX", **kwargs)
