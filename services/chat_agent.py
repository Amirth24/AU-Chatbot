"""A module for class `ChatAgent`"""
from langchain.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate,
                                    PromptTemplate)

SYSTEM_MESSAGE = """You're a AI bot built to answer questions about \
a university. Converse with the user for the provided context

Context: {context}
"""


class ChatAgent():
    def __init__(self, vec_db: Chroma, init_sys_msg: str = SYSTEM_MESSAGE):
        self.client = ChatGoogleGenerativeAI(
                model="gemini-pro",
                convert_system_message_to_human=True,
                stream=True)
        sys_prompt = SystemMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["context"],
                    template=init_sys_msg
                    )
                )
        human_prompt = HumanMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["question"],
                    template="{question}"
                    )
                )
        self.prompt = ChatPromptTemplate(
                input_variables=["context", "question"],
                messages=[
                    sys_prompt, human_prompt
                    ]
                )

        self.chain = (
                RunnableParallel({
                        "context": vec_db.as_retriever(search_type="mmr"),
                        "question": RunnablePassthrough()
                })
                | self.prompt
                | self.client
                | StrOutputParser()
                )

    def talk(self, question):
        """Returns the async stream of llm's output."""
        return self.chain.stream(question)


if __name__ == "__main__":
    from functools import reduce
    from langchain.memory import ChatMessageHistory
    from langchain.document_loaders import TextLoader
    from langchain_text_splitters import CharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    def main(db, chatbot, mess_his):
        while True:
            mess = input(">>>")
            ai_mess = chatbot.talk(mess)
            for chr in ai_mess:
                print(chr, end='')
            print()

    print("Starting Client")
    print("Loading Database")
    files = ['B.E_CS_(AI&ML)Handbook_R2021.txt']

    files = list(map(lambda x: TextLoader('documents/'+x), files))
    splitter = CharacterTextSplitter('\n', chunk_size=1000, chunk_overlap=0)
    docs = list(map(lambda x: splitter.split_documents(x.load()), files))
    docs = reduce(lambda x, y: x+y, docs)
    db = Chroma(
            persist_directory="chroma_data/",
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            )

    print("Loaded Database")
    chatbot = ChatAgent(db)
    mess_his = ChatMessageHistory()

    main(db, chatbot, mess_his)
