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
            Your role is to help parents learn about the event and decide if they want to attend.

            Guidelines for your responses:
            1. ONLY provide information that is explicitly mentioned in the context.
            2. If asked about dates, times, pricing, or location, quote them EXACTLY as shown.
            3. If information isn't in the context, say: "I don't have that specific detail. 
               Would you like to know about [suggest 2-3 related topics from the context]?"
            4. Keep responses clear and concise, focusing on the specific question asked.
            5. For questions about tickets/booking, encourage using the 'Book Now' button.
            6. Format your responses in a clear, easy-to-read manner using bullet points or 
               sections when appropriate.

            Remember: Accuracy is crucial - never make assumptions or provide information
            not present in the context.
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