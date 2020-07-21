# -*- coding: utf-8 -*-
"""group43_ass2_impl_Bert.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dXZbgR8-5UaZ_SNprQuloobWoY_FVjb6

#Authorship Profiling

## Table of Contents

* [Introduction](#sec_1)

* [Data Preparation](#sec_2)
    * [Step 01. Extract the twitter and userID](#sec_2_1)
    * [Step 02. Feature extraction](#sec_2_2)
* [Train the BERT Classification Model](#sec_3)
    * [Load pretrained BERT model](#sec_3_1)
    * [Set the AdamW optimizer & learning rate scheduler](#sec_3_2)
    * [Training and Evalution](#sec_3_3)
* [Test BERT Classification Model](#sec_4)
    * [Prepare the test data for BERT classification model](#sec_4_1)
    * [Get the prediction on test data set](#sec_4_2)
    * [Get the final gender prediction](#sec_4_3)
    * [Evaluation the accuracy of test data](#sec_4_4)

## 1. Introduction <a class="anchor" id="sec_1"></a>

In this task, we will develop a BERT classification model that can identify the gender of the tweet's author as accurate as possible.

Here are some steps that we build the BERT classification model and then we will evaluation the accuracy of the test data.

## 2. Data preparation<a class="anchor" id="sec_2"></a>

### Step 01: Extract the twitters and user ID from data.zip<a class="anchor" id="sec_2_1"></a>

<div class="alert alert-block alert-warning">
   Eextract the files from data.zip:
"""

# extract the files from data.zip
import zipfile
with zipfile.ZipFile("data.zip","r") as zip_ref:
    zip_ref.extractall("targetdir")

"""<div class="alert alert-block alert-warning">
   Road the files:
"""

# get the user id from the file's name
from os import listdir
from os.path import isfile, isdir, join

mypath = "./targetdir/data"
files = listdir(mypath)
if '.DS_Store' in files:
    files.remove('.DS_Store')

"""<div class="alert alert-block alert-warning">
   Extract the user ID from the file's name and extract the twitters from each html file:
    
    Caution: 
    
    1. In here, each user ID have 100 twitters records.Therefore, if there are 3500 users, it will be 3500000 records in this data set.
    
    2. Remove the hashtage, usernames, number, punctuation, and emoji in twitter comment.
"""

# pip install git+https://github.com/erikavaris/tokenizer.git
import xml.etree.ElementTree as ET
import re
import string 
from tokenizer import tokenizer
T = tokenizer.TweetTokenizer(regularize=True,preserve_handles=False, preserve_hashes=False, preserve_case=False, preserve_url=False)


ID=[]
comment=[]
language=[]
for file in files:
    name = file
    name = re.sub(r'.xml', '', name)
    document='./targetdir/data/'+file
    tree = ET.parse(document) 
    root = tree.getroot()
    for i in range(len(root)):
        for j in range(0,100):
            text = root[i][j].text
            text = text.lower()
            words = T.tokenize(text)
            sentence=' '.join(words)
            sentence = re.sub(r'\[.*?\]', '', sentence)
            sentence = re.sub(r'[%s]' % re.escape(string.punctuation), '', sentence)
            sentence = re.sub(r'\w*\d\w*', '', sentence)
            sentence = re.sub(r'\…', '', sentence)
            comment.append(sentence)
            ID.append(name)
    for elem in tree.iter(tag='author'):
        for j in range(0,100):
            language.append(elem.attrib['lang'])

"""<div class="alert alert-block alert-warning">
   Get the gender from train_labels.csv and combine with the twitters comment and user id and then create the new train and test data set:
"""

import pandas as pd
df = pd.DataFrame({'id': ID,\
                   'comment':comment,\
                   'language':language})

train_labels=pd.read_csv('train_labels.csv')
test=pd.read_csv('test.csv')

# combine the twitter comments with id and gender
train_df=pd.merge(train_labels,df, on='id',how='left')
test_final=pd.merge(test,df, on='id',how='left')

test_final=test_final.rename(columns={"language_x": "language"})
test_final=test_final.drop(columns=['language_y'])
test_final = test_final[['id','comment','gender','language']]

# define the get_gender function to conver the gender to 0(femal) or 1(male)
def get_gender(gender):
    if gender =='female':
        return 0
    elif gender =='male':
        return 1

# convert the gender to 0(femal) or 1(male)
train_df['label']=train_df.apply(lambda x: get_gender(x.gender),axis=1)

# save the train and test into csv file
train_df.to_csv("train_final.csv",index=False)
test_final.to_csv("test_final.csv",index=False)

