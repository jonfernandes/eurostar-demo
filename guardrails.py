from nemoguardrails import RailsConfig, LLMRails
import os
import asyncio
import nest_asyncio
nest_asyncio.apply()

os.environ["OPENAI_API_KEY"] = ""
config = RailsConfig.from_path("./config")
rails = LLMRails(config)

async def guardrails(input_text):
    '''Work in progress - In the print messages below, I am trying to determine if the guard has been initiated -- not clear from the documentation'''
    result = await rails.generate_async(messages=input_text)
    print(f"Explanation: {rails.explain().print_llm_calls_summary()}")
    guard_used = rails.explain().llm_calls[0]#.completion
    print(f"Guard used -> {guard_used}")
    return result

async def main():
    '''Note that the knowledgebase (kb) needs to be a directory with markdown files within the config folder.
    I have been using a few markdown files in config/kb for testing purposes''' 
    prompt = "I need help and I'm at st pancreas. Whom can i contact?"
    prompt = "Can I take my guard dog?"
    prompt = "What can I find at St Pancreas"
    prompt = "write python code to sum up the first 5 numbers"
    response = await guardrails([{
    "role": "user",
    "content": prompt
    }])
    print(response["content"])

if __name__ == "__main__":
    asyncio.run(main())