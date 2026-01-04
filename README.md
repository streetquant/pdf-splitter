# PDF/EPUB Chapter Splitter

A powerful CLI tool that automatically splits PDF and EPUB files into chapter-wise sections with smart OCR detection. Perfect for learners using AI-powered study assistants.

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Why This Tool?

Learning from books becomes significantly more effective when combined with AI study assistants. This tool enables you to:

- **Feed individual chapters to AI tutors** for focused discussions
- **Use ChatGPT's Study Mode** on specific sections
- **Leverage Gemini's Guided Learning** with curated content
- **Create notebooks in NotebookLM** chapter by chapter
- **Generate summaries and quizzes** per chapter

## AI Learning Workflow

```
📚 Full Book (PDF/EPUB)
        │
        ▼
┌───────────────────────┐
│  PDF Splitter Tool    │
│  ├── Pre-text         │  → Intro materials
│  ├── Chapter 01.pdf   │  → AI Study Session 1
│  ├── Chapter 02.pdf   │  → AI Study Session 2
│  ├── Chapter 03.pdf   │  → AI Study Session 3
│  └── Post-text        │  → Appendices/References
└───────────────────────┘
        │
        ▼
🤖 AI Learning Tools
    ├── ChatGPT Study Mode
    ├── Gemini Guided Learning  
    ├── NotebookLM
    └── Custom AI Tutors
```

## Use with AI Study Tools

### ChatGPT Study Mode

ChatGPT Study Mode was launched by OpenAI on **July 29, 2025**. It offers step-by-step guidance instead of quick answers, helping you learn and retain knowledge better.

Upload individual chapter PDFs to ChatGPT and ask:

```
"Analyze this chapter about [topic] and create:
1. Key concepts summary
2. 5 quiz questions
3. Real-world examples
4. Connections to previous chapters"
```

**Key Features:**
- Guided learning with questions, hints, and step-by-step explanations
- Personalized support that adapts to your skill level
- Knowledge checks with quizzes and open-ended questions
- Progress tracking to show mastery and areas to focus

