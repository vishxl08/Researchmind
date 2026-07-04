import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ResearchJobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.room_group_name = f"research_job_{self.job_id}"
        
        # Add connection to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove connection from group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def job_step(self, event):
        """Sends a single agent step to the client."""
        step = event['step']
        await self.send(text_data=json.dumps({
            "type": "step",
            "step_type": step["step_type"],
            "step_number": step["step_number"],
            "thought": step["thought"],
            "tool_name": step["tool_name"],
            "tool_input": step["tool_input"],
            "tool_output": step["tool_output"],
            "tokens_used": step["tokens_used"],
            "duration_ms": step["duration_ms"]
        }))

    async def job_complete(self, event):
        """Sends completion event with the report ID to client."""
        await self.send(text_data=json.dumps({
            "type": "complete",
            "report_id": event["report_id"]
        }))

    async def job_error(self, event):
        """Sends error message to client."""
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": event["message"]
        }))
