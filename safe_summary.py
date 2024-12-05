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

with open('categories_no_hyphens.txt', 'r') as file:
    content = file.read()


# st.markdown(content)

query=st.text_input("Input a query that you want to ask")

if st.button("Show me the insights"):
    system_prompt=f'''
        You are given a query, based on that query suggest some saas products.
        If the query demands only some specific product then output that product only.
        When the query demands a more general overview then output both suggested products and categories.
        You can use g2.com for browsing and suggesting softwares

        **The categories should exactly be choosen from the list of categories provided below meaning word to word,and not made artificially **
        **Go through the list of categories below and find categories that can help us answer this query and output that only, dont make up anything artificially**
        **Output the exact category as mentioned in the list and do not modify it at all**

        **start of list of categories**

        {content} 

        **end of list of categories**

        Example1: query:"Tell me more about asana"
                  Expected Output:{{'Product':['asana']}}

        Example2: query:"Suggest me some apps which are good for video confrencing"
                  Expected Response:{{'Product':['Zoom','Microsoft Teams','slack','google meet'],'Category':['video conferencing']}}

        Example3: query:"Suggest me some apps which are good for cyber security"
                  Expected Response:{{'Product':['Norton','McAfee','Bitdefender','Kaspersky','CrowdStrike'],'Category':['cybersecurity consulting','cybersecurity professional development']}}
        
        Example4: query:"Suggest me some apps for device management"
                  Expected Output:{{'Product':['Jamf','ManageEngine','Microsoft Intune','VMware Workspace ONE'],'Category':['mobile device management mdm','iot device management platforms']}}
        
        Example5: query:"Suggest me products similar to OfficeSpace"
                  Expected Output:{{'Product':['FMX','UpKeep','Hippo CMMS'],'Category':['facility management software']}}
        
        if you find any query irrelevant to the idea of getting answer to their saas product needs then handle it like this 
        Example6: query:"Suggest me some horror film"
                  Expected Output:{{'Product':['irrelevant'],'Category':['irrelevant']}}
        '''

    response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use "gpt-3.5-turbo" or "gpt-4" based on your need
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
    st.markdown(response['choices'][0]['message']['content'])
