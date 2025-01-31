from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

class PostGenerator:
    def __init__(self, api_key):
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            api_key=api_key,
        )
        
    def generate_post(self, event_title, content_length="Very Short"):
        post_length = self._get_post_length_prompt(content_length)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a skilled LinkedIn content creator, crafting professional posts for Indian festivals that align with corporate values like diversity, teamwork, and innovation. Your goal is to highlight the cultural significance of the festival while connecting it to themes such as growth, collaboration, and progress.

            Guidelines:
            {post_length}

            Key Points:
            - Start with a warm introduction to the festival and its significance.
            - Link the festival to themes such as growth, teamwork, or innovation.
            - Conclude with festive wishes and include the following hashtags and add 1 related to the event:
            #DigitalTransformation #Architect #Cloud #Devops #AIInnovation
            """),
            ("human", "{input}"),
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"input": event_title})
        return response.content
        
    def _get_post_length_prompt(self, content_length):
        prompts = {
            "Very Short": "Write a very short, concise post (1 line), briefly mentioning the significance of the event and connecting it to corporate values.",
            "Short": "Write a short post (1 paragraph), highlighting the significance of the event and how it connects to values like growth and collaboration.",
            "Medium": "Write a medium-length post (2-3 paragraphs), with a more detailed explanation of the event's significance and its relation to themes like innovation and teamwork."
        }
        return prompts.get(content_length, prompts["Very Short"])