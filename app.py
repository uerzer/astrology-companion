"""
Hybrid Astrology Companion Web Application
Combines natal chart generation with AI-powered astrological guidance
"""

import gradio as gr
from natal_backend import NatalChartGenerator, get_timezone_suggestions
from chat_companion import AstrologyCompanion, format_chart_for_display
from pathlib import Path
import os
from typing import Optional, Dict, List, Tuple

# Initialize backends
chart_generator = NatalChartGenerator()
ai_companion = AstrologyCompanion()

# Global state for current chart (persists across tabs)
current_chart_data = None


def generate_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
    latitude: float,
    longitude: float,
    timezone: str
) -> Tuple[str, str, str]:
    """
    Generate natal chart and update global state
    
    Returns:
        (chart_svg_path, chart_text, status_message)
    """
    global current_chart_data
    
    if not name or not city:
        return None, "Please provide both name and city.", "⚠ Missing required fields"
    
    # Generate chart
    result = chart_generator.generate_chart(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        city=city
    )
    
    if not result.get("success"):
        error_msg = result.get("message", "Unknown error occurred")
        return None, f"Error: {error_msg}", "❌ Chart generation failed"
    
    # Store chart data globally
    current_chart_data = result
    
    # Update AI companion with chart context
    ai_companion.set_chart_context(result)
    
    # Format for display
    chart_text = format_chart_for_display(result)
    chart_svg = result.get("chart_svg")
    
    # Check if SVG file exists
    if chart_svg and Path(chart_svg).exists():
        status = f"✓ Chart generated for {name}"
        return chart_svg, chart_text, status
    else:
        return None, chart_text, "⚠ Chart generated but SVG not found"


def chat_with_companion(message: str, history: List) -> str:
    """
    Process chat message with streaming response
    
    Args:
        message: User's message
        history: Gradio chat history format [[user_msg, bot_msg], ...]
    
    Returns:
        Streaming generator
    """
    if not message.strip():
        return
    
    # Convert Gradio history to API format
    conversation_history = []
    for user_msg, bot_msg in history:
        if user_msg:
            conversation_history.append({"role": "user", "content": user_msg})
        if bot_msg:
            conversation_history.append({"role": "assistant", "content": bot_msg})
    
    # Stream response
    full_response = ""
    for chunk in ai_companion.chat_stream(message, conversation_history):
        full_response += chunk
        yield full_response


def get_chart_status() -> str:
    """Get current chart status for display"""
    global current_chart_data
    
    if current_chart_data and current_chart_data.get("success"):
        name = current_chart_data.get("name", "Unknown")
        return f"✓ Chart loaded: {name}"
    else:
        return "⚠ No chart loaded - generate a chart first for personalized insights"


def load_suggested_prompts() -> List[List[str]]:
    """Load suggested prompts based on current chart"""
    global current_chart_data
    
    prompts = ai_companion.get_suggested_prompts(current_chart_data)
    # Return as list of single-item lists for Gradio examples format
    return [[p] for p in prompts]


# Custom CSS for celestial theme
custom_css = """
/* Celestial Dark Theme - No AI Slop */
:root {
    --cosmic-bg: #0a0e27;
    --nebula-purple: #6366f1;
    --star-gold: #fbbf24;
    --moon-silver: #e0e7ff;
    --space-blue: #1e293b;
    --accent-cyan: #06b6d4;
}

/* Global background */
.gradio-container {
    background: linear-gradient(135deg, #0a0e27 0%, #1e1b4b 100%) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Tab styling */
.tab-nav button {
    background: var(--space-blue) !important;
    color: var(--moon-silver) !important;
    border: 1px solid var(--nebula-purple) !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.3s ease;
}

.tab-nav button.selected {
    background: var(--nebula-purple) !important;
    color: white !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
}

/* Input fields */
input, textarea, select {
    background: var(--space-blue) !important;
    color: var(--moon-silver) !important;
    border: 1px solid var(--nebula-purple) !important;
    border-radius: 8px !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.3) !important;
}

/* Buttons */
button {
    background: linear-gradient(135deg, var(--nebula-purple), var(--accent-cyan)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: transform 0.2s, box-shadow 0.2s;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
}

/* Chat messages */
.message.user {
    background: var(--space-blue) !important;
    border-left: 3px solid var(--star-gold) !important;
}

.message.bot {
    background: linear-gradient(135deg, #1e293b, #0f172a) !important;
    border-left: 3px solid var(--nebula-purple) !important;
}

/* Chart display */
.chart-output {
    background: var(--space-blue) !important;
    border: 2px solid var(--nebula-purple) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* Markdown rendering */
.prose {
    color: var(--moon-silver) !important;
}

.prose h1, .prose h2, .prose h3 {
    color: var(--star-gold) !important;
}

.prose strong {
    color: var(--accent-cyan) !important;
}

/* Status indicators */
.status-success {
    color: #10b981 !important;
}

.status-warning {
    color: var(--star-gold) !important;
}

.status-error {
    color: #ef4444 !important;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 10px;
    background: var(--cosmic-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--nebula-purple);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-cyan);
}

/* Add subtle star background animation */
@keyframes twinkle {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20% 30%, white, transparent),
        radial-gradient(2px 2px at 60% 70%, white, transparent),
        radial-gradient(1px 1px at 50% 50%, white, transparent),
        radial-gradient(1px 1px at 80% 10%, white, transparent),
        radial-gradient(2px 2px at 90% 60%, white, transparent);
    background-size: 200% 200%;
    animation: twinkle 4s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.gradio-container > * {
    position: relative;
    z-index: 1;
}
"""

