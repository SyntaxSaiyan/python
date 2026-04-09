#!/usr/bin/env python3
"""
Kindle Notes to PDF Converter
One simple script to convert your Kindle clippings into printable PDFs
"""

import re
import os
import argparse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import darkblue
from reportlab.pdfbase.ttfonts import TTFont

class Note:
    """Represents a single Kindle note/highlight"""
    def __init__(self, book_title, author, note_type, page, location, added_date, content):
        self.book_title = book_title
        self.author = author
        self.note_type = note_type
        self.page = page
        self.location = location
        self.added_date = added_date
        self.content = content
    
    @property
    def book_key(self):
        """Unique key for book identification"""
        return f"{self.book_title} ({self.author})"

class KindleParser:
    """Parser for Kindle My Clippings.txt file"""
    
    def __init__(self, clippings_file):
        self.clippings_file = clippings_file
        self.notes = []
        
    def parse(self):
        """Parse the clippings file and return list of notes"""
        with open(self.clippings_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Split by separator and filter empty entries
        entries = [entry.strip() for entry in content.split('==========') if entry.strip()]
        
        for entry in entries:
            note = self._parse_entry(entry)
            if note:
                self.notes.append(note)
        
        return self.notes
    
    def _parse_entry(self, entry):
        """Parse a single entry"""
        lines = entry.split('\n')
        if len(lines) < 4:
            return None
        
        # Parse book line: "Book Title (Author)"
        book_line = lines[0].strip()
        author_match = re.search(r'\(([^)]+)\)$', book_line)
        if author_match:
            author = author_match.group(1)
            book_title = book_line[:author_match.start()].strip()
        else:
            book_title = book_line
            author = "Unknown"
        
        # Parse metadata line
        metadata_line = lines[1].strip()
        
        # Extract note type
        note_type = "Highlight"
        if "Note" in metadata_line:
            note_type = "Note"
        elif "Bookmark" in metadata_line:
            note_type = "Bookmark"
        
        # Extract page
        page = None
        page_match = re.search(r'page (\d+)', metadata_line)
        if page_match:
            page = page_match.group(1)
        
        # Extract location
        location = ""
        location_match = re.search(r'Location (\d+-?\d*)', metadata_line)
        if location_match:
            location = location_match.group(1)
        
        # Extract date
        date_match = re.search(r'Added on (.+)$', metadata_line)
        added_date = date_match.group(1) if date_match else ""
        
        # Content is everything after metadata line until empty lines
        content_lines = []
        for line in lines[2:]:
            if line.strip():
                content_lines.append(line.strip())
            else:
                break
        content = ' '.join(content_lines)
        
        # If content is empty, try to get all remaining lines
        if not content:
            content = ' '.join([line.strip() for line in lines[2:] if line.strip()])
        
        return Note(
            book_title=book_title,
            author=author,
            note_type=note_type,
            page=page,
            location=location,
            added_date=added_date,
            content=content
        )

class PDFExporter:
    """Export Kindle notes to PDF format"""
    
    def __init__(self, notes):
        self.notes = notes
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(self.styles['Title'].clone('BookTitle', fontSize=18, spaceAfter=20, textColor=darkblue, alignment=1))
        
        # Note header style
        self.styles.add(self.styles['Heading3'].clone('NoteHeader', fontSize=10, spaceAfter=6, spaceBefore=12, textColor=darkblue))
        
        # Note content style
        self.styles.add(self.styles['Normal'].clone('NoteContent', fontSize=11, spaceAfter=12, leftIndent=20, leading=14))
        
        # Separator style
        self.styles.add(self.styles['Normal'].clone('Separator', fontSize=8, spaceAfter=8, alignment=1))
    
    def export_book_to_pdf(self, book_key, output_dir="pdf_exports"):
        """Export a single book's notes to PDF"""
        # Get notes for this book
        book_notes = [note for note in self.notes if note.book_key == book_key]
        
        if not book_notes:
            print(f"No notes found for book: {book_key}")
            return None
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', book_key).strip()
        filename = os.path.join(output_dir, f"{safe_title}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        
        # Add title
        story.append(Paragraph(book_key, self.styles['BookTitle']))
        story.append(Spacer(1, 20))
        
        # Add summary
        summary_text = f"Total Notes: {len(book_notes)} | Generated on {self._get_current_date()}"
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Add notes
        for i, note in enumerate(book_notes, 1):
            # Note header
            header_text = f"{i}. {note.note_type}"
            if note.page:
                header_text += f" | Page {note.page}"
            header_text += f" | Location {note.location}"
            
            story.append(Paragraph(header_text, self.styles['NoteHeader']))
            
            # Note content
            content_text = self._escape_xml(note.content)
            story.append(Paragraph(content_text, self.styles['NoteContent']))
            
            # Separator (except for last note)
            if i < len(book_notes):
                story.append(Paragraph("•" * 30, self.styles['Separator']))
        
        # Build PDF
        doc.build(story)
        print(f"Exported {len(book_notes)} notes to {filename}")
        return filename
    
    def export_all_books_to_pdf(self, output_dir="pdf_exports"):
        """Export all books to separate PDF files"""
        # Group notes by book
        books = {}
        for note in self.notes:
            if note.book_key not in books:
                books[note.book_key] = []
            books[note.book_key].append(note)
        
        exported_files = []
        for book_key in books.keys():
            try:
                filename = self.export_book_to_pdf(book_key, output_dir)
                exported_files.append(filename)
            except Exception as e:
                print(f"Error exporting {book_key}: {e}")
        
        return exported_files
    
    def _escape_xml(self, text):
        """Escape XML special characters for PDF"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _get_current_date(self):
        """Get current date in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Export Kindle Notes to PDF')
    parser.add_argument('clippings_file', help='Path to My Clippings.txt file')
    parser.add_argument('--book', help='Export specific book')
    parser.add_argument('--all', action='store_true', help='Export all books')
    
    args = parser.parse_args()
    
    if not args.book and not args.all:
        print("Please specify --book 'Book Title (Author)' or --all")
        return
    
    # Parse clippings
    kindle_parser = KindleParser(args.clippings_file)
    notes = kindle_parser.parse()
    
    # Create PDF exporter
    exporter = PDFExporter(notes)
    
    if args.book:
        exporter.export_book_to_pdf(args.book)
    elif args.all:
        files = exporter.export_all_books_to_pdf()
        print(f"\nExported {len(files)} books to pdf_exports/")

if __name__ == "__main__":
    main()
