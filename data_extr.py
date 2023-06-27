### A quick script to help Jokke extract data out of pdfs ###

### Imports ###
import PyPDF2
import sys
import re
import csv
import requests
import io


def extract_start_and_end(reader, len_p):
    s_n = 0
    e_n = len(reader.pages)
    for r in range(len_p):
        page = reader.pages[r]
        s = page.extract_text(visitor_text=extract_page)
        start_re = r'\b(\d+)\b\s+General\s*(?:\.+\s*){10,}(\d+)'
        end_re = r'Annex.*(?:\.+\s*){10,}(\d+)'
        if s_n == 0:
            match = re.search(start_re, s)
            if match:
                s_n = match.group(2)
                # start found, now find the end on the same rotation
        else:
            match = re.search(end_re, s)
            if match:
                e_n = match.group(1)
    return [s_n, e_n]

def extract_page(text, cm, tm, font_dict, font_size):
    y = tm[5]
    x = tm[4]
    #if y > 50 and y < 720:
        #if x < 100:
            #print(text)

def extract_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            pdf_bytes = response.content
            pdf_stream = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            ext_text = ""
            len_p = int((len(pdf_reader.pages) * 15) / 100)
            start, end = extract_start_and_end(pdf_reader, len_p)
            print(start)
            print(end)
            for page in range(int(start), len(pdf_reader.pages)):
                pdf_page = pdf_reader.pages[page]
                ext_text += pdf_page.extract_text(visitor_text=extract_page)
    except Exception as err:
        print("something failed in pdf extraction.")
        print(err)


def get_links(target_file):
    with open(target_file, 'r') as csvfile:
        links = []
        pdf_link_re = r"http://www\.etsi\.org.*?\.pdf"
        reader = csv.DictReader(csvfile)
        for row in reader:
            for v in row.values():
                match = re.search(pdf_link_re, str(v))
                if match:
                    links.append(match.group().strip())
        return links

def get_pdfs(links):
    for link in links:
        extract_pdf(link)

def main():
    if len(sys.argv) < 2:
        print("give me path")
        sys.exit(1)
    else:
        file_path = sys.argv[1]
        get_pdfs(get_links(file_path))


if __name__ == "__main__":
    main()
