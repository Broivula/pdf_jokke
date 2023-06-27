### A quick script to help Jokke extract data out of pdfs ###

### Imports ###
import PyPDF2
import sys
import re



### This function locates us our starting location. Generally speaking we want to only
### extract relevant information - meaning that we can ignore the forewords etc.
### Unfortunately for us, pdfs as a file format are terrible for this - which is why we have to 
### locate the good starting location (i.e. the page where 'General' starts) via regex.

### The regex matches a singular number, followed by the word 'General' and at least 10 periods
### and extracts the number at the end of the string (which is our coveted starting page).
### returns a default value of 0
def extract_starting_location(reader):
    for r in range(5):
        page = reader.pages[r]
        s = page.extract_text(visitor_text=extract_page)
        match = re.search(r'\b(\d+)\b\s+General\s*(?:\.+\s*){10,}(\d+)', s)
        if match:
            text = match.group(2)
            return text
    return 0

def extract_page(text, cm, tm, font_dict, font_size):
    y = tm[5]
    x = tm[4]
    #if y > 50 and y < 720:
        #if x < 100:
            #print(text)

def extract_pdf(target_file):
    with open(target_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        ext_text = ""
        start = extract_starting_location(pdf_reader)
        print(start)
        #page = pdf_reader.pages[10]
        #ext_text += page.extract_text(visitor_text=extract_page)
        for page in range(start, pdf_reader.pages):
            pdf_page = pdf_reader.pages(page)
            ext_text += pdf_page.extracted_text(visitor_text=extract_page)

def main():
    if len(sys.argv) < 2:
        print("give me path")
        sys.exit(1)
    else:
        file_path = sys.argv[1]
        extract_pdf(file_path)


if __name__ == "__main__":
    main()
