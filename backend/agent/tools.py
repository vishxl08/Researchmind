import math
import requests
import arxiv
import wikipediaapi
from django.conf import settings
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safer_getattr
from RestrictedPython.PrintCollector import PrintCollector

def web_search_tool(query: str) -> dict:
    """Uses Serper API to perform web search."""
    api_key = getattr(settings, 'SERPER_API_KEY', '')
    if not api_key:
        return {
            "success": False,
            "content": "Serper API key is not configured in settings. Web search is disabled.",
            "source_url": "",
            "tool": "web_search"
        }
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": 5}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Serper ranks by relevance; only surface the top matches as citable content.
        # Passing every raw result through inflates the prompt and gives the writer LLM
        # more untracked URLs to draw on, which in practice made citation fabrication
        # more likely rather than less.
        results = data.get("organic", [])[:2]
        if not results:
            return {
                "success": True,
                "content": "No search results found for the query.",
                "source_url": "",
                "tool": "web_search"
            }

        output = []
        source_urls = []
        for idx, res in enumerate(results):
            title = res.get("title", "No Title")
            link = res.get("link", "")
            snippet = res.get("snippet", "")
            output.append(f"[{idx+1}] Title: {title}\nURL: {link}\nSnippet: {snippet}\n")
            if link:
                source_urls.append({"url": link, "title": title})

        return {
            "success": True,
            "content": "\n".join(output),
            "source_url": source_urls[0]["url"] if source_urls else "",
            "source_urls": source_urls,
            "tool": "web_search"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"Web search failed: {str(e)}",
            "source_url": "",
            "tool": "web_search"
        }


def arxiv_search_tool(query: str, max_results: int = 3) -> dict:
    """Queries academic papers on arXiv."""
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = list(client.results(search))

        if not results:
            return {
                "success": True,
                "content": "No arXiv papers found matching the query.",
                "source_url": "",
                "tool": "arxiv_search"
            }

        output = []
        source_urls = []
        for idx, paper in enumerate(results):
            title = paper.title
            url = paper.entry_id
            summary = paper.summary.replace('\n', ' ')[:400]
            authors = ", ".join([author.name for author in paper.authors])
            output.append(f"[{idx+1}] Title: {title}\nAuthors: {authors}\nURL: {url}\nAbstract: {summary}...\n")
            source_urls.append({"url": url, "title": title})

        return {
            "success": True,
            "content": "\n".join(output),
            "source_url": source_urls[0]["url"] if source_urls else "",
            "source_urls": source_urls,
            "tool": "arxiv_search"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"arXiv search failed: {str(e)}",
            "source_url": "",
            "tool": "arxiv_search"
        }


def wikipedia_tool(topic: str) -> dict:
    """Retrieves summaries and background information from Wikipedia.

    `topic` is often a full natural-language sub-question rather than an exact
    page title, so we first resolve it to a real page via MediaWiki's search API
    instead of doing a direct (near-always-failing) exact-title lookup.
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent='ResearchMind/1.0 (contact@researchmind.com)',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

        page_title = topic
        try:
            search_resp = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": topic,
                    "format": "json",
                    "srlimit": 1
                },
                headers={"User-Agent": "ResearchMind/1.0 (contact@researchmind.com)"},
                timeout=10
            )
            search_resp.raise_for_status()
            hits = search_resp.json().get("query", {}).get("search", [])
            if hits:
                page_title = hits[0]["title"]
        except Exception:
            pass  # fall back to using the raw topic as the title

        page = wiki.page(page_title)
        if not page.exists():
            return {
                "success": False,
                "content": f"No Wikipedia page found matching '{topic}'.",
                "source_url": "",
                "tool": "wikipedia"
            }

        return {
            "success": True,
            "content": f"Title: {page.title}\nSummary: {page.summary[:1500]}...",
            "source_url": page.fullurl,
            "tool": "wikipedia"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"Wikipedia retrieval failed: {str(e)}",
            "source_url": "",
            "tool": "wikipedia"
        }


def rag_memory_tool(query: str, user_id: str) -> dict:
    """Searches user's own local Qdrant memory namespace for past research."""
    from agent.memory import MemoryManager
    try:
        # User ID is passed to separate namespaces
        memory_mgr = MemoryManager(user_id=str(user_id))
        hits = memory_mgr.retrieve(query, top_k=5)
        
        if not hits:
            return {
                "success": True,
                "content": "No relevant past research memories found in vector store.",
                "source_url": "",
                "tool": "rag_memory"
            }
            
        output = []
        for idx, hit in enumerate(hits):
            content = hit.get("content", "")
            src_url = hit.get("source_url", "Internal Memory")
            score = hit.get("reliability_score", 0.5)
            output.append(f"[{idx+1}] Memory content: {content}\nSource: {src_url}\nReliability Score: {score}\n")
            
        return {
            "success": True,
            "content": "\n".join(output),
            "source_url": hits[0].get("source_url", ""),
            "tool": "rag_memory"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"RAG memory search failed: {str(e)}",
            "source_url": "",
            "tool": "rag_memory"
        }


def python_repl_tool(code: str) -> dict:
    """Safely executes sandboxed Python code for data analysis."""
    # Setup safe builtin env, wired up for RestrictedPython's print() support
    globs = dict(safe_globals)
    globs["_print_"] = PrintCollector
    globs["_getattr_"] = safer_getattr
    globs["__builtins__"]["_getattr_"] = safer_getattr

    try:
        # Compile under RestrictedPython rules
        byte_code = compile_restricted(code, filename="<inline>", mode="exec")
        exec(byte_code, globs)
        output = globs["_print"]() if "_print" in globs else ""

        return {
            "success": True,
            "content": output or "Code executed successfully with no output.",
            "source_url": "",
            "tool": "python_repl"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"Execution failed: {str(e)}",
            "source_url": "",
            "tool": "python_repl"
        }


def calculator_tool(expression: str) -> dict:
    """Safely evaluates math expressions."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names["abs"] = abs
    allowed_names["round"] = round
    
    try:
        # Format caret to exponentiation
        safe_expr = expression.replace("^", "**")
        result = eval(safe_expr, {"__builtins__": None}, allowed_names)
        return {
            "success": True,
            "content": str(result),
            "source_url": "",
            "tool": "calculator"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"Evaluation error: {str(e)}",
            "source_url": "",
            "tool": "calculator"
        }
