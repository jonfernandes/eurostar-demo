import streamlit as st

#with st.chat_message("user"):
#    st.write("I'm the user - can you help me")

###########################

#with st.chat_message("assistant"):
#    st.write("I'm the bot - what is your question?")


################

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("What can I help with?"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    ###########################

    with st.chat_message("assistant"):
        response = "I'm the bot - I always have the same response"
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