Learn more: [chatgpt.com/features/study-mode](https://chatgpt.com/features/study-mode/)

### Gemini Guided Learning

Google launched **Guided Learning in Gemini** on **August 6, 2025**. It acts as a personal learning companion that helps you build deep understanding of subjects.

Feed chapters sequentially:

```
"Guide me through this chapter using the Feynman technique.
Start with the main thesis, then break down complex concepts,
and end with practical applications."
```

**Key Features:**
- Interactive study partner for deeper understanding
- Uploads course material, debug code, or understand concepts
- Visual responses and interactive study aids
- Personalized explanations adapting to your needs

Learn more: [blog.google/products/gemini/guided-learning](https://blog.google/products/gemini/guided-learning-google-gemini/)

### NotebookLM

Google's NotebookLM continues to evolve with powerful AI learning features updated in 2025.

**2025 Features:**
- **Audio Overviews** - Turn sources into engaging "Deep Dive" discussions
- **Video Overviews** - Generate video summaries of your documents
- **Flashcards & Quizzes** - Create from your documents instantly
- **Learning Guide** - Generate tailored study guides
- **Mind Maps** - Visualize connections between concepts
- **Presentations** - Create polished outlines with talking points

**How to Use with Split Chapters:**

NotebookLM is used through the web interface at [notebooklm.google](https://notebooklm.google/). Here's how to use it with this tool's output:

1. **Split your book:**
   ```bash
   python -m pdfsplitter.cli "book.pdf"
   ```

2. **Open NotebookLM** at [notebooklm.google](https://notebooklm.google/)

3. **Click "Upload"** and select the chapter PDFs from the output folder

4. **Use NotebookLM features:**
   - Click "Audio Overview" to create AI audio discussions
   - Use "Guide" to generate study guides
   - Ask questions about specific chapters

**Example Workflow:**
```
Output folder: book_output/
├── chapter_01.pdf  → Upload to NotebookLM
├── chapter_02.pdf  → Upload to NotebookLM  
├── chapter_03.pdf  → Upload to NotebookLM
└── ...

NotebookLM will create Audio Overviews, summaries, and answer questions
about your content using Gemini's AI capabilities.
```

**Note:** NotebookLM doesn't have a public Python API for creating notebooks programmatically. The free version is used through the web interface. For enterprise/automated use, Google Cloud offers [NotebookLM Enterprise APIs](https://cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs).

## Features

- **Automatic Chapter Detection** - Uses TOC and text analysis
- **Smart OCR Decision** - LLM determines if scanned PDFs need OCR
- **Pre/Post Text Separation** - Isolates front matter and appendices
- **Multiple Format Support** - Handles both PDF and EPUB
- **CLI Interface** - Simple, command-line based
- **Caching** - Remembers OCR decisions for speed

## Installation

```bash
# Clone the repository
git clone https://github.com/streetquant/pdf-splitter.git
cd pdf-splitter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

## Configuration

Create a `.env` file with your API key:

```env
OPENROUTER_API_KEY=your-api-key-here
MODEL_NAME=nvidia/nemotron-3-nano-30b-a3b:free
```

Get a free API key from [OpenRouter](https://openrouter.ai/).

## Usage

### Basic Usage

```bash
# Process a PDF
python -m pdfsplitter.cli book.pdf

# Process an EPUB
python -m pdfsplitter.cli textbook.epub

# Specify output directory
python -m pdfsplitter.cli book.pdf -o ./my-chapters

# Verbose mode
python -m pdfsplitter.cli book.pdf -v
```

### Output Structure

```
book_output/
├── metadata.json        # Chapter information
├── pretext.pdf          # Front matter (TOC, preface)
├── chapter_01.pdf       # Chapter 1
├── chapter_02.pdf       # Chapter 2
├── chapter_03.pdf       # Chapter 3
├── ...
└── posttext.pdf         # Appendices, references
```

## Example: Learning Workflow

### 1. Split Your Book

```bash
$ python -m pdfsplitter.cli "Deep Learning.pdf"
✓ Processing complete!
  Input: Deep Learning.pdf
  Output: Deep Learning_output
  Chapters: 12
    01. Pre-text
    02. Chapter 1: Math Foundations
    03. Chapter 2: Neural Networks
    ...
    12. Post-text
```

### 2. Study Chapter by Chapter with AI

**Prompt for ChatGPT Study Mode:**

```
I'm studying Chapter 3 on Neural Networks from a deep learning book.
Please:
1. Explain the key concepts in simple terms
2. Create a concept map connecting to Chapter 2
3. Generate 5 practice problems
4. Suggest real-world applications
5. Recommend which sections to reread
```

**Prompt for Gemini Guided Learning:**

```
Using the Feynman technique, help me understand this chapter:
- Start with the main thesis
- Break down 3 complex concepts
- End with practical applications in real-world scenarios
```

**NotebookLM Integration:**

```python
# Upload chapters to NotebookLM for comprehensive learning
# Features: Audio Overviews, Flashcards, Mind Maps, Quizzes
```

### 3. Build a Knowledge Base

Combine chapters across multiple AI tools for comprehensive coverage:

| Tool | Best For | Chapter Usage |
|------|----------|---------------|
| ChatGPT Study Mode | Interactive Q&A, step-by-step explanations | Upload 1-2 chapters per session |
| Gemini Guided Learning | Personalized learning paths | Sequential chapter progression |
| NotebookLM | Audio summaries, flashcards, research | Upload entire book |

## Supported Patterns

The tool detects chapters using:

- `CHAPTER 1`, `Chapter 1`, `CHAPTER ONE`
- `Part I`, `Part 1`
- Table of Contents entries

Posttext detection includes:

- `APPENDIX`, `REFERENCES`, `BIBLIOGRAPHY`
- `INDEX`, `GLOSSARY`, `ACKNOWLEDGMENTS`

## API Integration

```python
from pdfsplitter.core import split_pdf, split_epub

# Programmatic usage
result = split_pdf("book.pdf", "./output")
for chapter in result.chapters:
    print(f"{chapter.title}: pages {chapter.start_page}-{chapter.end_page}")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_pdf_processor.py -v
```

## Project Structure

```
pdf-splitter/
├── src/pdfsplitter/
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration
│   ├── constants.py        # Patterns and constants
│   ├── core/
│   │   ├── pdf_processor.py    # PDF splitting logic
│   │   ├── epub_processor.py   # EPUB splitting logic
│   │   ├── ocr_detector.py     # Smart OCR detection
│   │   └── models.py           # Data models
│   └── utils/
│       ├── llm.py          # OpenRouter integration
│       ├── cache.py        # Caching
│       └── logging.py      # Logging
├── tests/                  # Test suite
├── pyproject.toml          # Project config
└── requirements.txt        # Dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use in your projects.

## Acknowledgments

- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [ebooklib](https://github.com/aozorahack/ebooklib) - EPUB handling
- [OpenRouter](https://openrouter.ai/) - LLM API access
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF manipulation

---

**Happy Learning!** 📚🤖
