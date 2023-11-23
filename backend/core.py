import os

from typing import Any, List, Dict

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone
import pinecone

from consts import INDEX_NAME

PINECONE_API_KEY='b32d298b-1cae-446f-9306-2d13539791df'
PINECONE_ENVIRONMENT_REGION='gcp-starter'

pinecone.init(
    # api_key='b32d298b-1cae-446f-9306-2d13539791df',
    # environment='gcp-starter',
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENVIRONMENT_REGION"],
)

#OPENAI_API_KEY='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'

def run_llm(query: str, chat_history: List[Dict[str, Any]]=[]) -> Any:

    # embeddings = OpenAIEmbeddings()
    embeddings = OpenAIEmbeddings(openai_api_key='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')

    docsearch = Pinecone.from_existing_index(
        index_name=INDEX_NAME, embedding=embeddings
    )
    #chat = ChatOpenAI(verbose=True, temperature=0)
    chat = ChatOpenAI(verbose=True, temperature=0, openai_api_key='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')

    qa = ConversationalRetrievalChain.from_llm(
        llm=chat, retriever=docsearch.as_retriever(), return_source_documents=True
    )

    return qa({"question": query, "chat_history": chat_history})


if __name__ == "__main__":
    print(run_llm(query="What is LangChain?"))
