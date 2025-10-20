"""Gemini model wrapper for smolagents."""

from smolagents import Model
from smolagents.models import ChatMessage
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Union
import time
import logging

logger = logging.getLogger(__name__)


class GeminiModel(Model):
    """Gemini model wrapper for smolagents with rate limit handling."""

    def __init__(
        self,
        model_id: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        **kwargs
    ):
        """
        Initialize Gemini model.

        Args:
            model_id: Gemini model identifier
            api_key: Google API key
            temperature: Sampling temperature
            max_retries: Maximum retry attempts for rate limits
            retry_delay: Initial retry delay in seconds
            **kwargs: Additional generation config parameters
        """
        super().__init__()
        self.model_id = model_id
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Configure Gemini API
        if api_key:
            genai.configure(api_key=api_key)

        # Set up generation config
        self.generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            **kwargs
        }

        # Create model
        self.model = genai.GenerativeModel(
            model_name=model_id,
            generation_config=self.generation_config
        )

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> ChatMessage:
        """
        Generate completion from messages with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stop_sequences: Optional stop sequences
            **kwargs: Additional generation parameters

        Returns:
            ChatMessage object with the response
        """
        # Convert messages to Gemini format
        prompt = self._messages_to_prompt(messages)

        # Retry loop for rate limiting
        for attempt in range(self.max_retries):
            try:
                # Generate response
                response = self.model.generate_content(prompt)

                # Extract text from response
                if hasattr(response, 'text'):
                    text = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    text = response.candidates[0].content.parts[0].text
                else:
                    text = str(response)

                # Return as ChatMessage
                return ChatMessage(role="assistant", content=text)

            except Exception as e:
                error_msg = str(e)

                # Check for rate limiting (429 or quota exceeded)
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    if attempt < self.max_retries - 1:
                        # Extract retry delay from error if available
                        delay = self.retry_delay * (2 ** attempt)  # Exponential backoff

                        # Try to extract suggested delay from error
                        if "retry in" in error_msg.lower():
                            try:
                                import re
                                match = re.search(r"retry in (\d+(?:\.\d+)?)", error_msg.lower())
                                if match:
                                    delay = float(match.group(1))
                            except:
                                pass

                        logger.warning(f"Rate limit hit, retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {self.max_retries} attempts. Please wait before retrying.")
                else:
                    # Non-rate-limit error, raise immediately
                    raise

        raise Exception(f"Failed after {self.max_retries} attempts")

    def forward(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Forward method required by smolagents Model base class.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stop_sequences: Optional stop sequences
            **kwargs: Additional generation parameters

        Returns:
            Generated text string
        """
        result = self.__call__(messages, stop_sequences, **kwargs)
        return result.content if isinstance(result, ChatMessage) else str(result)

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert message list to single prompt."""
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts)
