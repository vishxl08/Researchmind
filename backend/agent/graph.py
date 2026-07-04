import json
import time
from typing import List, Dict, TypedDict, Any
from django.conf import settings
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from langgraph.graph import StateGraph, END, START
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from research.models import ResearchJob, ResearchReport, AgentStep
from .memory import MemoryManager
from .tools import (
    web_search_tool,
    arxiv_search_tool,
    wikipedia_tool,
    rag_memory_tool,
    calculator_tool,
    python_repl_tool
)
from .prompts import (
    PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT,
    WRITER_SYSTEM_PROMPT, WRITER_USER_PROMPT,
    CRITIC_SYSTEM_PROMPT, CRITIC_USER_PROMPT,
    REVISOR_SYSTEM_PROMPT, REVISOR_USER_PROMPT,
    DEPTH_GUIDANCE, DEPTH_NUM_QUESTIONS, DEPTH_WORD_TARGET
)

# Define State Schema
class AgentState(TypedDict):
    job_id: int
    query: str
    sub_questions: List[str]
    current_question_idx: int
    findings: List[Dict[str, Any]]
    memory_hits: List[Dict[str, Any]]
    scratchpad: str
    draft_report: str
    critique: str
    final_report: str
    iteration: int
    max_iterations: int
    tool_calls_made: List[str]
    confidence_score: float
    done: bool
    user_id: int
    depth: str


def stream_step_to_channels(job_id: int, step_type: str, step_number: int, thought: str = "", tool_name: str = "", tool_input: Any = None, tool_output: str = "", tokens: int = 0, duration: int = 0):
    """Broadcasts step progress to Channels group."""
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f"research_job_{job_id}",
                {
                    "type": "job_step",
                    "step": {
                        "step_type": step_type,
                        "step_number": step_number,
                        "thought": thought,
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "tool_output": tool_output,
                        "tokens_used": tokens,
                        "duration_ms": duration
                    }
                }
            )
        except Exception as e:
            print(f"Error broadcasting WebSocket message: {e}")


def save_and_stream_step(state: AgentState, step_type: str, thought: str = "", tool_name: str = "", tool_input: Any = None, tool_output: str = "", duration_ms: int = 0) -> int:
    """Saves agent step to SQLite and broadcasts it via WebSocket."""
    job_id = state["job_id"]
    state["iteration"] += 1
    step_num = state["iteration"]
    
    tokens = 120 + len(thought) // 4 + len(tool_output) // 4
    
    try:
        job = ResearchJob.objects.get(id=job_id)
        AgentStep.objects.create(
            job=job,
            step_type=step_type,
            step_number=step_num,
            thought=thought,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            tokens_used=tokens,
            duration_ms=duration_ms
        )
    except Exception as e:
        print(f"Error saving AgentStep: {e}")
        
    stream_step_to_channels(
        job_id=job_id,
        step_type=step_type,
        step_number=step_num,
        thought=thought,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_output=tool_output,
        tokens=tokens,
        duration=duration_ms
    )
    return step_num


