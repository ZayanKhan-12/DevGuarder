import os
from fastapi import FastAPI, HTTPException, File, UploadFile
import requests
import json
import logging
from bs4 import BeautifulSoup

# Initialize FastAPI app
app = FastAPI()

# Hyperbolic API Key (make sure to set it securely, e.g., environment variable)
API_KEY_HYP = ""

# Set up logging to get detailed error information
logging.basicConfig(level=logging.DEBUG)

# Endpoint for the POST request to analyze webpage HTML content from an uploaded file
@app.post("/analyze-installation/")
async def analyze_installation(file: UploadFile = File(...)):
    try:
        # Read the uploaded HTML file content
        logging.debug(f"Received file: {file.filename}")
        html_content = await file.read()
        html_content_str = html_content.decode('utf-8')  # Convert bytes to string
        logging.debug(f"File content: {html_content_str[:200]}...")  # Log the first 200 characters for preview

        # Create a prompt that asks Hyperbolic API to analyze the HTML content for installation vulnerabilities
        prompt = f"""Analyze the following HTML content for installation instructions. Provide a trust rating (out of 100%) and any insights or vulnerabilities detected in the code, along with suggested fixes if any. If the content is safe, say 'Safe! Good to go!' output it like {{ rating: "a number out of 100", analysis: "bullet points, if no concern, just say "Safe! Good to go!"", fix: "potential fix and stuff, if none, make it None type"}} where it looks like a json
        basically the goal is the example output of a malicious installation guide will look like this {{ rating: "10", analysis: ["the code contains malicious code due to blah blah blah", "It is recommended that... blah blah blah", and etc.],
        fix: "it is recommended that ..." }}
        you can act like you're reading the webpage and everything about it. Act like you're talking to the user thats supposed to run these commands
        follow the prompt's format. dont output anything else. Here the code:
        \n{html_content_str}"""

        # Hyperbolic API URL and request headers
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
                    "content": "You are an interpreter. Your job is to interpret 'dialogues' from humans. The dialogues will be in the form of reports where the report contains instructions or code. Your job is to rate and analyze the security of the content based on provided HTML code."
                },
                {
                    "role": "user",
                    "content": f"""Please analyze the HTML content and provide the rating, analysis, and any suggested fixes. Output the result as a JSON with the fields 'rating', 'analysis', and 'fix'. Here is the content: {html_content_str}"""
                }
            ],
            "model": "meta-llama/Llama-3.2-3B-Instruct",  # You can adjust the model as needed
            "max_tokens": 512,
            "temperature": 0,
            "top_p": 0.9
        }

        # Send the request to Hyperbolic API
        logging.debug(f"Sending prompt to Hyperbolic API: {prompt[:200]}...")  # Log the first 200 characters of the prompt
        response = requests.post(url, headers=headers, json=data)

        # Check if the response is successful
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error from Hyperbolic API: {response.text}")

        # Get the analysis result from the response (the response will be a JSON-like string)
        analysis_result = response.json()
        logging.debug(f"Response from Hyperbolic API: {analysis_result}")

        # Return the parsed JSON directly
        return analysis_result

    except Exception as e:
        # Catch any exception and log it for debugging
        logging.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")

def get_content(url, title=False):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    query = ['head'] if title else ['script', 'style', 'noscript', 'head']


    # Extract all text content, ignoring scripts, styles, and hidden elements
    for script in soup(query):
        script.extract()

    return soup.get_text(separator=' ', strip=True)
