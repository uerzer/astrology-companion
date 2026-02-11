"""
AI Chat Companion using Claude API
Provides chart-aware astrological guidance through conversational AI
"""

import os
from typing import Dict, List, Optional, Generator
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AstrologyCompanion:
    """Claude-powered astrology chat companion"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chat companion
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Please set it in your .env file or pass it directly."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Chart context (set via set_chart_context)
        self.chart_context = None
    
    def _load_system_prompt(self) -> str:
        """Load the astrologer system prompt from file"""
        prompt_path = Path(__file__).parent / "prompts" / "astrologer_system.md"
        
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback if file not found
            return """You are a warm, insightful astrology companion. 
            Help users understand their natal chart through personalized, 
            empowering conversations. Reference their specific placements 
            when available."""
    
    def set_chart_context(self, chart_data: Optional[Dict]) -> None:
        """
        Set the natal chart context for chart-aware responses
        
        Args:
            chart_data: Dictionary containing chart information from NatalChartGenerator
        """
        if not chart_data or not chart_data.get("success"):
            self.chart_context = None
            return
        
        # Format chart data into readable context
        context_parts = [
            f"User's Natal Chart - {chart_data['name']}",
            f"Birth: {chart_data['birth_data']['date']} at {chart_data['birth_data']['time']}",
            f"Location: {chart_data['birth_data']['location']}",
            "",
            "PLACEMENTS:"
        ]
        
        # Add planetary placements
        for planet, data in chart_data.get('placements', {}).items():
            retro = " (Retrograde)" if data.get('retrograde') else ""
            context_parts.append(
                f"- {planet}: {data['sign']} in House {data['house']}{retro}"
            )
        
        # Add key interpretations
        if 'interpretation' in chart_data:
            context_parts.append("")
            context_parts.append("KEY THEMES:")
            for key, text in chart_data['interpretation'].items():
                context_parts.append(f"- {text}")
        
        # Add major aspects
        if chart_data.get('aspects'):
            context_parts.append("")
            context_parts.append("MAJOR ASPECTS:")
            for aspect in chart_data['aspects'][:5]:  # Top 5 aspects
                context_parts.append(
                    f"- {aspect['planets']}: {aspect['type']} (orb: {aspect['orb']}°)"
                )
        
        self.chart_context = "\n".join(context_parts)
    
    def chat(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Send a message and get a response (non-streaming)
        
        Args:
            message: User's message
            conversation_history: List of {"role": "user/assistant", "content": "..."}
        
        Returns:
            Assistant's response text
        """
        messages = conversation_history or []
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Build system prompt with chart context if available
        system_content = self.system_prompt
        if self.chart_context:
            system_content = f"{self.system_prompt}\n\n---\n\nCURRENT CHART CONTEXT:\n{self.chart_context}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_content,
                messages=messages
            )
            
            return response.content[0].text
            
        except anthropic.APIError as e:
            return f"API Error: {str(e)}. Please check your API key and try again."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_stream(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> Generator[str, None, None]:
        """
        Send a message and get a streaming response
        
        Args:
            message: User's message
            conversation_history: List of {"role": "user/assistant", "content": "..."}
        
        Yields:
            Text chunks as they arrive
        """
        messages = conversation_history or []
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Build system prompt with chart context if available
        system_content = self.system_prompt
        if self.chart_context:
            system_content = f"{self.system_prompt}\n\n---\n\nCURRENT CHART CONTEXT:\n{self.chart_context}"
        
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_content,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except anthropic.APIError as e:
            yield f"API Error: {str(e)}. Please check your API key and try again."
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_suggested_prompts(self, chart_data: Optional[Dict] = None) -> List[str]:
        """
        Generate suggested conversation starters based on chart
        
        Args:
            chart_data: Chart data to base suggestions on
        
        Returns:
            List of suggested prompts
        """
        if not chart_data or not chart_data.get("success"):
            # Generic prompts when no chart
            return [
                "Tell me about my sun sign",
                "What does my moon sign mean?",
                "How do I read my natal chart?",
                "What are the most important placements?",
                "Explain houses in astrology"
            ]
        
        # Chart-specific prompts
        placements = chart_data.get('placements', {})
        prompts = []
        
        if 'Sun' in placements:
            sun_sign = placements['Sun']['sign']
            prompts.append(f"What does my Sun in {sun_sign} mean for my identity?")
        
        if 'Moon' in placements:
            moon_sign = placements['Moon']['sign']
            prompts.append(f"Tell me about my Moon in {moon_sign}")
        
        if 'Venus' in placements:
            venus_house = placements['Venus']['house']
            prompts.append(f"What does Venus in my {venus_house}th house say about relationships?")
        
        # Add general prompts
        prompts.extend([
            "What stands out most in my chart?",
            "How can I work with my chart's challenges?",
            "What are my natural strengths according to my chart?"
        ])
        
        return prompts[:6]  # Return top 6


def format_chart_for_display(chart_data: Dict) -> str:
    """
    Format chart data into a readable text summary
    
    Args:
        chart_data: Chart data from NatalChartGenerator
    
    Returns:
        Formatted text summary
    """
    if not chart_data.get("success"):
        return "No chart data available."
    
    lines = [
        f"# Natal Chart: {chart_data['name']}",
        "",
        f"**Birth:** {chart_data['birth_data']['date']} at {chart_data['birth_data']['time']}",
        f"**Location:** {chart_data['birth_data']['location']}",
        "",
        "## Core Identity",
        ""
    ]
    
    # Add interpretations
    if 'interpretation' in chart_data:
        for text in chart_data['interpretation'].values():
            lines.append(text)
            lines.append("")
    
    # Add placements table
    lines.append("## Planetary Placements")
    lines.append("")
    if 'placements' in chart_data:
        for planet, data in chart_data['placements'].items():
            retro = " ℞" if data.get('retrograde') else ""
            lines.append(f"- **{planet}**: {data['sign']} (House {data['house']}){retro}")
        lines.append("")
    
    # Add aspects
    if chart_data.get('aspects'):
        lines.append("## Major Aspects")
        lines.append("")
        for aspect in chart_data['aspects'][:5]:
            lines.append(f"- {aspect['planets']}: {aspect['type']}")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    companion = AstrologyCompanion()
    
    # Test without chart context
    print("Testing basic chat...")
    response = companion.chat("What is a natal chart?")
    print(f"Response: {response[:200]}...")
    
    # Test suggested prompts
    print("\nSuggested prompts:")
    for prompt in companion.get_suggested_prompts():
        print(f"- {prompt}")