def call_llm(system_prompt: str, user_prompt: str, response_format_json: bool = False) -> str:
    """Helper to call Groq API with fallback mock responses."""
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key:
        print("Groq API key not found. Using Mock response.")
        time.sleep(1) # simulate latency
        if "planner" in system_prompt.lower():
            return json.dumps([
                "What is the definition and history of agentic AI?",
                "What are the main architectures of LLM agents?",
                "What memory persistence methods are used in agent systems?"
            ])
        elif "writer" in system_prompt.lower():
            return """# Executive Summary
Agentic AI represents a paradigm shift from simple chatbots to autonomous systems.

# Key Findings
- Agentic systems use reflection loops to critique drafts.
- Multi-tier memory stores state locally.

# Detailed Research Analysis
## History of Agentic AI
Initially chatbots were simple. Now they are complex workflows.

# Contradictions and Divergent Viewpoints
Some researchers claim agent reasoning is emergent, while others claim it is rule-based.

# Cited Sources
- [1] https://wikipedia.org/wiki/Software_agent (Wikipedia Page)
- [2] https://arxiv.org/abs/2401.12345 (arXiv Paper)
"""
        elif "critic" in system_prompt.lower():
            return "- Add a section detailing local SQLite storage vs Redis.\n- Cite more sources in the reflection discussion."
        elif "revisor" in system_prompt.lower():
            return """# Executive Summary
Agentic AI represents a major shift from one-shot prompts to persistent, self-directed workflows.

# Key Findings
- Self-critique loops significantly improve draft quality.
- Memory architecture uses SQLite + Vector stores.

# Detailed Research Analysis
## Architectures and Memory
Agents run on state machines like LangGraph. They query Qdrant to retrieve historical research.

# Contradictions and Divergent Viewpoints
A major conflict exists: is complex planning better done by prompting or code?

# Cited Sources
- [1] https://wikipedia.org/wiki/Software_agent (Wikipedia Page)
- [2] https://arxiv.org/abs/2401.12345 (arXiv Paper)
- [3] https://qdrant.tech (Qdrant Database)
"""
        return "Mock response"
        
    try:
        kwargs = {}
        if response_format_json:
            kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
            
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name=settings.GROQ_MODEL,
            temperature=0.2,
            **kwargs
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        res = llm.invoke(messages)
        return res.content
    except Exception as e:
        print(f"LLM call failed: {e}")
        if response_format_json:
            return "[]"
        return f"Writing report failed due to API error: {str(e)}"


# Nodes Implementation

def planner_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    query = state["query"]
    depth = state.get("depth") or "deep"

    # Call planner LLM
    output = call_llm(
        PLANNER_SYSTEM_PROMPT,
        PLANNER_USER_PROMPT.format(
            query=query,
            depth=depth,
            depth_guidance=DEPTH_GUIDANCE.get(depth, DEPTH_GUIDANCE["deep"]),
            num_questions=DEPTH_NUM_QUESTIONS.get(depth, DEPTH_NUM_QUESTIONS["deep"])
        ),
        response_format_json=True
    )

    try:
        parsed = json.loads(output)
        if isinstance(parsed, list):
            sub_questions = parsed
        elif isinstance(parsed, dict):
            # Groq's JSON object mode wraps the array in an object (e.g. {"sub_questions": [...]});
            # pull out the first list value rather than treating the whole blob as one question.
            list_values = [v for v in parsed.values() if isinstance(v, list)]
            sub_questions = list_values[0] if list_values else [output]
        else:
            sub_questions = [output]
    except Exception:
        # Fallback split
        sub_questions = [q.strip() for q in output.split("\n") if q.strip()]

    duration = int((time.time() - start_time) * 1000)
    save_and_stream_step(
        state,
        step_type="reason",
        thought=f"Decomposed query '{query}' ({depth} depth) into {len(sub_questions)} sub-questions:\n" + "\n".join([f"- {q}" for q in sub_questions]),
        duration_ms=duration
    )

    return {
        "sub_questions": sub_questions,
        "current_question_idx": 0,
        "iteration": state["iteration"]
    }


def memory_retriever_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    sub_questions = state["sub_questions"]
    user_id = state["user_id"]
    
    memory_mgr = MemoryManager(user_id=str(user_id))
    all_hits = []
    
    for idx, q in enumerate(sub_questions):
        hits = memory_mgr.retrieve(q, top_k=2)
        for h in hits:
            all_hits.append({
                "sub_question": q,
                "content": h.get("content"),
                "source_url": h.get("source_url")
            })
            
    duration = int((time.time() - start_time) * 1000)
    thought = f"Queried local Qdrant vector store. Found {len(all_hits)} matching historical research memories."
    save_and_stream_step(
        state,
        step_type="reason",
        thought=thought,
        duration_ms=duration
    )
    
    return {
        "memory_hits": all_hits,
        "iteration": state["iteration"]
    }


