import streamlit as st

from langsearch.chains.qa import QAChain

st.title("Audio/Video Question Answering Demo")
question = st.text_input("Type your question here")
if len(question) != 0:
    chain_output = QAChain()({"question": question})
    answer = chain_output["output_text"]
    sources = set([doc.metadata["source"] for doc in chain_output["docs"]])
    st.write(answer)
    for index, source in enumerate(sources):
        st.markdown(f"[{index + 1}] [{source}]({source})")