import json
from pprint import pprint


def get_unique_fonts(words_json_path):
    with open(words_json_path, "r", encoding="utf-8") as f:
        words_json = json.loads(f.read())
    unique_fonts = set()

    for word_entry in words_json:
        unique_fonts.add(word_entry["font"].split(" ")[0])
    return unique_fonts


all_unique_fonts = set()
pdf_file_path_wo_ext = ""
for page_no in range(1, 25):
    fill_char = "0"
    words_json_path = r"{pdf_file_path_wo_ext}_{:{fill_char}3}_words.json".format(page_no, fill_char=fill_char)
    unique_fonts = get_unique_fonts(words_json_path)
    all_unique_fonts = all_unique_fonts.union(unique_fonts)
    # print(words_json_path)
    print(len(unique_fonts))
    # print(unique_fonts)
print(len(all_unique_fonts))
pprint(all_unique_fonts)
