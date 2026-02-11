# 🌙 Astrology Companion

A hybrid web application that combines precise natal chart generation with AI-powered astrological guidance. Generate your birth chart and explore its meaning through conversational AI that references your specific placements.

![Astrology Companion](https://img.shields.io/badge/Powered%20by-Claude%20AI-6366f1)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Gradio](https://img.shields.io/badge/Gradio-4.0%2B-orange)

## ✨ Features

### 🎯 Natal Chart Generation
- **Accurate astronomical calculations** using Swiss Ephemeris (via Kerykeion)
- **Visual chart wheel** in SVG format
- **Complete planetary placements** with houses and retrograde indicators
- **Major aspect analysis** with orbs
- **Human-readable interpretations** for Sun, Moon, and Rising signs

### 💬 AI Chat Companion
- **Chart-aware conversations** powered by Claude 3.5 Sonnet
- **Personalized insights** that reference your specific placements
- **Streaming responses** for smooth, real-time interaction
- **Suggested questions** tailored to your chart
- **Empowering guidance** focused on self-discovery, not predictions

### 🎨 User Experience
- **Custom celestial theme** - dark mode with purple/gold accents and animated stars
- **Tabbed interface** - seamless switching between chart generation and chat
- **Session persistence** - your chart context remains available across tabs
- **Responsive design** - works on desktop and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/uerzer/astrology-companion.git
cd astrology-companion
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
   - Local: http://127.0.0.1:7860
   - Or use the public URL shown in terminal for remote access

## 📖 Usage Guide

### Generating Your Natal Chart

1. **Navigate to the "Generate Chart" tab**
2. **Enter your birth details**:
   - Full name
   - Date of birth (year, month, day)
   - Time of birth (hour, minute in 24h format)
   - Birth location (city, latitude, longitude, timezone)
   - **Tip**: Use online tools like [LatLong.net](https://www.latlong.net/) for coordinates
3. **Click "Generate Natal Chart"**
4. **View your results**:
   - Visual chart wheel (SVG)
   - Planetary placements with houses
   - Major aspects
   - Quick interpretations for Sun, Moon, Rising

### Chatting with the AI Companion

1. **Generate your chart first** (required for personalized insights)
2. **Switch to the "Chat Companion" tab**
3. **Start with suggested questions** or ask your own:
   - "What does my Sun in [sign] mean for my career?"
   - "How do I work with my Moon in [sign]?"
   - "Tell me about the aspect between my [planet 1] and [planet 2]"
4. **Get chart-aware responses** that reference your specific placements
5. **Continue the conversation** - the AI remembers context within the session

### Example Questions

- "What stands out most in my chart?"
- "How can I work with my challenging Saturn placement?"
- "What does my 7th house say about relationships?"
- "Explain the square between my Sun and Moon"
- "What's my life purpose based on my chart?"

## 🏗️ Architecture

```
astrology-companion/
├── app.py                      # Main Gradio application
├── natal_backend.py            # Chart generation engine (Kerykeion wrapper)
├── chat_companion.py           # Claude API integration
├── prompts/
│   └── astrologer_system.md   # AI system prompt
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

### Component Overview

- **`natal_backend.py`**: Wraps the Kerykeion library for natal chart calculations
  - Handles Swiss Ephemeris data
  - Generates SVG chart wheels
  - Extracts planetary positions, houses, aspects
  - Provides human-readable interpretations

- **`chat_companion.py`**: Manages AI conversations
  - Integrates Anthropic Claude API
  - Maintains chart context across conversations
  - Generates personalized question prompts
  - Streams responses for real-time interaction

- **`app.py`**: Gradio web interface
  - Two-tab layout (Chart Generation + Chat)
  - Custom celestial-themed UI
  - Session state management
  - Coordinate between chart generation and chat

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional (with defaults)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
```

### Customization Options

**Chart Output Directory**:
By default, charts are saved to `output/`. Change in `natal_backend.py`:
```python
self.output_dir = Path("your_custom_path")
```

**UI Theme**:
Modify the theme in `app.py`:
```python
with gr.Blocks(theme=gr.themes.Soft(...)) as demo:
```

**System Prompt**:
Edit `prompts/astrologer_system.md` to adjust the AI's personality and guidelines.

## 🛠️ Development

### Running Tests

```bash
# Test natal chart generation
python -c "from natal_backend import NatalChartGenerator; g = NatalChartGenerator(); print(g.generate_chart('Test', 1990, 1, 1, 12, 0, 0, 0, 'UTC', 'London'))"

# Test chat companion (requires .env setup)
python -c "from chat_companion import AstrologyCompanion; a = AstrologyCompanion(); print(a.get_suggested_questions())"
```

### Adding Features

**New chart features**: Extend `NatalChartGenerator` class
**Chat enhancements**: Modify `AstrologyCompanion` class
**UI changes**: Edit `app.py` Gradio components

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add transit calculations
- [ ] Implement compatibility (synastry) analysis
- [ ] Support for multiple chart storage
- [ ] Export charts as PDF/PNG
- [ ] Advanced aspect patterns (grand trine, yod, etc.)
- [ ] Progressive aspects over time
- [ ] Mobile-optimized responsive design

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **[Kerykeion](https://github.com/g-battaglia/kerykeion)** - Powerful Python astrology library
- **[Anthropic](https://www.anthropic.com/)** - Claude AI API
- **[Gradio](https://www.gradio.app/)** - Easy-to-use ML web interfaces
- **Swiss Ephemeris** - Astronomical calculations

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for common problems

## ⚠️ Disclaimer

This application is for entertainment and self-reflection purposes. Astrology is a symbolic language for exploring patterns and potentials, not a deterministic prediction tool. Always consult qualified professionals for medical, legal, financial, or mental health decisions.

---

Built with ❤️ for cosmic exploration and self-discovery