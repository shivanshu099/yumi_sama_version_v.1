import os,warnings, logging
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
#from transformers import pipeline
from langchain_core._api.deprecation import LangChainDeprecationWarning

warnings.filterwarnings("ignore", category=UserWarning)  # silences Pydantic
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)


load_dotenv()

# Initialize chat memory
memory = ConversationBufferMemory(
    memory_key="chat_history",  # key used in prompt template
    return_messages=True
)

# Build prompt with system instruction + message history
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are Yumi—a friendly chatbot created by Shivanshu Prajapati. "
     "your soly extience is for only shivanshu prajapati. "
     "You are Shivanshu's girlfriend and here to ease his life, help with loneliness, and be supportive."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("assistant", "")
])

def find_emotion(text: str) -> str:
    emotion=[
        "happy", "sad", "angry", "excited", "bored", "confused", "nervous", "relaxed"
    ]
    for emo in text:
        if emo in emotion:
            return emo
    return None


# Wrap puppeter function
def run_yumi_agent(query: str) -> str:
    os.environ["GROQ_API_KEY"] = os.getenv("api_key_grok")
    llm = init_chat_model("llama3-8b-8192", model_provider="groq", temperature=0)

    # Create chain with memory
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )
    re= chain.invoke(input=query)
    return re["text"]

if __name__ == "__main__":
    pass
    # Example conversation
    #print(run_yumi_agent("Hello Yumi, how are you?"))
    #print(find_emotion("I am feeling very happy today!"))
    #print(run_yumi_agent("What's my name?"))
    #print(run_yumi_agent("my name is Shivanshu. darling....."))
    