def select_tools_for_question(current_q: str, depth: str) -> List[str]:
    """Rule-based tool selection. Deep/expert depth cross-checks each sub-question
    against multiple complementary sources instead of a single lookup."""
    q_lower = current_q.lower()
    primary = "web_search"

    if "arxiv" in q_lower or "paper" in q_lower or "academic" in q_lower or "research breakthroughs" in q_lower:
        primary = "arxiv_search"
    elif "wikipedia" in q_lower or "define" in q_lower or "history of" in q_lower or "who is" in q_lower:
        primary = "wikipedia"
    elif "memory" in q_lower or "past research" in q_lower:
        primary = "rag_memory"
    elif "calculate" in q_lower or "math" in q_lower or "+" in q_lower or "*" in q_lower:
        primary = "calculator"

    tools = [primary]
    # Single-purpose tools (memory lookup, arithmetic) shouldn't be padded with unrelated lookups
    if primary in ("calculator", "rag_memory"):
        return tools

    if depth in ("deep", "expert") and "wikipedia" not in tools:
        tools.append("wikipedia")
    if depth == "expert":
        if "arxiv_search" not in tools:
            tools.append("arxiv_search")
        if "web_search" not in tools:
            tools.append("web_search")

    return tools[:3]


def tool_selector_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    idx = state["current_question_idx"]
    sub_questions = state["sub_questions"]
    depth = state.get("depth") or "deep"

    if idx >= len(sub_questions):
        return {"scratchpad": "DONE", "iteration": state["iteration"]}

    current_q = sub_questions[idx]
    tools = select_tools_for_question(current_q, depth)

    duration = int((time.time() - start_time) * 1000)
    thought = f"Selecting tool(s) {tools} to answer sub-question: '{current_q}'"
    save_and_stream_step(
        state,
        step_type="reason",
        thought=thought,
        duration_ms=duration
    )

    return {
        "scratchpad": f"tool:{','.join(tools)}",
        "iteration": state["iteration"]
    }


def execute_single_tool(tool_name: str, sub_question: str, user_id: int) -> Dict[str, Any]:
    result = {"success": False, "content": "Tool execution failed", "source_url": "", "tool": tool_name}
    try:
        if tool_name == "web_search":
            result = web_search_tool(sub_question)
        elif tool_name == "arxiv_search":
            result = arxiv_search_tool(sub_question)
        elif tool_name == "wikipedia":
            result = wikipedia_tool(sub_question)
        elif tool_name == "rag_memory":
            result = rag_memory_tool(sub_question, user_id)
        elif tool_name == "calculator":
            result = calculator_tool(sub_question)
        elif tool_name == "python_repl":
            result = python_repl_tool(sub_question)
    except Exception as e:
        result = {"success": False, "content": f"Error: {e}", "source_url": "", "tool": tool_name}
    return result


def tool_executor_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    scratchpad = state["scratchpad"]
    idx = state["current_question_idx"]

    if scratchpad == "DONE" or idx >= len(state["sub_questions"]):
        return {"iteration": state["iteration"]}

    sub_question = state["sub_questions"][idx]
    user_id = state["user_id"]
    tool_names = scratchpad.replace("tool:", "").split(",")

    sections = []
    sources = []
    any_success = False
    for tool_name in tool_names:
        result = execute_single_tool(tool_name, sub_question, user_id)
        content = result.get("content", "")
        if content:
            sections.append(f"[{tool_name}] {content}")
        if result.get("success") and content:
            any_success = True
            # Track source URLs that actually appear in the content the writer will see
            # (not just the top hit), so cited sources are never untracked. Capped per
            # sub-question (not per-tool) so multi-tool cross-checking doesn't turn the
            # reference list into an indiscriminate wall of citations.
            candidate_urls = result.get("source_urls") or (
                [{"url": result["source_url"], "title": ""}] if result.get("source_url") else []
            )
            for src in candidate_urls:
                if len(sources) >= 4:
                    break
                sources.append({"url": src["url"], "tool": tool_name})

    combined_content = "\n\n".join(sections)
    duration = int((time.time() - start_time) * 1000)

    save_and_stream_step(
        state,
        step_type="tool_call",
        thought=f"Invoked tool(s) '{', '.join(tool_names)}' for query '{sub_question}'",
        tool_name=",".join(tool_names),
        tool_input={"query": sub_question},
        tool_output=combined_content,
        duration_ms=duration
    )

    result_payload = {
        "success": any_success,
        "content": combined_content,
        "sources": sources,
        "source_url": sources[0]["url"] if sources else "",
        "tool": ",".join(tool_names)
    }

    return {
        "scratchpad": json.dumps(result_payload),
        "iteration": state["iteration"]
    }


