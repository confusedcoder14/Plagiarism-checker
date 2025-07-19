# Plagiarism Detection for Content

## Overview

This project is a web-based plagiarism detection tool designed to analyze and compare content from various file formats. It leverages advanced AI models, OCR, and digital pattern analysis to detect different levels of plagiarism, including paraphrased content using OpenAI's GPT models.

## Features

- Upload and scan files in .zip, .pdf, .docx, and .txt formats
- Detects complete, partial, and paraphrased plagiarism
- Uses AI-powered text similarity and digital pattern analysis
- OCR support for extracting text from images
- Real-time results and detailed reporting
- Web interface built with Flask and Streamlit

## Levels of Plagiarism Detection

1. **Level 1:** Complete Plagiarism (identical content)
2. **Level 2:** High Similarity (content with minor changes)
3. **Level 3:** Potential Plagiarism (moderate similarity)
4. **Level 4:** Paraphrased Plagiarism (detected using OpenAI)

## Setup Instructions

### 1. Clone the Repository

```bash
 git clone <repository-url>
 cd "Plagiarism detection for content"
```

### 2. Install Dependencies

Make sure you have Python 3.8 or higher installed.

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root and add your API keys:

```
OPENAI_API_KEY=your-openai-api-key
sD4bqVaCdgvTiEJ6haYkZfFcQIVVSJZH=your-apilayer-ocr-key
```

### 4. Run the Application

```bash
python app.py
```

The web app will be available at `http://127.0.0.1:5000/`.

## Usage

1. Open the web interface in your browser.
2. Upload a file or a zip archive containing files to check for plagiarism.
3. (Optional) Enable Level 4 detection for paraphrased content.
4. View the results and download the report.

## File Structure

- `app.py` - Main Flask web application
- `model.py` - Core plagiarism detection logic
- `ocr.py` - OCR text extraction from images
- `openai_model.py` - Paraphrasing detection using OpenAI
- `udp.py` - Digital pattern analysis for handwritten content
- `templates/` - HTML templates for the web interface
- `requirements.txt` - Python dependencies

## Dependencies

See `requirements.txt` for the full list of required Python packages.

## License

This project is for educational and research purposes. Please check individual package licenses for details.
