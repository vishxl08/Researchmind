from django.utils import timezone
from research.models import ResearchJob
from .graph import get_agent_graph

def run_agent(job_id: int):
    """Executes the agent LangGraph loop for the given ResearchJob ID."""
    try:
        job = ResearchJob.objects.get(id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
    except ResearchJob.DoesNotExist:
        print(f"ResearchJob with ID {job_id} does not exist. Runner aborted.")
        return
    except Exception as e:
        print(f"Failed to initialize ResearchJob run: {e}")
        return

    # Prepare initial LangGraph state
    initial_state = {
        "job_id": job.id,
        "query": job.query,
        "sub_questions": [],
        "current_question_idx": 0,
        "findings": [],
        "memory_hits": [],
        "scratchpad": "",
        "draft_report": "",
        "critique": "",
        "final_report": "",
        "iteration": 0,
        "max_iterations": job.max_iterations,
        "tool_calls_made": [],
        "confidence_score": 0.0,
        "done": False,
        "user_id": job.user.id,
        "depth": job.depth
    }

    try:
        # Compile and invoke state graph.
        # Each sub-question pass through the loop (tool_selector -> tool_executor ->
        # observer -> reflector) counts as several steps against LangGraph's recursion
        # limit, so the default of 25 is too low once depth/max_iterations allow more
        # than a handful of sub-questions (expert-depth runs were hitting it).
        graph = get_agent_graph()
        recursion_limit = max(100, job.max_iterations * 6)
        graph.invoke(initial_state, config={"recursion_limit": recursion_limit})
    except Exception as e:
        print(f"Critical execution error during agent run for job {job_id}: {e}")
        
        # Ensure job is marked failed
        try:
            job.status = 'failed'
            job.completed_at = timezone.now()
            job.save()
        except Exception as save_err:
            print(f"Could not save failed status for job: {save_err}")
