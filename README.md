# Classification-BERT

The aim of this challenge is to develop a classifier that can assign a set of twitter texts to their corresponding labels. In this task, I will focus on the gender classification task, where I  develop a classifier that can identify the gender of the tweet’s author as accurate as possible.

## What is BERT?

BERT (Bidirectional Encoder Representations from Transformers), released in late 2018, is the model we will use in this tutorial to provide readers with a better understanding of and practical guidance for using transfer learning models in NLP. BERT is a method of pretraining language representations that was used to create models that NLP practicioners can then download and use for free. You can either use these models to extract high quality language features from your text data, or you can fine-tune these models on a specific task (classification, entity recognition, question answering, etc.) with your own data to produce state of the art predictions.

This post will explain how you can modify and fine-tune BERT to create a powerful NLP model that quickly gives you state of the art results. 


## Analysis code

Key elements of the analysis code are as follows:
- *Gender_Classifiction_Bert.ipynb* - a Python script used to build the gender classifier with BERT.
- *data.zip* - a zip file contains 3,600 twitter texts for those authors, which acts as the training and testing data.
- *train_labels.csv* – a csv file contains training ids and gender. It contains twitter posts from 3,100 authors and acts as the training data.
- *test_labels.csv* - a csv file contains test ids and gender. It contains the twitter posts from 500 authors.


## Authors

Tangwei, Hung

## Contact
hung.tangwei@gmail.com




