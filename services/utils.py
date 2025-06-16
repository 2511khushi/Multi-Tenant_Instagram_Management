from langchain.text_splitter import RecursiveCharacterTextSplitter

def format_comment_thread(comment_text: str, replies: list):
    formatted = f"Comment: \"{comment_text}\"\nReplies:\n"
    for reply in replies:
        reply_text = reply.get("text", "").strip()
        if reply_text:
            formatted += f"- {reply_text}\n"
    return formatted

def split_document(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=160)
    return splitter.create_documents([text])