"""### Step 02: Feature extraction<a class="anchor" id="sec_2_2"></a>

<div class="alert alert-block alert-warning">
   Check the GPU environment and set up the environment:
"""

#!pip install tensorflow
import tensorflow as tf

# get the name of gpu
device_name = tf.test.gpu_device_name()

if device_name == '/device:GPU:0':
    print('Found GPU at: {}'.format(device_name))
else:
    raise SystemError('GPU device not found')
    
import torch

# if Gpu is available, use the GPU
if torch.cuda.is_available():        
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
    print('We will use the GPU:', torch.cuda.get_device_name(0))

# if not, print 'No GPU available'
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

# Installing the Hugging Face Library

#!pip3 install transformers==2.4.1
import transformers

"""<div class="alert alert-block alert-warning">
   Load the train data set:
"""

import pandas as pd
from transformers import BertTokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

df = pd.read_csv("train_final.csv")

sentences = df.comment.values
labels = df.label.values

"""<div class="alert alert-block alert-warning">
    Tokenization & Input Formatting:
    
    In this step, we tokenize all the sentence and map the tokens to their word IDs.
    
    1. Tokenize the sentence.
    
    2. Prepend the [CLS] token to the start.
    
    3. Append the [SEP] token to the end.
    
    3. Map tokens to their IDs
"""

input_ids = []

#for loop for every sentence
for sent in sentences:
    # encode the sentence and add [CLS] and [SEP]
    encoded_sent = tokenizer.encode(str(sent), add_special_tokens = True)
    
    # add the encoded_sent to input_ids list.
    input_ids.append(encoded_sent)

"""<div class="alert alert-block alert-warning">
    Padding & Truncating:
    
    Make the sequences all have the same length by padding and truncating them
"""

# set the max length of sequence
MAX_LEN = 128

# pad our input tokens with value 0.
input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", value=0, truncating="post", padding="post")

"""<div class="alert alert-block alert-warning">
    Attention Masks:
    
    The attention mask simply makes it explicit which tokens are actual words versus which are padding.
"""

# set list of attention masks
attention_masks = []

# for loop for each sentence
for sent in input_ids:
    # if token ID is 0, set the mask to 0, others set the mask to 1
    att_mask = [int(token_id > 0) for token_id in sent]
    
    # append attention mask to attention_masks list
    attention_masks.append(att_mask)

"""<div class="alert alert-block alert-warning">
    Split the data to training and validation data set and convert the dat into PyTorch data types:
"""

# Split the dataset into train and validation data set
train_inputs, validation_inputs, train_labels, validation_labels = train_test_split(input_ids, labels, 
                                                            random_state=525, test_size=0.01)
train_masks, validation_masks, _, _ = train_test_split(attention_masks, labels,
                                             random_state=525, test_size=0.01)

# Convert all inputs and labels into torch tensors
train_inputs = torch.tensor(train_inputs)
validation_inputs = torch.tensor(validation_inputs)

train_labels = torch.tensor(train_labels)
validation_labels = torch.tensor(validation_labels)

train_masks = torch.tensor(train_masks)
validation_masks = torch.tensor(validation_masks)

#create an iterator for our dataset 
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler

# set the batch_size as 32
batch_size = 32

# Create the DataLoader for our training set.
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

# Create the DataLoader for our validation set.
validation_data = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)

"""## 3. Train the BERT Classification Model<a class="anchor" id="sec_3"></a>

In here, we will fine tune the pre-trained BERT model to give outputs for our classification task.

<div class="alert alert-block alert-warning"><a class="anchor" id="sec_3_1"></a>
    Load pretrained BERT model of BertForSequenceClassification:
"""

from ipywidgets import IntProgress
from transformers import BertForSequenceClassification, AdamW, BertConfig

# load the pretrained BERT model of BertForSequenceClassification
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased", 
    num_labels = 2,   
    output_attentions = False, 
    output_hidden_states = False, 
).cuda() #use GPU

"""<div class="alert alert-block alert-warning"><a class="anchor" id="sec_3_2"></a>
    Set the AdamW optimizer & learning rate scheduler:
"""

# Create the AdamW optimizer
optimizer = AdamW(model.parameters(),lr = 2e-5,eps = 1e-8 )

from transformers import get_linear_schedule_with_warmup

# Set the number of epochs
epochs = 4

# Set the total steps which is the number of batches * number of epochs
total_steps = len(train_dataloader) * epochs

# Create the learning rate scheduler.
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps = 0,num_training_steps = total_steps)

