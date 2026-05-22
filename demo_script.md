# 🎬 DiffWhisperer: 60-Second Demo Script

Follow this script to record a professional, high-impact demo for your submission.

## 🕒 [0:00 - 0:10] - The Hook
**Action**: Open your terminal in the `diff-whisperer` repo. Ensure you have some staged changes.
**Command**: 
```bash
python main.py narrate --persona senior
```
**Voiceover/Caption**: "Turn cryptic git diffs into architectural stories with DiffWhisperer."

## 🕒 [0:10 - 0:25] - Deep Reasoning & Resilience
**Action**: Run the deep mode. Let the progress spinners show.
**Command**:
```bash
python main.py narrate --deep --save
```
**Voiceover/Caption**: "Our multi-stage Reasoning Pipeline performs a technical extraction, security audit, and synthesis in one flow."

## 🕒 [0:25 - 0:40] - Privacy Shield (The "Trust" Moment)
**Action**: Stage a change that includes a dummy secret (e.g., `API_KEY="12345"`) and run dry-run.
**Command**:
```bash
python main.py narrate --dry-run
```
**Voiceover/Caption**: "Privacy first. Our local Shield redacts secrets before they ever leave your machine."

## 🕒 [0:40 - 0:55] - Interactive Git-Chat
**Action**: Enter the REPL and ask one question.
**Command**:
```bash
python main.py chat --persona senior
# Question: "What are the risks in this change?"
```
**Voiceover/Caption**: "Don't just read—converse. Talk to your code history with our interactive Git-Chat REPL."

## 🕒 [0:55 - 1:00] - The Finish
**Action**: Show the `list-personas` table.
**Command**:
```bash
python main.py list-personas
```
**Voiceover/Caption**: "DiffWhisperer. Powered by Gemma 4. Storytelling for Developers."

---

### 💡 Pro Tips for Recording:
- **Clean Terminal**: Use a dark theme with a clean font (like Cascadia Code or Fira Code).
- **Speed**: If the AI is slow, you can speed up the "Thinking" parts in your video editor.
- **GIF Tool**: Use **Terminalizer** for a pixel-perfect GIF, or **OBS/Screen-to-Gif** for a video.
