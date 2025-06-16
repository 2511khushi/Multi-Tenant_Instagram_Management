import requests

def fetch_comments(post_id: str, access_token: str):
    url = f"https://graph.facebook.com/{post_id}/comments?access_token={access_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def fetch_replies(comment_id: str, access_token: str):
    url = f"https://graph.facebook.com/{comment_id}/replies?access_token={access_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching replies: {e}")
        return []
