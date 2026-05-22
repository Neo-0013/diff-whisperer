# 📖 DiffWhisperer: AI-Powered Code Review Storyteller
**Built for the Google Gemma 4 Challenge on DEV.**

> "Stop reading dry diffs. Start reading stories."

**DiffWhisperer** is a professional-grade CLI tool that leverages the reasoning capabilities of **Gemma 4** to transform cryptic git diff outputs into high-level architectural narratives. It bridges the gap between "what changed" and "why it matters," acting as a virtual Senior Architect on your team.

---

## 🌟 Key Features

### 🕵️ Pre-Flight Privacy Shield
Security first. Before any data leaves your machine, a local regex-based scanner redacts PII, API keys, and secrets. Use `--dry-run` to see exactly what gets redacted before any AI call is made.

### 🧠 Multi-Stage Reasoning Pipeline (`--deep`)
Beyond simple summarization. In deep mode, DiffWhisperer performs a 3-stage analysis:
1. **Technical Extraction**: Summarizes the "essence" of the logic shifts.
2. **Security Audit**: Analyzes the diff for architectural risks and blind spots.
3. **Persona Synthesis**: Combines the findings into a tailored narrative.

### 💬 Interactive Git-Chat REPL
Don't just read the review—converse with it. Enter a stateful chat session to ask follow-up questions about specific lines of code or refactoring suggestions.

### 🎭 Persona-Based Perspectives
- **`--persona senior`**: Focuses on architecture, security, and breaking changes.
- **`--persona mentor`**: Explains changes simply for learning and onboarding.
- **`--persona pirate`**: Adds a touch of high-seas adventure to your code reviews.

### 🛡️ Industrial-Grade Resilience
Built with a "Zero-Crash" philosophy. The tool features:
- **Universal Exponential Backoff**: Survives API spikes (500, 503, 429) with 5 layers of retries.
- **Dual-Model Fallback**: Automatically drops from 31B to 26B if high-demand limits are reached.
- **Pydantic Validation**: Guarantees structured, safe data handling.

---

## 🛠️ Installation

### 1. Clone & Setup
```bash
git clone https://github.com/Neo-0013/diff-narrator.git
cd diff-narrator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
1. Get your API Key from [Google AI Studio](https://aistudio.google.com/).
2. Copy `.env.example` to `.env`.
3. Add your key: `GEMMA_API_KEY=your_key_here`.

---

## 💻 Usage

### Generate a Narrative
```bash
# Standard analysis
python main.py narrate

# Deep architectural analysis with save
python main.py narrate --deep --save

# Using a specific persona
python main.py narrate --persona mentor
```

### Interactive Chat
```bash
python main.py chat --persona senior
```

### Privacy Check (Dry Run)
```bash
python main.py narrate --dry-run
```

---

## 🔮 Roadmap: The Future of DiffWhisperer
We’re just getting started. Here’s what we’re planning to add to the DiffWhisperer ecosystem:
- 🤖 **PR Comment Bot**: Direct GitHub Action integration to post narratives as PR comments automatically.
- 💬 **Team Hub**: Real-time Slack and Discord alerts with daily "Code Story" summaries for the whole team.
- 🧬 **Project DNA**: RAG-lite context awareness to help Gemma understand your entire codebase, not just the current diff.
- 📊 **Impact Graphs**: Automatic generation of Mermaid.js dependency impact diagrams for every change.
- 🌐 **DiffWhisperer Web**: A sleek, full-stack Web UI version for architectural visualization.

---

## 🧪 Testing
We believe in 100% logic reliability. Run the test suite with:
```bash
python -m pytest
```

---

## 📜 License
MIT License - Created for the Google Gemma 4 Challenge.

---

### 🚀 Demo
*(Insert your Demo GIF here! See the recording script below for inspiration.)*