def observer_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    scratchpad = state["scratchpad"]
    idx = state["current_question_idx"]

    if scratchpad == "DONE" or idx >= len(state["sub_questions"]):
        return {"iteration": state["iteration"]}

    current_q = state["sub_questions"][idx]
    user_id = state["user_id"]

    try:
        tool_result = json.loads(scratchpad)
    except Exception:
        tool_result = {"success": False, "content": scratchpad, "source_url": "", "tool": "unknown"}

    content = tool_result.get("content", "")
    tool_name = tool_result.get("tool", "")
    success = tool_result.get("success", False)
    sources = tool_result.get("sources") or (
        [{"url": tool_result["source_url"], "tool": tool_name}] if tool_result.get("source_url") else []
    )

    # Update memory manager reliability score per source domain
    from urllib.parse import urlparse
    memory_mgr = MemoryManager(user_id=str(user_id))
    for src in sources:
        url = src.get("url", "")
        if url and url.startswith("http"):
            domain = urlparse(url).netloc
            if domain:
                memory_mgr.update_reliability(domain, positive=success)

    # Store findings in memory manager if successful and content is informative
    if success and content and len(content.strip()) > 50:
        memory_mgr.store(
            content=f"Fact gathered for '{current_q}':\n{content[:2000]}",
            metadata={
                "source_url": sources[0]["url"] if sources else "",
                "source_tool": tool_name,
                "reliability_score": 0.8 if success else 0.4,
                "topic_tags": [state["query"][:20]]
            }
        )

    # Add to findings list
    findings = list(state["findings"])
    findings.append({
        "question": current_q,
        "answer": content,
        "sources": sources,
        "tool": tool_name,
        "success": success
    })

    duration = int((time.time() - start_time) * 1000)
    thought = f"Observer analyzed output from tool(s) '{tool_name}'. Found {len(sources)} source(s)."
    save_and_stream_step(
        state,
        step_type="observe",
        thought=thought,
        tool_output=content[:1000] + ("..." if len(content) > 1000 else ""),
        duration_ms=duration
    )
    
    return {
        "findings": findings,
        "current_question_idx": idx + 1,
        "iteration": state["iteration"]
    }


def reflector_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    idx = state["current_question_idx"]
    sub_questions = state["sub_questions"]
    iteration = state["iteration"]
    max_iter = state["max_iterations"]
    
    # Check if all sub questions answered or hit iteration limit
    done = (idx >= len(sub_questions)) or (iteration >= max_iter)
    
    # Calculate confidence based on successes
    findings = state["findings"]
    successes = [f for f in findings if f.get("success")]
    confidence = len(successes) / len(sub_questions) if sub_questions else 1.0
    
    duration = int((time.time() - start_time) * 1000)
    thought = f"Reflecting on search progress: Answered {idx}/{len(sub_questions)} sub-questions. Current confidence rating: {confidence * 100:.1f}%. Loop terminates? {done}"
    save_and_stream_step(
        state,
        step_type="reflect",
        thought=thought,
        duration_ms=duration
    )
    
    return {
        "done": done,
        "confidence_score": confidence,
        "iteration": state["iteration"]
    }


