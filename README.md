# Eurostar demo
Build a chatbot powered by LlamaIndex that augments GPT 3.5 with the contents of the Streamlit docs (or your own data).

## Pre-processing
- Excel document converted to html files
- Removed all files with titles starting "ILOYAL*", "PSP*", "INC*", "EURO*", "SBE*" as they were not relevant to a customer-facing knowledge base
- Calculated the number of tokens for the messages and got the following distribution

![Distribution of number of tokens](images/num_tokens_histogram.png)
![Distribution of number of tokens (percentages)](images/num_tokens_percentage.PNG)

### Chunking
Instead of trying to implement a complicated chunking strategy (e.g. splitting by every logical section / paragraph), given the distribution of the number of tokens in each of the files (95%+ is less than 1000 tokens), a sensible approach would be:
- Chunk data at 1000 tokens with an overlap of 200.
- Chunk data at 6000 tokens. Many embedding models have a context length of 8192 so viable.

## Results of unit testing

## Future development

## Demo App

Once the app is loaded, enter your question about the Streamlit library and wait for a response.
![Eurostar App](https://update this.streamlit.app/)
