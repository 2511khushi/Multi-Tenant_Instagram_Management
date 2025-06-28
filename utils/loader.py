import requests
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
import tempfile
import os

def load_document_from_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    file_ext = url.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_ext) as tmp_file:
        tmp_file.write(response.content)
        tmp_file.flush()

        if file_ext == "pdf":
            loader = PyPDFLoader(tmp_file.name)
        elif file_ext in ["docx", "doc"]:
            loader = UnstructuredWordDocumentLoader(tmp_file.name)
        elif file_ext in ["txt", "html"]:
            loader = TextLoader(tmp_file.name)
        else:
            raise ValueError("Unsupported file type: " + file_ext)

        docs = loader.load()
        os.unlink(tmp_file.name)

        content = "\n".join([doc.page_content for doc in docs])
        return content
