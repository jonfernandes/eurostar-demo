import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.postprocessor.cohere_rerank import CohereRerank
import asyncio
import nest_asyncio
nest_asyncio.apply()

import os
from nemoguardrails import RailsConfig, LLMRails

st.set_page_config(page_title="Eurostar chatbot", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.OPENAI_KEY
COHERE_API_KEY = st.secrets.COHERE_API_KEY

os.environ["OPENAI_API_KEY"] = openai.api_key

config = RailsConfig.from_path("./config")
rails = LLMRails(config)

cohere_rerank = CohereRerank(api_key=COHERE_API_KEY, top_n=2)
st.title("Hello, I am the Eurostar Bot 🤖.")
st.info("To protect your privacy, please don’t mention any personal information unless I ask you specifically.")


async def guardrails(input_text):
    try:
        result = await rails.generate_async(prompt=input_text)
        print(f"Explanation: {rails.explain().print_llm_calls_summary()}")
        return result
    except Exception as e:
        print(f"Error in guardrails function: {e}")
        return "An error occurred while processing your request."

def format_response(text):
    print(f"policy text to be formatted: {text}")
    if "yes" in text.lower():
        return "yes"
    else:
        return "no"

async def main():
    if "messages" not in st.session_state.keys(): 
        st.session_state.messages = [
            {"role": "assistant", "content": "Write a message ..."}
        ]

    @st.cache_resource(show_spinner=False)
    def load_data():
        with st.spinner(text="Loading data ..."):
            docs = SimpleDirectoryReader(input_dir="./config/kb", recursive=True).load_data() #was ./html_files
            llm = OpenAI(model="gpt-4o", 
                        temperature=0.0,
                        max_tokens=None, 
                        system_prompt="You are an expert on questions about the Eurostar and your job is to answer technical questions. Assume that all questions are related to Eurostar. Keep your answers technical and based on facts – do not hallucinate features.")
            embed_model = OpenAIEmbedding(model='text-embedding-3-large')
            text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
            service_context = ServiceContext.from_defaults(llm=llm,
                                                            embed_model=embed_model, 
                                                            chunk_size=1024, 
                                                            chunk_overlap=200)
            index = VectorStoreIndex.from_documents(docs, 
                                                    service_context=service_context,
                                                    text_splitter=text_splitter)
            return index

    index = load_data()
    print(f"index:\n {index}\n")

    if "chat_engine" not in st.session_state.keys(): 
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", 
                                                            verbose=True,
                                                            similarity_top_k=5,
                                                            node_postprocessors=[cohere_rerank])

    if prompt := st.chat_input("Your question"): 
        st.session_state.messages.append({"role": "user", "content": prompt})
        print(f"prompt-> {prompt}")
        overall_response = await rails.generate_async(prompt=prompt)
        print(f"overall_response: {overall_response}")
        print(f"rails colang history: {rails.explain().colang_history}")
        print(f"rails explain: {rails.explain()}")

        #print(f"overall results -> {overall_response}")
        #print(f"Explanation: {rails.explain().print_llm_calls_summary()}")
        print(f"Query: \n{rails.explain().llm_calls[0]}\n")
        query_response = rails.explain().llm_calls[0]
        print(f"Query Prompt: \n{query_response.prompt}\n")
        print(f"Query Completion: \n{query_response.completion}\n") #[0].completion}")
        policy_response = rails.explain().llm_calls[1]
        print(f"Policy: \n{policy_response}\n")
        print(f"Policy Prompt: \n{policy_response.prompt}\n")
        print(f"Policy Completion: \n{policy_response.completion}\n") #[0].completion}")
        formatted_policy_response = format_response(policy_response.completion) 

    for message in st.session_state.messages: 
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Retrieving data ..."):
                if formatted_policy_response == "yes":
                    st.write("I'm sorry, I can't respond to that.")
                    message = {"role": "assistant", "content": "I'm sorry I can't respond to that"}
                    st.session_state.messages.append(message)
                    formatted_policy_response = "" 
                else: 
                    response = st.session_state.chat_engine.chat(prompt)
                    print(f"response-> {response}")
                    print(f"source[0] -> {response.source_nodes[0]}")
                    print(f"source[1] -> {response.source_nodes[1]}")
                    #print(f"text-> {response.source_nodes[1].text}")
                    #print(f"metadata-> {response.source_nodes[1].metadata['file_name']}")
                    metadata = response.source_nodes[0].metadata['file_name']
                    metadata2 = response.source_nodes[1].metadata['file_name']
                    st.write(f"{response.response}  \n\n**Data source:**  \n[1] [{metadata}](https://jonfernandes.github.io/eurostar/{metadata})  \n[2] [{metadata2}](https://jonfernandes.github.io/eurostar/{metadata2})")
                    message = {"role": "assistant", "content": response.response}
                    st.session_state.messages.append(message) 

if __name__ == "__main__":
    asyncio.run(main())
