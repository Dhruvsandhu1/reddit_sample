import streamlit as st
import json
import os
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
import openai
from langchain_core.documents import Document

# Set or retrieve the OpenAI API key (environment variable or direct value)
key1=st.secrets["OPENAI_API_KEY"]
API_KEY = os.getenv("OPENAI_API_KEY", key1)  # Replace if testing locally
OPENAI_API_KEY = key1
openai.api_key = key1

with open('categories.txt', 'r') as file:
    content = file.read()

query=st.text_input("Input a query that you want to ask")

if st.button("Show me the insights"):
    system_prompt='''
        You are given a query, based on the query you have to fill in the following details -+
             
        intent=[]
        feature=[]
        Below you are given a list of categories
        Each category has many saas products in it 
        {content}
        The output should be product=[],category=[],intent=[],feature=[]

        Example 1: query:'Show me the list of all mdm products'
                   response:product=[],category=['master-data-management-mdm'],intent=['show all'],feature=[]

        Example 2: query:'Tell me about the customer support of jamf'
                   response:product=['jamf'],category=[],intent=['know'],feature=['customer support']

        Example 3: query:'Suggest me some apps that are suitable for startups'
                   response should include the products from your knowledge and the features should be then ['startup','cost effective'] something like this
        
        if the query matches some categorie then no need to add products from your knowledge
        The categories should be selected from the list only and not artificial.
        '''

    response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use "gpt-3.5-turbo" or "gpt-4" based on your need
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.4
        )
    st.markdown(response['choices'][0]['message']['content'])
