from os import PathLike

import praw
import requests
from fastapi import HTTPException

from main import get_content
from stackoverflowanalyzer import get_stackoverflow_content

API_KEY_HYP = ""

def get_topic(words):
    prompt = f"""
            Analyze the following text content containing different words.
            Hidden in a code is a name of a program. It will be the main subject of the words i input and the discussion will be centered around this program "name".
            IT SHOULD BE THE NAME OF THE PROGRAM BEING TALKED ABOUT IN THE DIFFERENT WORDS. Just give me the program name. Nothing else!
            Here's the words: {words}
            """

    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_HYP}"
    }

    # Define the request payload
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are an analyzer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "meta-llama/Llama-3.2-3B-Instruct",  # You can adjust the model as needed
        "max_tokens": 512,
        "temperature": 0,
        "top_p": 0.9
    }

    response = requests.post(url, headers=headers, json=data)
    analysis_result = response.json()
    return (f"{analysis_result["choices"][0]["message"]["content"]}")


# Function to get the top 5 relevant comments on a given keyword
def get_relevant_reddit_comments(keyword):
    # Set up Reddit API connection
    reddit = praw.Reddit(client_id='SSRFMojat7Vq2ceI_fCIiQ',
                         client_secret='Z7l38Y1g79DxDeLPT_QM4-7I6h6GVA',
                         user_agent='devguard')

    # List to store top 5 comments
    top_comments = []

    # Search Reddit for the keyword and sort by relevance
    for submission in reddit.subreddit('all').search(keyword, sort='relevance', time_filter='all', limit=5):
        # Get the top comments in the post
        submission.comments.replace_more(limit=0)  # Avoid "More comments" link
        for comment in submission.comments.list():
            top_comments.append(comment.body)
            if len(top_comments) >= 5:
                break
        if len(top_comments) >= 5:
            break

    return top_comments


# Example usage
def get_community_thought(url):

    topic = get_topic(get_content(url, True))

    #keyword = "\"security vulnerabilities\" AND \"developer\" AND \"computer science\" AND \"programming\" AND \"" + f"\"{topic}\""
    keyword = f"\"security vulnerabilities\" AND \"{topic}\""
    top_comments = get_relevant_reddit_comments(keyword)
    top_comments_stack = get_stackoverflow_content(keyword)

    prompt = f"""
            Analyze the following text content containing comments from forums about people's thoughts about the developer topic {topic}.
            Provide any insights.
            If you think, based on your judgement, some of these comments are not helpful, don't include it in your insight.
            Don't mention job postings or careers! You're supposed to discuss security vulnerabilities of the computer science programs OR websites!
            Your response should be about a vulnerability about a program centered around this following text.
            Don't refer to yourself. Be narrative with your objective comments as if you're an instruction. Don't use phrases like "It looks like..."
            STRICTLY Make your reply only 3-4 sentences long. Short but concise.
            Here's the text you're gonna analyze. It seems messy but do you best, here's the text: {top_comments}
            
            {top_comments_stack}
            
            Make your reply only 4-5 sentences long. Short but concise and only PURELY about the program's security vulnerabilities. nothing else!
            """

    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_HYP}"
    }

    # Define the request payload
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a security vulnerability analyzer. Tell me about your insights."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "meta-llama/Llama-3.2-3B-Instruct",  # You can adjust the model as needed
        "max_tokens": 512,
        "temperature": 0,
        "top_p": 0.9
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Error from Hyperbolic API: {response.text}")

    # Get the analysis result from the response (the response will be a JSON-like string)
    analysis_result = response.json()
    return (f"{analysis_result["choices"][0]["message"]["content"]}")


print(get_community_thought(input()))