"""<div class="alert alert-block alert-warning"><a class="anchor" id="sec_3_3"></a>
    Training and Evalution:
    
    In training:
    
    1. Unpack our data inputs and labels
    
    2. Load data onto the GPU for acceleration
    
    3. Clear any previously calculated gradients out.
    
    4. Perform a forward pass 
    
    5. Perform a backward pass to calculate the gradients
    
    6. Update parameters
    
    7. Track variables for monitoring progress
    
    
    In Evaluation:
    
    1. Unpack our data inputs and labels
    
    2. Load data onto the GPU for acceleration
    
    3. Perform a forward pass 
    
    4. Compute loss on validation data and track variables for monitoring progress
"""

import numpy as np

# define the flat_accuracy function to calculate the accuracy of predictions vs labels
def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return np.sum(pred_flat == labels_flat) / len(labels_flat)

import time
import datetime

# Define the format_time function to calculate the spending time
def format_time(elapsed):

    # Round to the nearest second.
    elapsed_rounded = int(round((elapsed)))
    
    # Format as hh:mm:ss
    return str(datetime.timedelta(seconds=elapsed_rounded))

import random

# set the seed value to make the result repoducible
seed_val = 25

random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

# create the loss_values to store the average loss
loss_values = []

# for loop for each epochs
for epoch_i in range(0, epochs):
    
    # The training step:   
    print("")
    print('======= Epoch {:} / {:} ======='.format(epoch_i + 1, epochs))
    print('Training...')

    # set t0 to get the time
    t0 = time.time()
    # reset the total loss as zero
    total_loss = 0

    # set the model into training mode
    model.train()

    for step, batch in enumerate(train_dataloader):
        # unpack data inputs, masks, and labels onto the GPU for acceleration
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        # clear any previously calculated gradients out.
        model.zero_grad()        
        # Perform a forward pass (it will return the loss)
        outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels) 
        # get the loss value
        loss = outputs[0]
        # accumulate the training loss
        total_loss += loss.item()
        # perform a backward pass to calculate the gradients.
        loss.backward()
        # Clip the norm of the gradients to 1.0.
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # update parameters
        optimizer.step()
        # update the learning rate.
        scheduler.step()

    # calculate the average loss
    avg_train_loss = total_loss / len(train_dataloader)            
    # append the average loss to loss_values list.
    loss_values.append(avg_train_loss)

    print("")
    print("  Average training loss: {0:.2f}".format(avg_train_loss))
    print("  Training epcoh took: {:}".format(format_time(time.time() - t0)))
        
    
    
    
    # The Evalution step:
    print("")
    print("Running Validation...")

    t0 = time.time()

    # set the model into evalution mode.
    model.eval()

    # set the tracking variables 
    eval_loss, eval_accuracy = 0, 0
    nb_eval_steps, nb_eval_examples = 0, 0

    for batch in validation_dataloader:        
        # add batch onto GPU
        batch = tuple(t.to(device) for t in batch)        
        # unpack data inputs, masks, and labels
        b_input_ids, b_input_mask, b_labels = batch
        
        # no gradients are calculated
        with torch.no_grad():        
            # Perform a forward pass (it will return the logit predictions)
            outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
        
        # get the logit predictions
        logits = outputs[0]

        # move the logits predictions and labels to CPU
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        
        # calculate the accuracy 
        tmp_eval_accuracy = flat_accuracy(logits, label_ids)
        
        # accumulate the total accuracy.
        eval_accuracy += tmp_eval_accuracy

        # track the number of batches
        nb_eval_steps += 1

    print("  Accuracy: {0:.2f}".format(eval_accuracy/nb_eval_steps))
    print("  Validation took: {:}".format(format_time(time.time() - t0)))

print("")
print("Training complete!")

"""## 4. Test BERT Classification Model<a class="anchor" id="sec_4"></a>

<div class="alert alert-block alert-warning"><a class="anchor" id="sec_4_1"></a>
    Prepare the test data for BERT classification model:
"""

import pandas as pd

# read the test data.
df = pd.read_csv("test_final.csv")

# get the sentences from test data
sentences = df.comment.values

# tokenize all of the sentences and map the tokens to thier word IDs.
input_ids = []

for sent in sentences:
    # encode the sentence and add [CLS] and [SEP]
    encoded_sent = tokenizer.encode(str(sent), add_special_tokens = True,)
    # append the encoded_set to input_ids list
    input_ids.append(encoded_sent)
    
# pad our input tokens
input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

# set list of attention masks
attention_masks = []

for seq in input_ids:
    # if token ID is 0, set the mask to 0, others set the mask to 1
    seq_mask = [float(i>0) for i in seq]
    # append attention mask to attention_masks list
    attention_masks.append(seq_mask) 

