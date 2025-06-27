def format_comment_reply_pair(comment_text: str, reply_text: str):
    return f'User comment: "{comment_text}" → Agent reply: "{reply_text}"'

def format_comment_thread(comment_text: str, replies: list):
    formatted = f'Comment: "{comment_text}"\nReplies:\n'
    for reply in replies:
        text = reply.get("text", "").strip()
        if text:
            formatted += f"- {text}\n"
    return formatted
