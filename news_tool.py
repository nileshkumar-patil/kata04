#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

try:
    import trafilatura
    import google.generativeai as genai
except ImportError:
    print("Required packages are missing. Please run: pip install -r requirements.txt")
    sys.exit(1)

DATA_FILE = "articles.json"

def init_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Error: GEMINI_API_KEY not found or not set in .env file.")
        sys.exit(1)
    genai.configure(api_key=api_key)
    # Using gemini-1.5-flash as it is fast and efficient for text tasks
    return genai.GenerativeModel('gemini-1.5-flash')

def summarize_article(url):
    print(f"Fetching article from {url}...")
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print("Failed to download the article. Check the URL and your connection.")
        sys.exit(1)
    
    # Extract text and metadata
    metadata = trafilatura.extract_metadata(downloaded)
    text = trafilatura.extract(downloaded)
    
    if not text:
        print("Failed to extract text from the article.")
        sys.exit(1)

    # Determine date
    article_date = metadata.date if metadata and metadata.date else datetime.now().strftime("%d %B %Y")
    
    print("Article extracted. Generating summary using Gemini...")
    model = init_gemini()
    
    prompt = f"""
    You are an expert news summarizer. I will provide you with the text of a news article.
    Read the article and provide a concise summary. Also, categorize the article type (e.g., financial, technology, politics, sports, entertainment).
    The extracted date of the article is: {article_date}
    
    Article Text:
    {text}
    
    Return the result strictly as a valid JSON object with exactly the following keys:
    "date" (use the provided date or format it nicely, e.g., "1st April 2024")
    "summary" (the concise summary)
    "articleType" (the category)
    
    Do not include any Markdown formatting like ```json or ``` around the output. Just the raw JSON object.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown JSON blocks if the model still outputs them
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        parsed_json = json.loads(response_text)
        
        # Load existing data
        data = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        # Append and save
        data.append(parsed_json)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        print("\nSuccessfully summarized and saved to articles.json!")
        print(json.dumps(parsed_json, indent=4))
        
    except Exception as e:
        print(f"Error during summarization: {e}")

def ask_question(question):
    if not os.path.exists(DATA_FILE):
        print(f"No data found. Please summarize some articles first using '{sys.argv[0]} summarize <url>'.")
        sys.exit(1)
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Error: articles.json is corrupted or empty.")
            sys.exit(1)
            
    if not data:
        print("No articles to ask questions about.")
        sys.exit(1)
        
    print(f"Asking Gemini: '{question}' based on {len(data)} saved articles...")
    model = init_gemini()
    
    prompt = f"""
    You are a helpful assistant. I have a collection of news article summaries in JSON format.
    Based strictly on the following JSON data, answer the user's question.
    If the answer cannot be found in the provided JSON data, politely say that you don't have enough information based on the saved articles.
    
    JSON Data:
    {json.dumps(data, indent=2)}
    
    User Question: {question}
    """
    
    try:
        response = model.generate_content(prompt)
        print("\nAnswer:")
        print(response.text.strip())
    except Exception as e:
        print(f"Error during question answering: {e}")

def main():
    parser = argparse.ArgumentParser(description="LLM-based News Summarization Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize a news article from a URL")
    summarize_parser.add_argument("url", type=str, help="The URL of the news article")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question based on summarized articles")
    ask_parser.add_argument("question", type=str, help="The question to ask")
    
    args = parser.parse_args()
    
    if args.command == "summarize":
        summarize_article(args.url)
    elif args.command == "ask":
        ask_question(args.question)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
