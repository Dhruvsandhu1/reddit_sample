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

if not API_KEY:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize the ChatOpenAI model explicitly
llm = ChatOpenAI(
    model="gpt-4",  # Use 'ChatOpenAI' for gpt-3.5-turbo
    temperature=0.5,
    openai_api_key=API_KEY
)

# Define prompt templates
chunks_prompt1 = '''
Summarize the following text and give emphasis on pricing information,usability feedback,feature analysis,comparision to competitors if mentioned for jamf

Text: {text}
'''

final_prompt = '''
Provide the final high quality refined summary of the entire document in 5 solid points for pros and cons of jamf only
where pros are when jamf is shown in positive light and cons when jamf is shown in negative light 
both pros and cons should have mentioning of jamf and written in the perspective of jamf only
tell me the pros and cons that are crucial for the customer to make an informed decision.
refrain from saying that there is no usability feedback,pricing or datailed comparision to competitiors available
refrain from saying that you dont have any information about something

and return in json with just key as Pros and cons and value is simply a list constining the pros and cons and nothing else

Document: {text}
'''

# Create LangChain prompt templates
map_prompt_template = PromptTemplate(input_variables=["text"], template=chunks_prompt1)
final_prompt_template = PromptTemplate(input_variables=["text"], template=final_prompt)

# Streamlit UI
st.title("Jamf Reviews")

# File Upload Section


# Load JSON content
with open('jamf_senti.json', 'r') as f:
        data=json.load(f)
chunks=[]
for item in data:
     if item['useful']=='0':
          chunks.append(item['body'])
# st.write(chunks)
# Load the summarize chain with map-reduce strategy
summary_chain = load_summarize_chain(
    llm=llm,
    chain_type="map_reduce",
    map_prompt=map_prompt_template,
    combine_prompt=final_prompt_template,
    verbose=True
)
def pprint_json(data):
    for key,value in data.items():
        st.header(key)
        for elem in data[key]:
            st.write(f"-{elem}")
def check_similarity(review1,review2):
    system_prompt='''
        you are given 2 reviews in the form of 1 : review1,2 : review2
        if the there is strong reference of review1 in review2 then output 1 else output 0.
        or review 1 and review2 are highly similar then also output 1 or else output 0
        output should be 0 or 1 only.
        '''

    response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" or "gpt-4" based on your need
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"1 : {review1},2 : {review2}"}
            ],
            temperature=0.4
        )
    return response['choices'][0]['message']['content']

def give_refrence(review1,reviews):
    list1=[]
    for i in range(len(reviews)):
        if check_similarity(review1,reviews[i])=='1':
            list1.append(i)
    return list1

# Generate and display the summary
if st.button("Generate Summary"):
    supreme_dict={}
    with st.spinner("Generating Summary..."):
        refined_chunks=[]
        for i in range(len(chunks)):
            refined_chunks.append(Document(page_content=str(chunks[i])))
        # st.write(refined_chunks)
        summary = summary_chain.run(refined_chunks[:6])  # Run the summarization
        st.header("Summary of the Document")
        # st.write(summary)
        data = json.loads(summary)
        i=0
        for key,value in data.items():
            for elem in value:
                list1= give_refrence(elem,chunks[:5])#append those numbers there only and do refrencing later on 
                supreme_dict[i]=list1
                i+=1
        # st.write(supreme_dict)  
        i=0
        for key,value in data.items():
            st.header(key)
            for elem in value:
                formatted_values = ", ".join([f"[{val+1}](#{val})" for val in supreme_dict[i]])
                st.markdown(f"- {elem} {formatted_values}")
                i+=1
        st.markdown("______________")
        with open("sentiment_insights.json", "r") as json_file:
            file = json.load(json_file)
        i=0
        for elem in file:
            flag=0
            if elem['useful'] == '0':  # Display reviews marked as '0'
                if elem['body']=="":
                    flag=1
                if 'title' in elem and flag==0:
                    st.markdown(elem['title'])
                st.markdown(f"Platform : Reddit/{elem['subreddit']} | {elem['created'].split()[0]} | [Open Review]({elem['url']}) | Upvotes : {elem['upvotes']}")
                sample_para=elem['body']
                if flag==1:
                    sample_para=elem['title']
                para1 = sample_para.replace('\n', '<br>')
                para = para1.replace('$', r'\$')
                if elem['sentiment']=='2':
                    st.markdown(
                                f"""<a id='{i}'></a>
                                <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                                    <p style="color: #155724; font-size: 16px; margin: 0;">{para}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                elif elem['sentiment']=='4':
                    st.markdown(
                                f"""<a id='{i}'></a>
                                <div style="background-color: #cce5ff; padding: 10px; border-radius: 5px;">
                                    <p style="color: #004085; font-size: 16px;">{para}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                else:
                    st.markdown(
                                f"""<a id='{i}'></a>
                                <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px;">
                                    <p style="color: #721c24; font-size: 16px;">{para}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                st.markdown("______________________")
                i+=1
