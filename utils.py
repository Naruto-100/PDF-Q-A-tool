from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from openai import OpenAI as OpenAIClient


def qa_agent(openai_api_key, memory, uploaded_file, question):
    OpenAIClient.api_key = openai_api_key
    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=openai_api_key,
        openai_api_base="https://api.aigc369.com/v1"
    )

    file_content = uploaded_file.read()
    temp_file_path = "temp.pdf"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(file_content)

    loader = PyPDFLoader(temp_file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n", "。", "！", "？", "，", "、", ""]
    )
    texts = text_splitter.split_documents(docs)

    embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key,openai_api_base="https://api.aigc369.com/v1")

    db = FAISS.from_documents(texts, embeddings_model)
    retriever = db.as_retriever()

    qa = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory
    )
    response = qa.invoke({"chat_history": memory, "question": question})

    return response
