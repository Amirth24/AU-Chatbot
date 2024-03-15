"""A module for class `ChatAgent`"""
from typing import List
from langchain.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.llms.ollama import Ollama

SYSTEM_MESSAGE = """You're a AI bot built to answer questions about \
a university. Converse with the user for the provided context

Context: {context}
"""


class ChatAgent():
    def __init__(self, vec_db: Chroma, init_sys_msg: str = SYSTEM_MESSAGE):
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=init_sys_msg),
            MessagesPlaceholder(variable_name="messages")
        ])

        self.client = Ollama(model="tinyllama")
        self.chain = (
                RunnableParallel({
                    "context": vec_db.as_retriever(search_type="mmr"),
                    "messages": RunnablePassthrough()
                    })
                | self.prompt
                | self.client
                | StrOutputParser()
                )

    async def talk(self, messages: List[BaseMessage]):
        """Returns the async stream of llm's output."""
        await self.chain.ainvoke(messages)


if __name__ == "__main__":
    from langchain.memory import ChatMessageHistory
    import asyncio

    async def main(db, chatbot, mess_his):
        while True:
            mess = input(">>>")
            mess_his.add_user_message(mess)
            ai_mess = await chatbot.talk(mess_his.messages)
            mess_his.add_ai_message(ai_mess)
            print(ai_mess)

    db = Chroma()
    chatbot = ChatAgent(db)
    mess_his = ChatMessageHistory()

    asyncio.run(main(db, chatbot, mess_his))
