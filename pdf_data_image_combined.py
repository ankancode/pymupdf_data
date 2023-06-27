import json
import os

from pdf_data_extraction import get_all_outputs, extract_textbox_horizontal_info
from pdf_image_extraction import extract_image_info


def get_image_insertion_index(combined_list, image_bbox):
    # logic is that if the image's y1 (top left y) is greater than current textbox, it should be inserted before the current textbox
    for i in range(len(combined_list)-1, -1, -1):
        if image_bbox[1] > combined_list[i]["bbox"][1]:
            return i+1
    return 0


if __name__ == "__main__":
    file_path = input("file_path: ")
    images_output_folder = input("images_output_folder: ")
    os.makedirs(images_output_folder, exist_ok=True)
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    all_outputs = get_all_outputs(file_path)
    page_wise_textbox_horizontals = extract_textbox_horizontal_info(all_outputs)
    extracted_image_json = extract_image_info(file_path, images_output_folder)
    all_combined_list = {}
    for page_no in page_wise_textbox_horizontals.keys():
        textbox_list = page_wise_textbox_horizontals[page_no]
        images_list = extracted_image_json[page_no]
        combined_list = textbox_list[:]
        if images_list:
            for image in images_list:
                image_bbox = image["bbox"]
                insertion_index = get_image_insertion_index(combined_list, image_bbox)
                combined_list.insert(insertion_index, image)
        all_combined_list[page_no] = combined_list
    with open(f"{filename_wo_ext}_all_combined.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(all_combined_list, indent=4))