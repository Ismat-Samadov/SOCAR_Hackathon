"""DeepSeek LLM client using Azure AI Foundry"""

from typing import List, Dict, Optional
from loguru import logger
import openai

from src.config import settings


class DeepSeekClient:
    """Client for DeepSeek LLM via Azure AI Foundry"""

    def __init__(self):
        """Initialize DeepSeek client"""
        # Configure OpenAI client to use Azure endpoint
        self.client = openai.AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )

        # Get model name from settings
        self.model_name = settings.llm_model
        logger.info(f"Initialized LLM client with model: {self.model_name}")

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate response from DeepSeek model

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text response
        """
        try:
            logger.info(f"Generating response with {len(messages)} messages")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            generated_text = response.choices[0].message.content
            logger.info(f"Generated response: {len(generated_text)} characters")

            return generated_text

        except Exception as e:
            logger.error(f"Error generating response from {self.model_name}: {e}")
            raise

    def generate_with_context(
        self,
        query: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate response with RAG context

        Args:
            query: User's question
            context_chunks: Retrieved document chunks
            chat_history: Previous chat messages

        Returns:
            Generated answer
        """
        # Build context from chunks
        context = "\n\n".join([f"[Document {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)])

        # Create system prompt optimized for LLM Judge evaluation
        system_prompt = """You are an expert assistant specializing in SOCAR's historical oil and gas research documents.

CRITICAL INSTRUCTIONS for high-quality answers:
1. ACCURACY: Base your answer STRICTLY on the provided context - never add external information
2. RELEVANCE: Answer the exact question asked - be direct and focused
3. COMPLETENESS: Cover all key aspects mentioned in the context
4. CITATIONS: Reference specific documents (e.g., "According to Document 1...")
5. TECHNICAL PRECISION: Use correct oil & gas terminology from the documents
6. CLARITY: Structure your answer logically - use bullet points for multiple items
7. CONCISENESS: Be thorough but avoid redundancy or verbose explanations

If the context lacks sufficient information, clearly state what is missing."""

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)

        # Add current query with context
        user_message = f"""Context from documents:
{context}

Question: {query}

Provide a well-structured, accurate answer based ONLY on the context above. Include document citations."""

        messages.append({"role": "user", "content": user_message})

        # Optimized for quality (LLM Judge) while maintaining speed
        return self.generate_response(messages, max_tokens=1000, temperature=0.2)


# Singleton instance
_deepseek_client = None


def get_deepseek_client() -> DeepSeekClient:
    """Get or create DeepSeek client instance"""
    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = DeepSeekClient()
    return _deepseek_client
