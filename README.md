# News Summarization Tool

This is a command-line application that leverages Large Language Models (LLMs), specifically Google's Gemini API, to provide concise summaries of news articles. It allows users to summarize articles from URLs, automatically categorize them, and store the metadata (date, summary, articleType) in a local JSON file. It also provides an interactive way to query and ask questions about the saved summaries.

## Prerequisites

- Python 3.8 or higher.
- A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/).

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd kata04
   ```

2. **(Optional but recommended) Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API Key:**
   - Copy the `.env.example` file to a new file named `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open the `.env` file and replace `your_gemini_api_key_here` with your actual Google Gemini API key.

## Usage

The tool provides two main commands: `summarize` and `ask`.

### 1. Summarizing an Article

Use the `summarize` command followed by the URL of the news article you want to process.

```bash
python3 news_tool.py summarize "https://example.com/news/article"
```

**What it does:**
- Downloads the article content using `trafilatura`.
- Extracts the main text and metadata (like the date).
- Sends the text to the Gemini API to generate a summary and categorize the article type.
- Saves the extracted information into `articles.json` in the following format:
  ```json
  {
      "date": "1st April 2024",
      "summary": "This is the generated summary of the news article.",
      "articleType": "technology"
  }
  ```

### 2. Asking Questions

Once you have summarized a few articles, you can ask questions based on the accumulated data.

```bash
python3 news_tool.py ask "What are the main topics discussed in the financial articles?"
```

**What it does:**
- Loads the contents of `articles.json`.
- Sends the stored summaries and your question to the Gemini API.
- Outputs the answer based strictly on the stored knowledge base.

## Files Structure

- `news_tool.py`: The main Python script containing the CLI logic.
- `requirements.txt`: Python package dependencies.
- `.env.example`: Template for environment variables.
- `report.md`: A brief report covering the project's development, API integration, and challenges.
- `articles.json`: (Created dynamically) Stores the summarized article data.
