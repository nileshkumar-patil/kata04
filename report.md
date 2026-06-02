# News Summarization Tool - Development Report

## 1. Process of Integrating the LLM API
For this tool, we chose the **Google Gemini API** (`gemini-1.5-flash`), accessed via the `google-generativeai` Python SDK. The integration process involved:
- **Authentication**: Implementing an environment variable approach (`.env`) to securely load the `GEMINI_API_KEY`.
- **Prompt Engineering**: Designing a clear, multi-part prompt that instructs the LLM to (1) summarize the provided text concisely, (2) determine the category (`articleType`), and (3) output the exact JSON structure requested (`date`, `summary`, `articleType`).
- **Data Parsing**: We used `json.loads` to safely parse the response and automatically handled cases where the LLM might return Markdown JSON blocks (e.g., stripping ```json and ``` tags).
- **Secondary Feature (Answering Questions)**: We passed the historically generated JSON data back into a secondary Gemini prompt, instructing it to act as an assistant that bases its answers strictly on the provided JSON context.

## 2. Extracting and Processing Article Content
To extract content, the tool uses **Trafilatura**, a robust Python library designed to parse HTML pages and extract the main article text while ignoring boilerplate elements like navbars, sidebars, and ads.
- **Fetching**: The `fetch_url` function is used to securely download the raw HTML from the target URL.
- **Parsing**: `trafilatura.extract` is used to get clean, unformatted text suitable for LLM processing. `trafilatura.extract_metadata` is also used to attempt to locate the publication date from the HTML meta tags; if none is found, the current date is utilized as a fallback.
- **Handling Failure**: The tool implements basic error handling to terminate execution gracefully if the URL is invalid or Trafilatura fails to extract the core text.

## 3. Approach to Managing API Usage Costs
When utilizing paid LLMs, keeping token usage low is critical. In this implementation:
- **Client-Side HTML Stripping**: By using Trafilatura instead of passing raw HTML to the LLM, we drastically reduce the token count per request. Only the core article text is passed as prompt context.
- **Model Selection**: We opted for `gemini-1.5-flash` rather than the larger, more expensive `pro` models. Flash models are highly capable of straightforward summarization tasks and categorization while being significantly faster and cheaper.
- **Local Caching**: The generated summaries are stored locally in `articles.json`. If a user needs to review past summaries, they don't have to re-summarize the URL. When the user uses the `ask` command, we only pass the *summarized* context (which is very short) rather than the original full-length articles, heavily saving on token usage for Q&A tasks.

## 4. Challenges Encountered and Potential Improvements
### Challenges
- **Strict JSON Enforcement**: LLMs often try to be helpful by adding conversational text or Markdown formatting around their JSON output. Ensuring the script robustly strips this extraneous formatting before parsing was necessary.
- **Date Extraction**: HTML meta tags are not uniform across news sites. Relying entirely on Trafilatura for date extraction occasionally yields `None`. Falling back to the current date was implemented as a simple workaround.

### Potential Improvements for Future Versions
- **Asynchronous Processing**: Currently, summarizing multiple articles requires running the script sequentially. Implementing `asyncio` could speed up bulk processing.
- **Database Backend**: Moving away from a flat `articles.json` file to a proper database (like SQLite or a NoSQL database) would allow for better searchability, scalability, and safer concurrent writes.
- **Vector Database & RAG**: As the `articles.json` file grows, passing the entire JSON array to the LLM for the `ask` command will eventually hit the context window limit. Implementing Retrieval-Augmented Generation (RAG) using a vector database (e.g., ChromaDB) would allow the tool to only query the most relevant articles when answering questions.
