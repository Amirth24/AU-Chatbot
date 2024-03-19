"""This script populates the vector db"""
import glob
from functools import reduce
from pathlib import Path
from langchain_community.document_loaders import async_html, text, json_loader
from langchain_community.vectorstores.chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


BASE_URL = "https://annamalaiuniversity.ac.in/"
TEXT_DIR = Path("processed")
pages = [
    "index.php",
    "about_university.php",
]


if __name__ == "__main__":
    loaders = async_html.AsyncHtmlLoader([
            BASE_URL+page
            for page in pages
        ])

    print("File Loading")
    loaders = [loaders] + [
        text.TextLoader(file)
        for file in glob.glob(str('processed/*/*/*.txt'))
    ] + [
        json_loader.JSONLoader(
            file,
            jq_schema=".[]",
            text_content=False
        )
        for file in glob.glob('documents/**/*.json', recursive=True)
    ]
    print("No of docs:", len(loaders))

    print("Text Splitting")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )

    docs = reduce(
            lambda x, y: x + y,
            map(
                lambda x: splitter.split_documents(x.load()),
                loaders
            )
        )
    print("No of Chunks: ", len(docs))

    print("Document Processing")
    Chroma.from_documents(
        persist_directory="chroma_data",
        documents=docs,
        embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
    )
