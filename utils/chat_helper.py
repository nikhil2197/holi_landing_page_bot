import os
from openai import OpenAI
from typing import Dict, Optional

class ChatHelper:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
        self.model = "gpt-4o"
        
    def generate_response(
        self, 
        query: str, 
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generates a response using GPT-4 with the given context.
        """
        try:
            if not context:
                return {
                    "answer": "I apologize, but I don't have access to the event information "
                    "at the moment. Would you like to know about the general concept of "
                    "Holi celebration or would you prefer to contact the event organizers directly?",
                    "status": "error"
                }

            system_prompt = """
            You are a helpful assistant providing information about the Holi Playdate event.
            Only provide information that is explicitly mentioned in the context provided.
            If information is not available in the context, suggest alternative topics.
            Format your responses in a clear, concise manner.
            Do not make assumptions or provide information not present in the context.
            """

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            return {
                "answer": response.choices[0].message.content,
                "status": "success"
            }

        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error while processing your "
                f"request. Please try again later.",
                "status": "error"
            }
