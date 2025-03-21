# -*- coding: utf-8 -*-

import numpy as np
import pickle
import streamlit as st
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

port_stem = PorterStemmer()


# loading the saved model
loaded_model = pickle.load(open("D:/ML_deployment/Fake_news/fake_news.sav", 'rb'))
loaded_vectorizer = pickle.load(open("D:/ML_deployment/Fake_news/vector.sav", 'rb'))


data = pd.DataFrame(columns=['Title', 'Author', 'Text'])

# Function to add a new entry to the DataFrame
def add_entry(title, author, text):
    global data
    new_entry = pd.DataFrame({'Title': [title], 'Author': [author], 'Text': [text]})
    data = pd.concat([data, new_entry], ignore_index=True)

#Checking nan values
def nan_value(data):
    return data.fillna('')
    
# Creating content column
def content(data):
    data['content'] = data['Author']+' '+data['Title']
    return data
    
#Porter streammer
def stemming(content):
    stemmed_content = re.sub('[^a-zA-Z]',' ',content)
    stemmed_content = stemmed_content.lower()
    stemmed_content = stemmed_content.split()
    stemmed_content = [port_stem.stem(word) for word in stemmed_content if not word in stopwords.words('english')]
    return ' '.join(stemmed_content)


def prediction(input_data):

    prediction = loaded_model.predict(input_data)

    if (prediction[0]==0):
        return 'The news is Real'
    else:
        return 'The news is Fake'


def main():
    # giving a title
    st.title('Fake News web App')
    
    # getting the input data from the user       
    Title = st.text_input('What is the title')
    Author = st.text_input('Who is the Author')
    Text = st.text_input('What is the text')
    
    # Creating the DataFrame
    add_entry(Title, Author, Text)
    
    #Filling Nan values
    nan_value(data)
    
    #Creating content
    content(data)
    
    #Porter
    data['content'] = data['content'].apply(stemming)
    
    X = data['content'].values
    
    
    X = loaded_vectorizer.transform(X)
        
    
    # code for Prediction
    diagnosis = ''
    
    # creating a button for Prediction
    
    if st.button('Check news'):
        diagnosis = prediction(X)
        
        
    st.success(diagnosis)
       
if __name__ == '__main__':
    main()