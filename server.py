from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

mcp = FastMCP("tavily-search")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"


@mcp.tool()
def search_internet(query: str, max_results: int = 5) -> str:
    """Search the internet for up-to-date information on a topic.

    Use this when you don't know the answer, the information may have changed
    after your training cutoff, or you need to enrich your response with
    current facts, news, or data.

    Args:
        query: The search query.
        max_results: Number of results to return (default 5, max 10).
    """
    max_results = min(max_results, 10)
    response = tavily.search(query=query, max_results=max_results)

    results = []
    for r in response.get("results", []):
        results.append(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Content: {r['content']}\n"
        )

    if not results:
        return "No results found."

    return "\n---\n".join(results)


@mcp.tool()
def search_internet_with_answer(query: str) -> str:
    """Search the internet and get a direct AI-generated answer with sources.

    Use this for quick factual questions where you want a concise answer
    alongside supporting sources rather than raw search results.

    Args:
        query: The question or topic to search for.
    """
    response = tavily.search(
        query=query,
        search_depth="advanced",
        include_answer=True,
        max_results=3,
    )

    answer = response.get("answer", "No direct answer available.")
    sources = response.get("results", [])

    output = f"Answer: {answer}\n\nSources:\n"
    for r in sources:
        output += f"- {r['title']}: {r['url']}\n"

    return output


@mcp.tool()
def ask_groq(prompt: str, model: str = GROQ_MODEL) -> str:
    """Send a prompt directly to a Groq-hosted LLM and get a response.

    Use this for reasoning, summarization, code generation, or any task
    that benefits from fast LLM inference without needing live web data.

    Args:
        prompt: The message or question to send to the model.
        model: Groq model to use (default: llama-3.3-70b-versatile).
    """
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


@mcp.tool()
def search_and_summarize(query: str, max_results: int = 5) -> str:
    """Search the internet and summarize the results using Groq.

    Use this when you need current information presented as a clean,
    concise summary rather than raw search snippets.

    Args:
        query: The topic or question to research and summarize.
        max_results: Number of search results to feed into the summary (default 5, max 10).
    """
    max_results = min(max_results, 10)
    response = tavily.search(query=query, max_results=max_results)

    results = response.get("results", [])
    if not results:
        return "No search results found."

    context = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        for r in results
    )

    prompt = (
        f"Based on the following search results, provide a concise and accurate "
        f"summary answering: {query}\n\nSearch Results:\n{context}"
    )

    groq_response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    summary = groq_response.choices[0].message.content

    sources = "\n".join(f"- {r['title']}: {r['url']}" for r in results)
    return f"{summary}\n\nSources:\n{sources}"


if __name__ == "__main__":
    mcp.run()
