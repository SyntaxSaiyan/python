#!/usr/bin/env python3
"""
PDF Exporter for Kindle Notes
Generates beautifully formatted PDFs for printing
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import black, darkblue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re
from kindle_organizer import KindleOrganizer, Note

class PDFExporter:
    """Export Kindle notes to PDF format"""
    
    def __init__(self, organizer: KindleOrganizer):
        self.organizer = organizer
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='BookTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=20,
            textColor=darkblue,
            alignment=1  # Center
        ))
        
        # Note header style
        self.styles.add(ParagraphStyle(
            name='NoteHeader',
            parent=self.styles['Heading3'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=12,
            textColor=darkblue
        ))
        
        # Note content style
        self.styles.add(ParagraphStyle(
            name='NoteContent',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20,
            leading=14
        ))
        
        # Separator style
        self.styles.add(ParagraphStyle(
            name='Separator',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=8,
            alignment=1  # Center
        ))
    
    def export_book_to_pdf(self, book_key: str, output_dir: str = "pdf_exports") -> str:
        """Export a single book's notes to PDF"""
        if book_key not in self.organizer.get_books():
            raise ValueError(f"Book '{book_key}' not found")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', book_key).strip()
        filename = os.path.join(output_dir, f"{safe_title}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        notes = self.organizer.get_books()[book_key]
        
        # Add title
        story.append(Paragraph(book_key, self.styles['BookTitle']))
        story.append(Spacer(1, 20))
        
        # Add summary
        summary_text = f"Total Notes: {len(notes)} | Generated on {self._get_current_date()}"
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Add notes
        for i, note in enumerate(notes, 1):
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
            if i < len(notes):
                story.append(Paragraph("•" * 30, self.styles['Separator']))
        
        # Build PDF
        doc.build(story)
        
        # Mark as printed
        self.organizer.mark_as_printed(book_key)
        
        return filename
    
    def export_all_books_to_pdf(self, output_dir: str = "pdf_exports") -> list:
        """Export all books to separate PDF files"""
        exported_files = []
        books = self.organizer.get_books()
        
        for book_key in books:
            try:
                filename = self.export_book_to_pdf(book_key, output_dir)
                exported_files.append(filename)
                print(f"Exported: {filename}")
            except Exception as e:
                print(f"Error exporting {book_key}: {e}")
        
        return exported_files
    
    def export_combined_pdf(self, book_keys: list, output_filename: str = None) -> str:
        """Export multiple books to a single combined PDF"""
        if not output_filename:
            output_filename = "combined_notes.pdf"
        
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Add title page
        story.append(Paragraph("Kindle Notes Collection", self.styles['BookTitle']))
        story.append(Spacer(1, 20))
        
        book_titles = ", ".join(book_keys[:3])
        if len(book_keys) > 3:
            book_titles += f" and {len(book_keys) - 3} more"
        
        story.append(Paragraph(f"Books: {book_titles}", self.styles['Normal']))
        story.append(Paragraph(f"Generated on {self._get_current_date()}", self.styles['Normal']))
        story.append(PageBreak())
        
        # Add each book
        for book_key in book_keys:
            if book_key not in self.organizer.get_books():
                continue
            
            notes = self.organizer.get_books()[book_key]
            
            # Book title
            story.append(Paragraph(book_key, self.styles['BookTitle']))
            story.append(Spacer(1, 15))
            
            # Notes
            for i, note in enumerate(notes, 1):
                header_text = f"{i}. {note.note_type}"
                if note.page:
                    header_text += f" | Page {note.page}"
                header_text += f" | Location {note.location}"
                
                story.append(Paragraph(header_text, self.styles['NoteHeader']))
                content_text = self._escape_xml(note.content)
                story.append(Paragraph(content_text, self.styles['NoteContent']))
                
                if i < len(notes):
                    story.append(Paragraph("•" * 20, self.styles['Separator']))
            
            # Page break between books (except last)
            if book_key != book_keys[-1]:
                story.append(PageBreak())
        
        doc.build(story)
        return output_filename
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters for PDF"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _get_current_date(self) -> str:
        """Get current date in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")

def main():
    """Command line interface for PDF export"""
    import argparse
    from kindle_organizer import KindleParser
    
    parser = argparse.ArgumentParser(description='Export Kindle Notes to PDF')
    parser.add_argument('clippings_file', help='Path to My Clippings.txt file')
    parser.add_argument('--book', help='Export specific book')
    parser.add_argument('--all', action='store_true', help='Export all books')
    parser.add_argument('--combined', nargs='+', help='Export multiple books to combined PDF')
    parser.add_argument('--output-dir', default='pdf_exports', help='Output directory')
    
    args = parser.parse_args()
    
    # Load notes
    kindle_parser = KindleParser(args.clippings_file)
    notes = kindle_parser.parse()
    organizer = KindleOrganizer(notes)
    
    # Create PDF exporter
    exporter = PDFExporter(organizer)
    
    if args.book:
        try:
            filename = exporter.export_book_to_pdf(args.book, args.output_dir)
            print(f"Exported {args.book} to {filename}")
        except ValueError as e:
            print(f"Error: {e}")
    
    elif args.all:
        files = exporter.export_all_books_to_pdf(args.output_dir)
        print(f"Exported {len(files)} books to {args.output_dir}")
    
    elif args.combined:
        filename = exporter.export_combined_pdf(args.combined)
        print(f"Exported combined PDF to {filename}")
    
    else:
        print("Please specify --book, --all, or --combined")

if __name__ == "__main__":
    main()
