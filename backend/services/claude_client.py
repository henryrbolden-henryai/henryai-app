"""Claude API client wrapper with retry logic and streaming support"""

import os
import time
import logging
import anthropic
from dataclasses import dataclass
from typing import Optional
from fastapi import HTTPException

logger = logging.getLogger("henryhq")


@dataclass
class ClaudeResponse:
    """Response from Claude API including token usage."""
    text: str
    input_tokens: int
    output_tokens: int
    model: str

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

# Module-level client instance
_client = None


def initialize_client(api_key: str = None, timeout: float = 120.0):
    """Initialize the Anthropic client. Call this once at app startup.

    Returns None if API key is not available (graceful degradation).
    """
    global _client
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        logger.warning("ANTHROPIC_API_KEY not set - Claude API calls will fail")
        return None
    _client = anthropic.Anthropic(api_key=key, timeout=timeout)
    logger.info("Anthropic client initialized successfully")
    return _client


def get_client() -> anthropic.Anthropic:
    """Get the initialized Anthropic client.

    Raises HTTPException if client is not initialized.
    """
    global _client
    if _client is None:
        # Try to initialize (might work if env var was set after import)
        _client = initialize_client()
    if _client is None:
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable. Please try again."
        )
    return _client


def call_claude_with_usage(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    max_retries: int = 3,
    temperature: float = 0,
    model: str = "claude-sonnet-4-20250514"
) -> ClaudeResponse:
    """Call Claude API with given prompts and return response with token usage.

    Args:
        system_prompt: The system prompt to use
        user_message: The user message to send
        max_tokens: Maximum tokens in response
        max_retries: Number of retry attempts for overload errors
        temperature: Controls randomness. Use 0 for deterministic scoring, higher for creative tasks.
        model: The Claude model to use

    Returns:
        ClaudeResponse with text and token usage information
    """
    client = get_client()

    for attempt in range(max_retries):
        try:
            print(f"🤖 Calling Claude API... (message length: {len(user_message)} chars, attempt {attempt + 1}/{max_retries}, temp={temperature})")
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            response_text = message.content[0].text
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            print(f"🤖 Claude responded with {len(response_text)} chars, {input_tokens} input tokens, {output_tokens} output tokens")

            return ClaudeResponse(
                text=response_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model
            )
        except anthropic.APIStatusError as e:
            # Check for overload error (529)
            if e.status_code == 529:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s exponential backoff
                    print(f"⏳ API overloaded, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"🔥 API still overloaded after {max_retries} attempts")
                    raise HTTPException(
                        status_code=503,
                        detail="Our AI is temporarily busy. Please try again in a moment."
                    )
            else:
                print(f"🔥 CLAUDE API ERROR: {e}")
                raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
        except Exception as e:
            print(f"🔥 CLAUDE API ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")


def call_claude(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    max_retries: int = 3,
    temperature: float = 0,
    model: str = "claude-sonnet-4-20250514"
) -> str:
    """Call Claude API with given prompts and automatic retry for overload errors.

    This is a convenience wrapper around call_claude_with_usage that returns just the text.

    Args:
        system_prompt: The system prompt to use
        user_message: The user message to send
        max_tokens: Maximum tokens in response
        max_retries: Number of retry attempts for overload errors
        temperature: Controls randomness. Use 0 for deterministic scoring, higher for creative tasks.
        model: The Claude model to use

    Returns:
        The text response from Claude
    """
    response = call_claude_with_usage(
        system_prompt=system_prompt,
        user_message=user_message,
        max_tokens=max_tokens,
        max_retries=max_retries,
        temperature=temperature,
        model=model
    )
    return response.text


@dataclass
class StreamingUsage:
    """Container for streaming usage data that gets populated after stream completes."""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""


def call_claude_streaming(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    max_retries: int = 3,
    temperature: float = 0,
    model: str = "claude-sonnet-4-20250514"
):
    """Call Claude API with streaming support - yields chunks of text, with retry for overload.

    Args:
        system_prompt: The system prompt to use
        user_message: The user message to send
        max_tokens: Maximum tokens in response
        max_retries: Number of retry attempts for overload errors
        temperature: Controls randomness. Use 0 for deterministic scoring.
        model: The Claude model to use

    Yields:
        Text chunks from Claude's response
    """
    client = get_client()

    for attempt in range(max_retries):
        try:
            print(f"🤖 Calling Claude API (streaming)... (message length: {len(user_message)} chars, attempt {attempt + 1}/{max_retries}, temp={temperature})")
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
            return  # Success, exit the retry loop
        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2
                    print(f"⏳ API overloaded, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"🔥 API still overloaded after {max_retries} attempts")
                    raise HTTPException(
                        status_code=503,
                        detail="Our AI is temporarily busy. Please try again in a moment."
                    )
            else:
                print(f"🔥 CLAUDE API ERROR: {e}")
                raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
        except Exception as e:
            print(f"🔥 CLAUDE API ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")


def call_claude_streaming_with_usage(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    max_retries: int = 3,
    temperature: float = 0,
    model: str = "claude-sonnet-4-20250514",
    usage_container: Optional[StreamingUsage] = None
):
    """Call Claude API with streaming support and capture token usage.

    Args:
        system_prompt: The system prompt to use
        user_message: The user message to send
        max_tokens: Maximum tokens in response
        max_retries: Number of retry attempts for overload errors
        temperature: Controls randomness. Use 0 for deterministic scoring.
        model: The Claude model to use
        usage_container: Optional StreamingUsage object that will be populated with usage data
                        after the stream completes

    Yields:
        Text chunks from Claude's response
    """
    client = get_client()

    for attempt in range(max_retries):
        try:
            print(f"🤖 Calling Claude API (streaming with usage)... (message length: {len(user_message)} chars, attempt {attempt + 1}/{max_retries}, temp={temperature})")
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            ) as stream:
                for text in stream.text_stream:
                    yield text

                # Capture usage after stream completes
                if usage_container is not None:
                    final_message = stream.get_final_message()
                    usage_container.input_tokens = final_message.usage.input_tokens
                    usage_container.output_tokens = final_message.usage.output_tokens
                    usage_container.model = model
                    print(f"🤖 Stream complete: {usage_container.input_tokens} input tokens, {usage_container.output_tokens} output tokens")

            return  # Success, exit the retry loop
        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2
                    print(f"⏳ API overloaded, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"🔥 API still overloaded after {max_retries} attempts")
                    raise HTTPException(
                        status_code=503,
                        detail="Our AI is temporarily busy. Please try again in a moment."
                    )
            else:
                print(f"🔥 CLAUDE API ERROR: {e}")
                raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
        except Exception as e:
            print(f"🔥 CLAUDE API ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
