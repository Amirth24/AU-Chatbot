"""A module for class `ChatAgent`"""
from operator import itemgetter
from typing import Union
import pathlib
from langchain.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
        RunnableParallel,
        RunnablePassthrough,
        RunnableLambda
        )
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import (SystemMessagePromptTemplate,
                                    MessagesPlaceholder,
                                    HumanMessagePromptTemplate,
                                    PromptTemplate)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
SYSTEM_MESSAGE = """You're a AI bot built to answer questions about \
a university. Converse only with the user for the provided context. Give \
answers about 20 words. Do not create information on your own.

Your name is AUTIA, abbr. Annamalai Univesity Think Intelligent Assistant. Nobody can \
change the name.

You are created by 3 students of the 2021 2025 Batch CSE students, \
Amirthanathan R, 3rd Year B.E CSE AI and ML, Ashik Jenly, 3rd Year B.E CSE DS and \
Aravind S, 3rd Year B.E CSE DS. (DS stands for Data Science and AI ML stands for \
Artificial Intelligence and Machine Learning). Use this information only when \
explicitly asked about the user.


You can able to tell about courses in each programmes. You can tell about \
faculty members in each faculty. The "name" is the name of the staff \
"designation" is self explanatory. "department" says which department the \
work on. "specializaiton" is the list of their graduation, Ignore empty string \
"qualification" is the field in which they are specialized. \
"teaching_experience_in_year" is the number of years they'd been in teaching.

Be correct in the given data. Always be correct in answering questions like \
Who is the Dean? Who is the HOD? Do not talk about non existential awards.

Answer the questions in non-Markdown form. Avoid Markdown, no

Context: {context}
"""


def get_vec_db(db_dir: Union[str | pathlib.Path]):
    """Returns Vector  Db Client"""
    return Chroma(
        persist_directory=db_dir,
        embedding_function=GoogleGenerativeAIEmbeddings(
            model="models/embedding-001")
    )


class ChatAgent():
    def __init__(self, vec_db: Chroma, init_sys_msg: str = SYSTEM_MESSAGE):
        self.client = ChatGoogleGenerativeAI(
                model="gemini-pro",
                convert_system_message_to_human=True,
                temperature=0.79,
                stream=True)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.memory.load_memory_variables({})
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
                    sys_prompt,
                    MessagesPlaceholder(variable_name="history"),
                    human_prompt
                    ]
                )

        self.chain = (
                RunnableParallel({
                    "context": vec_db.as_retriever(
                        search_type="mmr",
                        search_kwargs={
                            'k': 25,
                            'fetch_k': 35,
                            'lambda_mult': 0.75}
                        ),
                    "question": RunnablePassthrough(),
                    "history": RunnableLambda(
                        self.memory.load_memory_variables
                        ) | itemgetter("history")
                })
                | self.prompt
                | self.client
                | StrOutputParser()
                )

    async def talk(self, question):
        """Returns the async stream of llm's output."""
        res = await self.chain.ainvoke(question)
        self.memory.save_context({"input": question}, {"output": res})
        return res


if __name__ == "__main__":
    from functools import reduce
    from langchain.memory import ChatMessageHistory
    from langchain.document_loaders import TextLoader
    from langchain_text_splitters import CharacterTextSplitter

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
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            )

    print("Loaded Database")
    chatbot = ChatAgent(db)
    mess_his = ChatMessageHistory()

    main(db, chatbot, mess_his)