# Convert all inputs and masks into torch tensors
prediction_inputs = torch.tensor(input_ids)
prediction_masks = torch.tensor(attention_masks)


# set the batch_size as 32 
batch_size = 32  

# Create the DataLoader for our test data set.
prediction_data = TensorDataset(prediction_inputs, prediction_masks)
prediction_sampler = SequentialSampler(prediction_data)
prediction_dataloader = DataLoader(prediction_data, sampler=prediction_sampler, batch_size=batch_size)

"""<div class="alert alert-block alert-warning"><a class="anchor" id="sec_4_2"></a>
    Get the prediction on test data set:
"""

# set the model into the evaluation mode
model.eval()

# set the predictions list 
predictions = []

for batch in prediction_dataloader:
    # add batch to GPU
    batch = tuple(t.to(device) for t in batch)
    # unpack data inputs, and masks
    b_input_ids, b_input_mask = batch
  
    # no gradients are calculated
    with torch.no_grad():
        # Perform a forward pass (it will return the logit predictions)
        outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
    
    # get the logit predictions
    logits = outputs[0]
    # move the logits predictions to CPU
    logits = logits.detach().cpu().numpy()
  
    # append the logits prediction to preictions list
    predictions.append(logits)
    
# get the flat predictions
flat_predictions = [item for sublist in predictions for item in sublist]
flat_predictions = np.argmax(flat_predictions, axis=1).flatten()

"""<div class="alert alert-block alert-warning"><a class="anchor" id="sec_4_3"></a>
    Get the final gender prediction:
    
    In this step we will combine the 100 twitter prediction to one final gender prediction for each userID.
    
    For example, if the userID has 100 twitter comments, and the BERT classifiction model predict there are 70 comments are male in these 100 twitter comments, then we final consider this userID is male.
"""

# define the final_gender_prediction to get the final prediction.
def final_gender_prediction(labels):
    if labels >=0.5:
        return 1
    elif labels<0.5:
        return 0

ID=df['id'].values
pred_df=pd.DataFrame({'id':ID,'flat_label':flat_predictions})
pred_df=pred_df.groupby('id').mean()

# use the final_gender_prediction function to get the prediction.
pred_df['Pred_label']=pred_df.apply(lambda x: final_gender_prediction(x.flat_label),axis=1)

# read the original test data
test = pd.read_csv("test.csv")
# drop the columns of gender and language
test=test.drop(columns=['gender','language'])
# merge the test dataframe and pred_df dataframe on id to final dataframe
final=pd.merge(test,pred_df, on='id')
# rename the columns
final=final.rename(columns={"Pred_label": "gender"})
#drop the column of flat_label
final=final.drop(columns=['flat_label'])
final=final[['id','gender']]

"""<div class="alert alert-block alert-warning"><a class="anchor" id="sec_4_4"></a>
    Evaluation the accuracy of test data:
"""

from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix, matthews_corrcoef
import pandas as pd
import numpy as np

# read the test_labels.csv
df_anwser=pd.read_csv('test_labels.csv')

# change the label into 0(femal) or 1(male)
df_anwser['label']=df_anwser.apply(lambda x: get_gender(x.gender),axis=1)

# get the predict labels and test labels
predict_labels = final.gender.tolist() 
test_labels = df_anwser.label.tolist() 
predict_label=np.asarray(predict_labels)
test_label=np.asarray(test_labels)

print(confusion_matrix(test_labels,predict_labels))
recall=recall_score(test_labels,predict_labels,average='macro')
precision=precision_score(test_labels,predict_labels,average='macro')
f1score=f1_score(test_labels,predict_labels,average='macro')
accuracy=accuracy_score(test_labels,predict_labels)
matthews = matthews_corrcoef(test_labels,predict_labels) 
print('Accuracy: '+ str(accuracy))
print('Macro Precision: '+ str(precision))
print('Macro Recall: '+ str(recall))
print('Macro F1 score:'+ str(f1score))
print('MCC:'+ str(matthews))

"""<div class="alert alert-block alert-warning">
    Save the final reslut to pred labels.csv:
"""

# define the gender function to conver the label to femal or male
def final_gender(label):
    if label ==0:
        gender='female'
        return gender
    elif label ==1:
        gender='male'
        return gender

# change the gender into female or male
final['label']=final.apply(lambda x: final_gender(x.gender),axis=1)
final=final.drop(columns=['gender'])
final=final.rename(columns={"label": "gender"})

# ouput as csv file
final.to_csv('pred_labels.csv',index=False)