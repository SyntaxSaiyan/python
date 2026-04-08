#!/usr/bin/env python3
"""
Kindle Notes Organizer
A tool to parse and export Kindle clippings to PDF
"""

import re
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path
import argparse

@dataclass
class Note:
    """Represents a single Kindle note/highlight"""
    book_title: str
    author: str
    note_type: str  # Highlight, Note, Bookmark
    page: Optional[str]
    location: str
    added_date: str
    content: str
    
    @property
    def book_key(self) -> str:
        """Unique key for book identification"""
        return f"{self.book_title} ({self.author})"

class KindleParser:
    """Parser for Kindle My Clippings.txt file"""
    
    def __init__(self, clippings_file: str):
        self.clippings_file = clippings_file
        self.notes: List[Note] = []
        
    def parse(self) -> List[Note]:
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
    
    def _parse_entry(self, entry: str) -> Optional[Note]:
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
        
        # Parse metadata line: "- Your Highlight on page 5 | Location 105-106 | Added on Monday, December 25, 2023 8:55:17 PM"
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

class KindleOrganizer:
    """Main organizer class for Kindle notes"""
    
    def __init__(self, notes: List[Note]):
        self.notes = notes
        self.printed_books = set()
        
    def get_books(self) -> Dict[str, List[Note]]:
        """Group notes by book"""
        books = {}
        for note in self.notes:
            if note.book_key not in books:
                books[note.book_key] = []
            books[note.book_key].append(note)
        return books
    
    def search_notes(self, query: str) -> List[Note]:
        """Search notes by content"""
        query_lower = query.lower()
        return [note for note in self.notes if query_lower in note.content.lower()]
    
    def get_book_stats(self) -> Dict[str, int]:
        """Get statistics for each book"""
        books = self.get_books()
        return {book: len(notes) for book, notes in books.items()}
    
    def mark_as_printed(self, book_key: str):
        """Mark a book as printed"""
        self.printed_books.add(book_key)
    
    def get_unprinted_books(self) -> List[str]:
        """Get list of books that haven't been printed"""
        all_books = set(self.get_books().keys())
        return list(all_books - self.printed_books)
    
    def export_to_json(self, filename: str):
        """Export notes to JSON format"""
        data = {
            'notes': [asdict(note) for note in self.notes],
            'printed_books': list(self.printed_books),
            'export_date': datetime.now().isoformat()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_book_to_text(self, book_key: str, output_dir: str = "exports"):
        """Export a single book's notes to text file"""
        if book_key not in self.get_books():
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', book_key).strip()
        filename = os.path.join(output_dir, f"{safe_title}.txt")
        
        notes = self.get_books()[book_key]
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{book_key}\n")
            f.write("=" * len(book_key) + "\n\n")
            
            for note in notes:
                f.write(f"{note.note_type} - ")
                if note.page:
                    f.write(f"Page {note.page} - "
                f"Location {note.location}\n")
                f.write(f"Added: {note.added_date}\n")
                f.write(f"\n{note.content}\n")
                f.write("-" * 50 + "\n\n")
        
        print(f"Exported {len(notes)} notes to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Kindle Notes Organizer')
    parser.add_argument('clippings_file', help='Path to My Clippings.txt file')
    parser.add_argument('--search', help='Search notes')
    parser.add_argument('--list-books', action='store_true', help='List all books')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export-json', help='Export to JSON file')
    parser.add_argument('--export-book', help='Export specific book to text file')
    parser.add_argument('--printed', help='Mark book as printed (book key)')
    
    args = parser.parse_args()
    
    # Parse clippings
    kindle_parser = KindleParser(args.clippings_file)
    notes = kindle_parser.parse()
    organizer = KindleOrganizer(notes)
    
    print(f"Loaded {len(notes)} notes from {len(organizer.get_books())} books")
    
    if args.search:
        results = organizer.search_notes(args.search)
        print(f"\nFound {len(results)} notes matching '{args.search}':")
        for note in results[:10]:  # Show first 10
            print(f"\n{note.book_key}")
            print(f"{note.content[:100]}...")
    
    if args.list_books:
        print("\nBooks:")
        for book, notes in organizer.get_books().items():
            print(f"  {book} ({len(notes)} notes)")
    
    if args.stats:
        stats = organizer.get_book_stats()
        print(f"\nStatistics:")
        print(f"Total notes: {len(notes)}")
        print(f"Total books: {len(stats)}")
        print(f"Average notes per book: {len(notes)/len(stats):.1f}")
    
    if args.export_json:
        organizer.export_to_json(args.export_json)
        print(f"Exported to {args.export_json}")
    
    if args.export_book:
        organizer.export_book_to_text(args.export_book)
    
    if args.printed:
        organizer.mark_as_printed(args.printed)
        print(f"Marked '{args.printed}' as printed")

if __name__ == "__main__":
    main()
