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

        # Set up safety settings - be permissive for code generation
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        # Create model
        self.model = genai.GenerativeModel(
            model_name=model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List] = None,
        **kwargs
    ) -> ChatMessage:
        """
        Generate completion from messages with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stop_sequences: Optional stop sequences
            grammar: Optional grammar/formatting structure
            tools_to_call_from: Optional list of tools (not used for Gemini)
            **kwargs: Additional generation parameters

        Returns:
            ChatMessage object with the response
        """
        logger.info(f"GeminiModel.__call__ invoked with {len(messages)} messages")

        # Convert messages to Gemini format
        prompt = self._messages_to_prompt(messages)

        # Retry loop for rate limiting
        for attempt in range(self.max_retries):
            try:
                # Generate response with safety settings
                response = self.model.generate_content(
                    prompt,
                    safety_settings=self.safety_settings
                )

                # Check if response was blocked
                if not response.candidates:
                    # Check prompt feedback for blocking reasons
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        block_reason = getattr(feedback, 'block_reason', 'UNKNOWN')
                        safety_ratings = getattr(feedback, 'safety_ratings', [])
                        error_details = f"Response blocked. Reason: {block_reason}"
                        if safety_ratings:
                            error_details += f", Safety ratings: {safety_ratings}"
                        logger.error(error_details)
                        raise Exception(f"Gemini blocked the response: {block_reason}")
                    else:
                        raise Exception("Gemini returned empty candidates (content may be blocked)")

                # Extract text from response
                try:
                    # Try the .text property first (most reliable)
                    text = response.text
                except (ValueError, AttributeError):
                    # Fallback to manual extraction
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            if len(candidate.content.parts) > 0:
                                text = candidate.content.parts[0].text
                            else:
                                raise Exception("Response candidate has no parts")
                        else:
                            raise Exception("Response candidate has no content")
                    else:
                        raise Exception("No valid response candidates")

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
