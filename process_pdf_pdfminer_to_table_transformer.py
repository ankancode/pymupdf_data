# this is for processing selectable pdf to table transformer format
import json
import os
from pdf_data_extraction import extract_character_info, extract_word_info


if __name__ == "__main__":
    file_path = input("file_path: ")
    output_folder = input("output_folder: ")
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    file_result_folder = os.path.join(output_folder, filename_wo_ext)
    os.makedirs(file_result_folder, exist_ok=True)
    
    page_wise_data, all_outputs = extract_character_info(file_path)
    page_wise_words = extract_word_info(page_wise_data)

    for page_no in page_wise_words:
        page_words = page_wise_words[page_no]
        fill_char = "0"
        padded_page_no = "{:{fill_char}3}".format(page_no, fill_char=fill_char)
        with open(os.path.join(file_result_folder, f"{filename_wo_ext}_{padded_page_no}_words.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(page_words, indent=4))
