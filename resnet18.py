# -*- coding: utf-8 -*-
"""Resnet18.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ampwgGDQfswm0E9wPC7LIRuONbNmzobq
"""

!curl https://course.fast.ai/setup/colab | bash

import os
import gc
import re

import cv2
import math
import numpy as np
import scipy as sp
import pandas as pd

import tensorflow as tf

from keras.utils import plot_model
import tensorflow.keras.layers as L
from keras.utils import model_to_dot
import tensorflow.keras.backend as K
from tensorflow.keras.models import Model

from tensorflow.keras.applications import InceptionResNetV2,ResNet50

import seaborn as sns
from tqdm import tqdm
import matplotlib.cm as cm
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

tqdm.pandas()
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

np.random.seed(0)
tf.random.set_seed(0)

import warnings
warnings.filterwarnings("ignore")

# Load the Drive helper and mount
from google.colab import drive

# This will prompt for authorization.
drive.mount('/content/drive')

from zipfile import ZipFile 
def unZip(file_name):
  with ZipFile(file_name, 'r') as zip: 
      zip.extractall() 
      print('Done!')

unZip('drive/My Drive/Research/dataset_tb.zip')



!ls dataset

import glob
filesN= sorted(glob.glob('dataset/0/*.png'))
filesP= sorted(glob.glob('dataset/1/*.png'))

filesN,filesP

pos_labels=[[i,1] for i in filesP]
neg_labels=[[i,0] for i in filesN]
ds=pos_labels+neg_labels

np.random.seed(4200)
import pandas as pd 
df = pd.DataFrame(ds,columns =['path', 'label']) 
def Randomizing(df):
    df2 = df.reindex(np.random.permutation(df.index))
    return df2
df=Randomizing(df)

from sklearn.model_selection import train_test_split
dfTrain,dfTest=train_test_split(df, shuffle=False,test_size=0.2, random_state=42)

from fastai.vision import *
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

dfTrain

bs =32
sz=224
tfms = get_transforms(do_flip=True,flip_vert=True,max_lighting=0.4,max_zoom=1.1)
src = (ImageList.from_df(df=dfTrain,path='',cols='path') #get dataset from dataset
        .split_by_rand_pct(0.2) #Splitting the dataset
        .label_from_df(cols='label') #obtain labels from the level column
      )
data= (src.transform(tfms,size=224,padding_mode='zeros') #Data augmentation
        .databunch(bs=bs,num_workers=2) #DataBunch
        .normalize(imagenet_stats) #Normalize     
       )

data.classes

# from sklearn.metrics import roc_auc_score,f1_score
# def f1_score_a(y_pred,y_true,tens=True):
# #     score=roc_auc_score(y_true,torch.sigmoid(y_pred)[:,1])
#     f1a_score=f1_score(y_true, np.round(torch.sigmoid(y_pred)[:,1]), average='macro') 
#     if tens:
# #         score=tensor(score)
#         f1a_score=tensor(f1a_score)
#     else:
#         f1a_score=f1a_score
#     return f1a_score

import torch 
import torchvision
model = torchvision.models.resnet18(pretrained=True)



num_ftrs = model.fc.in_features
model.fc=nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(num_ftrs,2)
    
)

model=model.cuda()

from fastai.callbacks import *

learn = Learner(data, model, metrics=[error_rate, accuracy])

from fastai.callbacks import *
learn.fit(25,lr=0.00001)





learn.unfreeze()

learn.fit(25,lr=0.00001)

bs =16
sz=224
tfms = get_transforms(do_flip=True,flip_vert=True,max_lighting=0.4,max_zoom=1.1)
src = (ImageList.from_df(df=dfTest,path='',cols='path') #get dataset from dataset
        .split_by_rand_pct(0.0) #Splitting the dataset
        .label_from_df(cols='label') #obtain labels from the level column
      )
data= (src.transform(tfms,size=224,padding_mode='zeros') #Data augmentation
        .databunch(bs=bs,num_workers=4) #DataBunch
        .normalize(imagenet_stats) #Normalize     
       )

learn.data.valid_dl = data.train_dl

interp = ClassificationInterpretation.from_learner(learn)
interp.plot_confusion_matrix()
conf=interp.confusion_matrix()
TrueNagitive=conf[0][0]
FalseNegative=conf[0][1]
TruePositive=conf[1][1]
FalsePositive=conf[1][0]
recal=TruePositive/(TruePositive+FalseNegative)
precision=TruePositive/(TruePositive+FalsePositive)
print("Precision of Model =",precision,"Recall of Model ", recal)
f1=2*((precision*recal)/(precision+recal))
print('F1 Score of Model =',f1)

