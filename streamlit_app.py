import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter

st.set_page_config(page_title="Eurostar chatbot", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.OPENAI_KEY
st.title("Hello, I am the Eurostar Bot 🤖.")
st.info("To protect your privacy, please don’t mention any personal information unless I ask you specifically.")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Write a message ..."}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Eurostar docs."):
        docs = SimpleDirectoryReader(input_dir="./html_files", recursive=True).load_data()
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
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): 
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            print(f"response-> {response}")
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
