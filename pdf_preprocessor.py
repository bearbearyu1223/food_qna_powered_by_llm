from PyPDF2 import PdfReader
from typing import Dict
import os
import json

def extract_content_from_pdfs(book_dir:str)->Dict:
    pdf_files = sorted([x for x in os.listdir(book_dir) if 'DS_Store' not in x])
    books = {} # key: book title, value: book (dict) below
    for p in pdf_files:
        pdf_path = os.path.join(book_dir,p)
        reader = PdfReader(pdf_path)
        book = {}
        if reader is not None:
            if len(reader.pages) > 0:
                for i in range(len(reader.pages)):
                    page_content = {}
                    if reader.pages[i]:
                        page = reader.pages[i]
                        page_content['page_num'] = i
                        page_content['len_of_raw_text'] = len(page.extract_text()) if len(page.extract_text())>0 else 0 
                        page_content['raw_text'] = page.extract_text() if len(page.extract_text())>0 else ''
                    book["page_"+str(i)] = page_content
        books[reader.metadata.title] = book
        return books

if __name__ == '__main__':
    book_dir = os.path.join(os.curdir,'cook_book_data')
    books = extract_content_from_pdfs(book_dir=book_dir)
    with open("sample.json", "w") as outfile:
            json.dump(books, outfile, indent = 4)