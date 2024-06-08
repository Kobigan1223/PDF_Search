import fitz  # PyMuPDF
import os

def highlight_word_in_pdf(pdf_path, word, exact_match=False):
    document = fitz.open(pdf_path)
    word = word.lower()
    highlights = {}

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text = page.get_text().lower().split()  # Get lowercase words from the page

        if exact_match:
            # Check if the word exactly matches any word in the page text
            if word in text:
                # If the word is found, create a highlight annotation
                highlights[page_num + 1] = 1  # Count occurrences as 1
                highlight_instances = page.search_for(word)
                for inst in highlight_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()
        else:
            # Perform regular search and highlighting
            text_instances = page.search_for(word)
            if text_instances:
                highlights[page_num + 1] = len(text_instances)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()

    if highlights:
        modified_pdf_path = pdf_path.replace(".pdf", "_highlighted.pdf")
        document.save(modified_pdf_path)
        document.close()
        return modified_pdf_path, highlights
    else:
        document.close()
        return None, None

def search_in_folder(folder_path, word, exact_match=False):
    search_results = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            modified_pdf_path, results = highlight_word_in_pdf(pdf_path, word, exact_match)
            if results:
                search_results[filename] = (modified_pdf_path, results)
    return search_results
