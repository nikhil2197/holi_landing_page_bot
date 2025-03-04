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
        Generates a response using GPT-4 with enhanced context handling.
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
            Your role is to help parents learn about the event activities and details.

            Response Guidelines:
            1. For general "what is happening" queries:
               - Provide a concise, engaging summary of main activities
               - Use emojis to make points visually appealing
               - Structure as "A [duration] Holi playdate where kids:" followed by key activities

            2. For specific activity queries:
               - Provide detailed explanation of the activity steps
               - Break down the process clearly
               - Keep the focus on what children will do/learn

            3. For logistics queries (time, location, price):
               - Quote EXACTLY from the context
               - Format clearly with relevant details grouped together

            4. For missing information:
               - Say: "I don't have that specific detail. Would you like to know about [2-3 related topics]?"

            5. For booking questions:
               - Encourage using the 'Book Now' button in the sidebar

            Remember:
            - Only use information explicitly in the context
            - Make responses engaging but factual
            - Present information in a parent-friendly way
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