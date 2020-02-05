# from keras.utils import get_file
from SAX_utility import WikiXmlHandler
import subprocess
import xml
import mwparserfromhell
import re
import os
from SQLite3_utility import create_connection, insert_record, get_counts


filename = 'enwiki-20191101-pages-articles4.xml-p200511p352689.bz2'

sqlite3_path = "path_to_the_sqlite3_db"
data_path = "../../.keras/datasets/" + filename

save_file_dir = "path/save/the/raw/text/of/wikipage"


def process_page(page_obj, pdir):
    entity_name = str(page_obj[0])
    wikicode = str(page_obj[1])
    clean_text = wikicode.partition("\n }} \n")[-1]

    clean_text2 = mwparserfromhell.parse(clean_text)

    wikilinks = [(str(x.title), str(x.title)) if x.text is None else (str(x.text), str(x.title)) for x in
                 clean_text2.filter_wikilinks()]
    wikilinks = dict(wikilinks)

    first_paragraph = re.split("\n", clean_text2.strip_code().strip())[0]
    for key in list(wikilinks):
        if key not in first_paragraph:
            wikilinks.pop(key, None)

    print(entity_name)
    print("\n")
    # print(first_paragraph)
    # print(wikilinks)
    if len(first_paragraph) <= 50:
        print("drop this one")
    else:
    	## codes for extract the first paragraph contents
        try:
            with open(os.path.join(pdir, entity_name + ".txt"), "w+") as wf:
                wf.write(first_paragraph)
                wf.write("\n\n")
                for item in wikilinks.keys():
                    wf.write(item + "||" + wikilinks[item])
                    wf.write("\n")
                wf.close()
    
        except:
            print("something wrong!!!!")

    print("-------------------------------")

    return entity_name


# Prepare the Geography and Place infobox items
infoboxes = set([line.rstrip('\n') for line in open("infobox_new.txt", "r")])

print(infoboxes)
# Object for handling xml
handler = WikiXmlHandler(infoboxes)
# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
# Iteratively process file
db_conn = create_connection(sqlite3_path)
start_ID = get_counts(db_conn)

for line in subprocess.Popen(['bzcat'],
                             stdin=open(data_path),
                             stdout=subprocess.PIPE).stdout:

    parser.feed(line)

    if len(handler._pages) > old_pages:
        location = process_page(handler._pages[old_pages], save_file_dir)
        old_pages = len(handler._pages)
        insert_record(db_conn, (start_ID+old_pages, str(location)))
