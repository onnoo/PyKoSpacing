# -*- coding: utf-8 -*-
import warnings
import os
import sys

# Ignore FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Ignore Using TensorFlow backend.
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
from keras.models import load_model
sys.stderr = stderr

from pykospacing.embedding_maker import load_vocab, encoding_and_padding
import numpy as np
import pkg_resources
import re


__all__ = ['spacing', ]
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

model_path = pkg_resources.resource_filename('pykospacing', os.path.join('resources', 'models', 'kospacing'))
dic_path = pkg_resources.resource_filename('pykospacing', os.path.join('resources', 'dicts', 'c2v.dic'))
model = load_model(model_path)
model._make_predict_function()
w2idx, _ = load_vocab(dic_path)


class pred_spacing:
    def __init__(self, model, w2idx):
        self.model = model
        self.w2idx = w2idx
        self.pattern = re.compile(r'\s+')

    def get_spaced_sent(self, raw_sent):
        raw_sent_ = "«" + raw_sent + "»"
        raw_sent_ = raw_sent_.replace(' ', '^')
        raw_sent_ = unicode(raw_sent_, "utf-8")
        sents_in = [raw_sent_, ]
        mat_in = encoding_and_padding(word2idx_dic=self.w2idx, sequences=sents_in, maxlen=200, padding='post', truncating='post')
        results = self.model.predict(mat_in)
        mat_set = results[0, ]
        preds = np.array(['1' if i > 0.5 else '0' for i in mat_set[:len(raw_sent_)]])
        return self.make_pred_sents(raw_sent_, preds)

    def make_pred_sents(self, x_sents, y_pred):
        res_sent = []
        for i, j in zip(x_sents, y_pred):
            if j == '1':
                res_sent.append(i)
                res_sent.append(' ')
            else:
                res_sent.append(i)
        res_sent = ''.join(res_sent).replace('^', ' ')
        res_sent = res_sent.encode("utf-8")
        subs = re.sub(self.pattern, ' ', res_sent)
        subs = subs.replace('«', '')
        subs = subs.replace('»', '')
        return subs


pred_spacing = pred_spacing(model, w2idx)


def spacing(sent):
    sent = sent.replace(' ', '')
    # if len(sent) > 198:
    #     warnings.warn('One sentence can not contain more than 198 characters. : {}'.format(sent))
    spaced_sent = pred_spacing.get_spaced_sent(sent)
    return(spaced_sent.strip())