def writer_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    query = state["query"]
    findings = state["findings"]
    depth = state.get("depth") or "deep"

    # Format findings text for LLM, listing every source retrieved per sub-question.
    # Cap each finding's text so the combined prompt stays within the LLM's token/rate
    # limits even at "expert" depth with many sub-questions and multi-tool findings.
    per_finding_cap = max(400, 9000 // max(1, len(findings)))
    findings_list = []
    for idx, f in enumerate(findings):
        sources = f.get("sources") or []
        if sources:
            src_lines = "\n".join(f"  - {s['url']}" for s in sources if s.get("url"))
        else:
            src_lines = "  - (no external source retrieved; based on internal reasoning only)"
        answer = f["answer"]
        if len(answer) > per_finding_cap:
            answer = answer[:per_finding_cap] + "..."
        findings_list.append(f"Sub-Question {idx+1}: {f['question']}\nFinding: {answer}\nSources:\n{src_lines}\n")
    findings_text = "\n".join(findings_list)

    length_target = DEPTH_WORD_TARGET.get(depth, DEPTH_WORD_TARGET["deep"])
    draft_report = call_llm(
        WRITER_SYSTEM_PROMPT.format(length_target=length_target),
        WRITER_USER_PROMPT.format(query=query, findings_text=findings_text, depth=depth)
    )

    duration = int((time.time() - start_time) * 1000)
    save_and_stream_step(
        state,
        step_type="write",
        thought="Assembled all facts. Writing initial draft report in markdown with inline citations.",
        tool_output=draft_report[:1000] + ("..." if len(draft_report) > 1000 else ""),
        duration_ms=duration
    )
    
    return {
        "draft_report": draft_report,
        "iteration": state["iteration"]
    }


def critic_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    query = state["query"]
    draft_report = state["draft_report"]
    depth = state.get("depth") or "deep"
    length_target = DEPTH_WORD_TARGET.get(depth, DEPTH_WORD_TARGET["deep"])

    critique = call_llm(
        CRITIC_SYSTEM_PROMPT.format(length_target=length_target),
        CRITIC_USER_PROMPT.format(query=query, draft_report=draft_report)
    )
    
    duration = int((time.time() - start_time) * 1000)
    save_and_stream_step(
        state,
        step_type="critique",
        thought="Critiquing draft report to ensure formatting, citation consistency, and fact coverage.",
        tool_output=critique,
        duration_ms=duration
    )
    
    return {
        "critique": critique,
        "iteration": state["iteration"]
    }


def revisor_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    draft = state["draft_report"]
    critique = state["critique"]
    depth = state.get("depth") or "deep"
    length_target = DEPTH_WORD_TARGET.get(depth, DEPTH_WORD_TARGET["deep"])

    final_report = call_llm(
        REVISOR_SYSTEM_PROMPT.format(length_target=length_target),
        REVISOR_USER_PROMPT.format(draft_report=draft, critique=critique)
    )
    
    duration = int((time.time() - start_time) * 1000)
    save_and_stream_step(
        state,
        step_type="write",
        thought="Revised draft report incorporating reviewer feedback. Producing final polished version.",
        tool_output=final_report[:1000] + ("..." if len(final_report) > 1000 else ""),
        duration_ms=duration
    )
    
    return {
        "final_report": final_report,
        "iteration": state["iteration"]
    }


def finalizer_node(state: AgentState) -> Dict[str, Any]:
    job_id = state["job_id"]
    final_report = state["final_report"]
    findings = state["findings"]
    confidence = state["confidence_score"]
    
    try:
        # Extract title and summary using basic helpers
        title = "Research Report: " + state["query"][:100]
        exec_summary = "An autonomous research report generated for the query: " + state["query"]
        
        # Simple markdown extraction
        lines = final_report.split("\n")
        for line in lines:
            if line.startswith("# ") or line.startswith("## "):
                title = line.replace("#", "").strip()
                break
                
        # Find Executive Summary block
        for idx, line in enumerate(lines):
            if "executive summary" in line.lower():
                # take next non empty line
                summary_lines = []
                for sub_line in lines[idx+1:idx+6]:
                    if sub_line.strip() and not sub_line.startswith("#"):
                        summary_lines.append(sub_line.strip())
                if summary_lines:
                    exec_summary = " ".join(summary_lines)
                break
        
        # Sources parsing (dedup by URL; a finding may carry multiple cross-checked sources)
        sources = []
        seen_urls = set()
        for f in findings:
            for src in (f.get("sources") or ([{"url": f["source_url"]}] if f.get("source_url") else [])):
                url = src.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "url": url,
                        "title": f.get("question", "Search Result"),
                        "reliability_score": 0.8 if f.get("success") else 0.4
                    })


        sub_questions = state["sub_questions"]
        
        # Word count
        word_count = len(final_report.split())
        
        # Save to SQLite
        job = ResearchJob.objects.get(id=job_id)
        
        # Create or update report
        ResearchReport.objects.update_or_create(
            job=job,
            defaults={
                "title": title,
                "executive_summary": exec_summary,
                "full_report_markdown": final_report,
                "sources": sources,
                "sub_questions": sub_questions,
                "key_findings": ["Report generated autonomously", f"Word count: {word_count}"],
                "confidence_score": float(confidence),
                "word_count": word_count
            }
        )
        
        # Update job status
        job.status = 'done'
        job.completed_at = timezone.now()
        job.save()

        # Trigger email notification if scheduled and requested
        try:
            from scheduler.models import ScheduledResearch
            from notifications.email import send_report_email
            if ScheduledResearch.objects.filter(user=job.user, query_template=job.query, deliver_via_email=True).exists():
                send_report_email(job.user, job.report)
        except Exception as email_err:
            print(f"Failed to send scheduled research email: {email_err}")
        
        # Stream complete event
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"research_job_{job_id}",
                {
                    "type": "job_complete",
                    "report_id": job.report.id
                }
            )
            
    except Exception as e:
        print(f"Error in finalizer node: {e}")
        try:
            job = ResearchJob.objects.get(id=job_id)
            job.status = 'failed'
            job.completed_at = timezone.now()
            job.save()
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"research_job_{job_id}",
                    {
                        "type": "job_error",
                        "message": str(e)
                    }
                )
        except Exception:
            pass
            
    return state


