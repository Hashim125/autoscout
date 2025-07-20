import os
import time
import logging
from typing import Generator, Optional, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
import streamlit as st
from config.settings import config

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for handling OpenAI API interactions"""
    
    def __init__(self):
        self.base_url = config.OPENAI_BASE_URL
        self.model = config.DEFAULT_MODEL
        self.temperature = config.TEMPERATURE
        self.client = None
    
    def _get_api_key(self):
        """Get API key from Streamlit secrets or environment variable"""
        return st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    
    def _ensure_client(self):
        """Ensure client is initialized with current API key"""
        api_key = self._get_api_key()
        
        if not api_key:
            return False
        
        # Reinitialize client if API key changed or client doesn't exist
        if not self.client or self.client.api_key != api_key:
            try:
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=api_key
                )
                return True
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                return False
        
        return True
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is set and working"""
        if not self._ensure_client():
            return False
        
        try:
            # Test API connection with a minimal request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"API validation failed: {e}")
            return False
    
    def generate_report_stream(
        self, 
        system_prompt: str, 
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Generator[str, None, None]:
        """
        Generate report with streaming response
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt with data
            model: Model to use (defaults to config)
            temperature: Temperature setting (defaults to config)
            
        Yields:
            Chunks of the response as they arrive
        """
        try:
            # Ensure client is initialized
            if not self._ensure_client():
                yield "❌ Error: OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable."
                return
            
            # Validate inputs
            if not system_prompt or not user_prompt:
                raise ValueError("System and user prompts are required")
            
            # Use provided parameters or defaults
            model = model or self.model
            temperature = temperature or self.temperature
            
            # Create the stream
            stream = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                stream=True
            )
            
            # Yield chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in report generation: {e}")
            yield f"❌ Error generating report: {str(e)}"
    
    def generate_report_sync(
        self, 
        system_prompt: str, 
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate report with synchronous response
        
        Returns:
            Complete response as string
        """
        try:
            # Ensure client is initialized
            if not self._ensure_client():
                return "❌ Error: OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable."
            
            model = model or self.model
            temperature = temperature or self.temperature
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in sync report generation: {e}")
            return f"❌ Error generating report: {str(e)}"
    
    def get_available_models(self) -> Dict[str, str]:
        """Return only Llama 3 70B as the available model."""
        return {
            "meta-llama/llama-3-70b-instruct": "Llama 3 70B (Free)"
        } 