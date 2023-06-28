### A quick script to help Jokke extract data out of pdfs ###

### database class

class Local_DB(object):

    def __init__(self, db = None):
        self.db = sl.connect('local_etsi_database.db')
        self.generate_db()

    def generate_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS PDFS(
                id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                url         TEXT NOT NULL,
                title       TEXT,
                contents    TEXT NOT NULL
            );
            """)
    def insert_new(self,
                   url      : str = "none",
                   title    : str = "no_title",
                   contents : str = "",
                   ):
        c = self.db.cursor()
        data = (
            url,
            title,
            contents
        )
        query = 'INSERT INTO PDFS (url, title, contents) VALUES (?,?,?)'
        self.db.execute(query, data)
        self.db.commit()

    def check_if_exists(self, url) -> bool:
        query = 'SELECT * FROM PDFS WHERE url = ?'
        c = self.db.cursor()
        r = c.execute(query, (url, ))
        res = r.fetchall()
        c.close()
        if len(res) > 0:
            return True
        else:
            return False

    def get_data_for_csv(self):
        query = 'SELECT * FROM PDFS'
        c = self.db.cursor()
        r = c.execute(query)
        rows = r.fetchall()
        c_names = [desc[0] for desc in  c.description]
        c.close()
        return c_names, rows

### Imports ###
import PyPDF2
import sys
import re
import csv
import requests
import io
import hashlib
import sqlite3 as sl

### Globals
gathered_text = ""

def extract_start_and_end(reader, len_p):
    s_n = 0
    e_n = len(reader.pages)
    for r in range(len_p):
        page = reader.pages[r]
        s = page.extract_text()
        start_re = r'\b(\d+)\b\s+4\s.*(?:\.+\s*){10,}(\d+)'
        end_re = r'Annex.*(?:\.+\s*){10,}(\d+)'
        match = re.search(start_re, s)
        if match and s_n == 0:
            s_n = match.group(2)
            # start found, now find the end on the same rotation
        match = re.search(end_re, s)
        if match and e_n == len(reader.pages):
            e_n = match.group(1)
    return [s_n, e_n]

def extract_page(text, cm, tm, font_dict, font_size):
    y = tm[5]
    x = tm[4]
    if y > 50 and y < 750:
        if x < 115:
            global gathered_text
            gathered_text += text

def store_in_db(url, title, db):
    global gathered_text
    db.insert_new(url, title, gathered_text)
    gathered_text = ""

def extract_pdf(pdf_url, db):
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            pdf_bytes = response.content
            pdf_stream = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            len_p = int((len(pdf_reader.pages) * 25) / 100)
            start, end = extract_start_and_end(pdf_reader, len_p)
            meta = pdf_reader.metadata
            print(pdf_url)
            print(meta.title)
            print(meta.subject)
            print(start)
            print(end)
            for page in range(int(start) -1, int(end)-1):
                pdf_page = pdf_reader.pages[page]
                pdf_page.extract_text(visitor_text=extract_page)
            store_in_db(pdf_url,meta.title, db)

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

def write_csv(c_names, rows):
    try:
        print("Starting to create local csv file")
        with open('etsi_data.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(c_names)
            csv_writer.writerows(rows)
        print("Done! file \'etsi_data.csv\' created.")
    except Exception as err:
        print("Something went wrong with csv creation. Error msg:")
        print(err)


def get_pdfs(links, db):
    for link in links:
        if db.check_if_exists(link) is False:
            extract_pdf(link, db)
        else:
            print("Url already found in local database. Skipping..")
    c_names, rows = db.get_data_for_csv()
    write_csv(c_names, rows)


def main():
    if len(sys.argv) < 2:
        print("give me path")
        sys.exit(1)
    else:
        file_path = sys.argv[1]
        db = Local_DB()
        get_pdfs(get_links(file_path), db)


if __name__ == "__main__":
    main()