# Routing Decisions

def route_reflect(state: AgentState) -> str:
    if state["done"]:
        return "writer"
    return "tool_selector"


# Build the Graph

def get_agent_graph():
    builder = StateGraph(AgentState)
    
    # Add Nodes
    builder.add_node("planner", planner_node)
    builder.add_node("memory_retriever", memory_retriever_node)
    builder.add_node("tool_selector", tool_selector_node)
    builder.add_node("tool_executor", tool_executor_node)
    builder.add_node("observer", observer_node)
    builder.add_node("reflector", reflector_node)
    builder.add_node("writer", writer_node)
    builder.add_node("critic", critic_node)
    builder.add_node("revisor", revisor_node)
    builder.add_node("finalizer", finalizer_node)
    
    # Add Edges
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "memory_retriever")
    builder.add_edge("memory_retriever", "tool_selector")
    builder.add_edge("tool_selector", "tool_executor")
    builder.add_edge("tool_executor", "observer")
    builder.add_edge("observer", "reflector")
    
    # Conditional edge
    builder.add_conditional_edges(
        "reflector",
        route_reflect,
        {
            "tool_selector": "tool_selector",
            "writer": "writer"
        }
    )
    
    builder.add_edge("writer", "critic")
    builder.add_edge("critic", "revisor")
    builder.add_edge("revisor", "finalizer")
    builder.add_edge("finalizer", END)
    
    return builder.compile()