# Build the interface
with gr.Blocks(css=custom_css, theme=gr.themes.Base(), title="Astrology Companion") as app:
    
    gr.Markdown(
        """
        # ✨ Astrology Companion
        ### Your Personal Guide to the Cosmos
        
        Generate your natal chart and explore its meaning through AI-powered insights.
        """
    )
    
    with gr.Tabs() as tabs:
        
        # TAB 1: NATAL CHART GENERATION
        with gr.Tab("🌙 Generate Chart"):
            gr.Markdown("### Enter Your Birth Information")
            
            with gr.Row():
                with gr.Column(scale=1):
                    name_input = gr.Textbox(
                        label="Name",
                        placeholder="Your name",
                        value=""
                    )
                    
                    with gr.Row():
                        year_input = gr.Number(label="Year", value=1990, precision=0)
                        month_input = gr.Number(label="Month", value=1, precision=0)
                        day_input = gr.Number(label="Day", value=1, precision=0)
                    
                    with gr.Row():
                        hour_input = gr.Number(label="Hour (24h)", value=12, precision=0)
                        minute_input = gr.Number(label="Minute", value=0, precision=0)
                
                with gr.Column(scale=1):
                    city_input = gr.Textbox(
                        label="City",
                        placeholder="Birth city"
                    )
                    
                    latitude_input = gr.Number(
                        label="Latitude",
                        value=40.7128,
                        info="Example: 40.7128 for NYC"
                    )
                    
                    longitude_input = gr.Number(
                        label="Longitude",
                        value=-74.0060,
                        info="Example: -74.0060 for NYC"
                    )
                    
                    timezone_input = gr.Dropdown(
                        label="Timezone",
                        choices=get_timezone_suggestions(),
                        value="America/New_York",
                        allow_custom_value=True
                    )
            
            generate_btn = gr.Button("🌟 Generate Natal Chart", variant="primary", size="lg")
            status_output = gr.Textbox(label="Status", interactive=False)
            
            with gr.Row():
                with gr.Column(scale=1):
                    chart_svg_output = gr.Image(
                        label="Natal Chart Visualization",
                        type="filepath"
                    )
                
                with gr.Column(scale=1):
                    chart_text_output = gr.Markdown(label="Chart Interpretation")
        
        # TAB 2: AI CHAT COMPANION
        with gr.Tab("💬 Chat Companion"):
            gr.Markdown("### Explore Your Chart with AI Guidance")
            
            chart_status_display = gr.Textbox(
                label="Chart Status",
                value=get_chart_status(),
                interactive=False
            )
            
            chatbot = gr.Chatbot(
                label="Astrology Companion",
                height=500,
                show_label=True
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask about your chart, astrology concepts, or life areas...",
                    scale=4,
                    show_label=False
                )
                send_btn = gr.Button("Send", scale=1, variant="primary")
            
            gr.Examples(
                examples=load_suggested_prompts(),
                inputs=msg_input,
                label="✨ Suggested Questions (based on your chart)"
            )
            
            clear_btn = gr.Button("🗑 Clear Conversation")
    
    # Event handlers
    generate_btn.click(
        fn=generate_natal_chart,
        inputs=[
            name_input, year_input, month_input, day_input,
            hour_input, minute_input, city_input,
            latitude_input, longitude_input, timezone_input
        ],
        outputs=[chart_svg_output, chart_text_output, status_output]
    ).then(
        fn=get_chart_status,
        inputs=None,
        outputs=chart_status_display
    )
    
    # Chat handlers
    msg_input.submit(
        fn=chat_with_companion,
        inputs=[msg_input, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        None,
        msg_input
    )
    
    send_btn.click(
        fn=chat_with_companion,
        inputs=[msg_input, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        None,
        msg_input
    )
    
    clear_btn.click(
        lambda: None,
        None,
        chatbot
    )

# Launch configuration
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
