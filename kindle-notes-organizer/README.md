I wanted to export my Kindle notes and highlights but found that clippings.io only gives you the first 100 characters of each highlight in the free version. This meant most of my notes were incomplete and practically meaningless.

So I teamed up with Windsurf to create a quick Python script that parses through the `My Clippings.txt` file and creates reader-friendly PDF documents. Now I can print them and have physical copies to easily access whenever I want to be reminded of the lessons I learned from the books I've read.

# Kindle Notes Organizer

Turn your Kindle highlights into beautiful, printable PDFs. Perfect for book lovers who want physical copies of their reading notes!

## What This Does

Instead of losing your highlights to the 100-character limit, this tool:
- **Preserves every word** of your notes and highlights
- **Creates one PDF per book** - clean and organized
- **Makes printing easy** - perfect for physical reference

## Easy Setup (3 Simple Steps)

### Step 1: Get the Tool

**Option A: Quick & Easy (No Git Required)**
1. Go to: https://github.com/SyntaxSaiyan/python/tree/main/kindle-notes-organizer
2. Click on `kindle_to_pdf.py` and copy the code
3. Create 1 new text file on your computer:
   - `kindle_to_pdf.py` (paste the code)
4. Save it in a new folder called "kindle-notes"

**Option B: GitHub Method**
1. Open terminal and run: `git clone https://github.com/SyntaxSaiyan/python.git`
2. Navigate to: `cd python/kindle-notes-organizer`

### Step 2: Install the Tool

Open your computer's terminal/command prompt and run:
```bash
pip install reportlab
```

*Don't have pip? No worries! Just search "install pip" for your computer type (Mac/Windows).*

### Step 3: Get Your Kindle Notes

1. **Connect your Kindle** to your computer with the USB cable
2. **Open the Kindle folder** like you would any USB drive
3. **Find the "documents" folder** inside your Kindle
4. **Copy "My Clippings.txt"** to the same folder as these scripts

### Step 4: Create Your PDFs

Run this simple command:
```bash
python3 kindle_to_pdf.py "My Clippings.txt" --all
```

That's it! You'll find beautiful PDF files in the new `pdf_exports/` folder.

## What You'll Get

- **One PDF per book** with all your highlights
- **Clean formatting** with page numbers and locations
- **Ready to print** - perfect A4 size
- **Organized by book title and author**

## Need Help with One Book Only?

```bash
python3 kindle_to_pdf.py "My Clippings.txt" --book "Book Title (Author)"
```

## Questions?

**"I'm scared of the terminal!"** - I promise this is beginner-friendly. Just copy-paste the commands exactly as shown.

**"Where do I find the terminal?"** 
- **Mac**: Search for "Terminal" in Spotlight
- **Windows**: Search for "Command Prompt" or "PowerShell"

**"Python isn't working!"** - Try `python` instead of `python3` in the commands above.

## Why This Matters

Your reading notes contain gold - insights, lessons, and reminders that deserve to be preserved. Don't let character limits truncate your learning!

---

*Built by a book lover, for book lovers. Happy reading!*
