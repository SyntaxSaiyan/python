I sideloaded some books to my Kindle and lost the option to export my notes and highlights directly to email from the device. After some online research, I came across clippings.io, which worked but the free version only gives you the first 100 characters of each highlight. This meant the rest of my highlights were lost, making most of my notes incomplete and practically meaningless.

So I teamed up with Windsurf to create a quick Python script that parses through the `My Clippings.txt` file and creates reader-friendly PDF documents. Now I can print them and have physical copies to easily access whenever I want to be reminded of the lessons I learned from the books I've read.

# Kindle Notes Organizer

A Python tool to export your Kindle clippings into printable PDFs.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Kindle Clippings

1. Connect your Kindle to your computer
2. Navigate to the `documents` folder on your Kindle
3. Copy the `My Clippings.txt` file to this project directory
4. Place it alongside the Python scripts

### 3. Export All Books to PDF

```bash
python3 pdf_exporter.py "My Clippings.txt" --all
```

This will create separate PDF files for each book in the `pdf_exports/` directory, ready for printing.

### 4. Export Specific Book

```bash
python3 pdf_exporter.py "My Clippings.txt" --book "Book Title (Author)"
```

## File Structure

```
kindle-notes-organizer/
|-- kindle_organizer.py    # Core parser
|-- pdf_exporter.py        # PDF generation
|-- requirements.txt       # Dependencies
|-- My Clippings.txt      # Your Kindle clippings file (add this)
|-- pdf_exports/          # Generated PDFs
```

## Kindle Clippings Format

The tool expects the standard Kindle clippings format:

```
Book Title (Author Name)
- Your Highlight on page 5 | Location 105-106 | Added on Monday, December 25, 2023 8:55:17 PM

Your highlighted text here
==========
```

## Troubleshooting

- **File Not Found**: Make sure `My Clippings.txt` is in the project directory
- **Python Command**: Use `python3` instead of `python` if needed
- **Dependencies**: Install with `pip3 install -r requirements.txt` if `pip` doesn't work
