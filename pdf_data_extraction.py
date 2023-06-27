from pathlib import Path
from typing import Iterable, Any
from pdfminer.high_level import extract_pages
import json
import os


def show_ltitem_hierarchy(o: Any, all_outputs):
    element_type = get_intended_name(o)
    if element_type == "LTPage":
        bbox = get_optional_bbox(o)
        all_outputs.append([element_type, bbox])
    elif element_type == "LTTextBoxHorizontal":
        bbox = get_optional_bbox(o)
        text = get_optional_text(o)
        font_info = get_optional_font_info(o)
        all_outputs.append([element_type, bbox, text, font_info])
    elif element_type == "LTTextLineHorizontal":
        bbox = get_optional_bbox(o)
        text = get_optional_text(o)
        font_info = get_optional_font_info(o)
        all_outputs.append([element_type, bbox, text, font_info])
    elif element_type == "LTChar":
        bbox = get_optional_bbox(o)
        text = get_optional_text(o)
        font_info = get_optional_font_info(o)
        all_outputs.append([element_type, bbox, text, font_info])
    elif element_type == "LTAnno":
        all_outputs.append([element_type])
    
    if isinstance(o, Iterable):
        for i in o:
            show_ltitem_hierarchy(i, all_outputs)
    return all_outputs
        
        
def get_intended_name(o: Any):
    return o.__class__.__name__


def get_optional_bbox(o: Any):
    if hasattr(o, 'bbox'):
        bbox_dict = {
            "bottom_left_x": o.x0,
            "bottom_left_y": o.y0,
            "top_right_x": o.x1,
            "top_right_y": o.y1
        }
        return bbox_dict


def get_optional_text(o: Any):
    if hasattr(o, "get_text"):
        return o.get_text().strip()
    return ""


def get_optional_font_info(o: Any):
    if hasattr(o, "fontname") and hasattr(o, 'size'):
        return f"{o.fontname} {round(o.size)}pt"
    return ""


def get_all_outputs(file_path):
    path = Path(file_path).expanduser()
    pages = extract_pages(path)
    # pages = extract_pages(path, laparams)
    all_outputs = []
    all_outputs = show_ltitem_hierarchy(pages, all_outputs)
    return all_outputs


def get_page_wise_data(all_outputs):
    page_wise_data = {}
    current_page_no = 0
    current_page_height = 0
    current_page_width = 0
    for i in range(len(all_outputs)):
        current_element = all_outputs[i]
        current_element_type = current_element[0]
        if current_element_type == "LTPage":
            bbox = current_element[1]
            current_page_no += 1
            current_page_height = bbox["top_right_y"]
            current_page_width = bbox["top_right_x"]
            page_wise_data[current_page_no] = {}
            page_wise_data[current_page_no]["id"] = current_page_no
            page_wise_data[current_page_no]["bbox"] = bbox
            page_wise_data[current_page_no]["character_data"] = []
        
        elif current_element_type == "LTChar":
            bbox = current_element[1]
            text = current_element[2]
            font_info = current_element[3]
            
            page_height = current_page_height
            image_coordinate_top_left_x = bbox["bottom_left_x"]
            image_coordinate_top_left_y = page_height - bbox["top_right_y"]
            image_coordinate_bottom_right_x = bbox["top_right_x"]
            image_coordinate_bottom_right_y = page_height - bbox["bottom_left_y"]
            
            x1 = image_coordinate_top_left_x
            y1 = image_coordinate_top_left_y
            x2 = image_coordinate_bottom_right_x
            y2 = image_coordinate_bottom_right_y
            
            # for the case of very close space
            if text == "":
                text = " "
            current_character_info = {
                "character_id": len(page_wise_data[current_page_no]["character_data"]),
                "text": text,
                "font": f"{font_info}",
                "bbox": [round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)]
            }
            page_wise_data[current_page_no]["character_data"].append(current_character_info)
        elif current_element_type == "LTAnno":
            if i+1 < len(all_outputs):
                next_element = all_outputs[i+1]
                previous_element = all_outputs[i-1]
                
                next_element_type = next_element[0]
                if next_element_type == "LTChar":
                    # space
                    page_height = current_page_height
                    image_coordinate_top_left_x = previous_element[1]["top_right_x"]
                    image_coordinate_top_left_y = page_height - previous_element[1]["top_right_y"]
                    image_coordinate_bottom_right_x = next_element[1]["bottom_left_x"]
                    image_coordinate_bottom_right_y = page_height - next_element[1]["bottom_left_y"]
                    
                    x1 = image_coordinate_top_left_x
                    y1 = image_coordinate_top_left_y
                    x2 = image_coordinate_bottom_right_x
                    y2 = image_coordinate_bottom_right_y
                    
                    text = " "
                    current_character_info = {
                        "character_id": len(page_wise_data[current_page_no]["character_data"]),
                        "text": text,
                        "font": f"{font_info}",
                        "bbox": [round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)]
                    }
                    page_wise_data[current_page_no]["character_data"].append(current_character_info)

                elif next_element_type == "LTTextLineHorizontal":
                    # new line
                    page_height = current_page_height
                    page_width = current_page_width

                    image_coordinate_top_left_x = previous_element[1]["top_right_x"]
                    image_coordinate_top_left_y = page_height - previous_element[1]["top_right_y"]
                    image_coordinate_bottom_right_x = page_width
                    image_coordinate_bottom_right_y = page_height - next_element[1]["bottom_left_y"]

                    x1 = image_coordinate_top_left_x
                    y1 = image_coordinate_top_left_y
                    x2 = image_coordinate_bottom_right_x
                    y2 = image_coordinate_bottom_right_y
                    
                    text = "\n"
                    current_character_info = {
                        "character_id": len(page_wise_data[current_page_no]["character_data"]),
                        "text": text,
                        "font": f"{font_info}",
                        "bbox": [round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)]
                    }
                    page_wise_data[current_page_no]["character_data"].append(current_character_info)

                elif next_element_type == "LTTextBoxHorizontal":
                    # paragraph
                    # TODO: need to review this part of code, as it might not be correct 
                    page_height = current_page_height
                    page_width = current_page_width

                    image_coordinate_top_left_x = previous_element[1]["top_right_x"]
                    image_coordinate_top_left_y = page_height - previous_element[1]["top_right_y"]
                    image_coordinate_bottom_right_x = page_width
                    image_coordinate_bottom_right_y = page_height - next_element[1]["bottom_left_y"]

                    x1 = image_coordinate_top_left_x
                    y1 = image_coordinate_top_left_y
                    x2 = image_coordinate_bottom_right_x
                    y2 = image_coordinate_bottom_right_y
                    
                    text = "\n"
                    current_character_info = {
                        "character_id": len(page_wise_data[current_page_no]["character_data"]),
                        "text": text,
                        "font": f"{font_info}",
                        "bbox": [round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)]
                    }
                    page_wise_data[current_page_no]["character_data"].append(current_character_info)
    return page_wise_data


def extract_character_info(file_path):
    # from pdfminer.layout import LAParams
    # word_margin = 4
    # laparams = LAParams(word_margin=word_margin)
    all_outputs = get_all_outputs(file_path)
    page_wise_data = get_page_wise_data(all_outputs)
    return page_wise_data, all_outputs


def extract_word_info(page_wise_data):
    page_wise_words = {}
    for page_no in page_wise_data:
        current_page_data = page_wise_data[page_no]
        character_data = current_page_data["character_data"]
        current_word_id = None
        word_groupings = [[]]
        for i in range(len(character_data)):
            current_character_info = character_data[i]
            current_text = current_character_info["text"]
            if current_text != " " and current_text != "\n":
                character_entry = {"is_word_terminating_character": False, "data": current_character_info}
                if len(word_groupings) > 1:
                    # when last entry in the previous list was a terminating character
                    if word_groupings[-1][-1]["is_word_terminating_character"]:
                        word_groupings.append([])
                        word_groupings[-1].append(character_entry)
                    else:
                        word_groupings[-1].append(character_entry)
                else:
                    word_groupings[-1].append(character_entry)

            elif current_text == " " or current_text == "\n":
                character_entry = {"is_word_terminating_character": True, "data": current_character_info}
                # the issue of last entry being a terminating or non-terminating character is resolved when inserting characters
                word_groupings.append([])
                word_groupings[-1].append(character_entry)

        all_words = []
        word_id = 0
        for word_grouping in word_groupings:
            if not word_grouping[0]["is_word_terminating_character"]:
                current_word_top_left_x = word_grouping[0]["data"]["bbox"][0]
                current_word_top_left_y = word_grouping[0]["data"]["bbox"][1]
                current_word_bottom_right_x = word_grouping[-1]["data"]["bbox"][2]
                current_word_bottom_right_y = word_grouping[-1]["data"]["bbox"][3]
                current_font = word_grouping[0]["data"]["font"]
                current_word = "".join([character_entry["data"]["text"] for character_entry in word_grouping])
                word_id += 1
                all_words.append({
                    "word_id": word_id,
                    "text": current_word,
                    "font": current_font,
                    "bbox": [current_word_top_left_x, current_word_top_left_y, current_word_bottom_right_x, current_word_bottom_right_y]
                })
            else:
                word_id += 1
                all_words.append({
                    "word_id": word_id,
                    "text": word_grouping[0]["data"]["text"],
                    "font": word_grouping[0]["data"]["font"],
                    "bbox": word_grouping[0]["data"]["bbox"]
                })

        page_wise_words[page_no] = all_words
    return page_wise_words


def convert_coordinates_to_top_left_origin(coordinates, page_height):
    x1, y1, x2, y2 = coordinates['bottom_left_x'], page_height-coordinates['top_right_y'], coordinates['top_right_x'], page_height-coordinates['bottom_left_y']
    return [x1, y1, x2, y2]


def extract_textbox_horizontal_info(all_outputs):
    page_height = all_outputs[0][1]["top_right_y"]
    page_wise_textbox_horizontals = {}
    page_no = 0
    textbox_id = 0
    for current_element in all_outputs:
        if current_element[0] == "LTPage":
            page_no += 1
            page_wise_textbox_horizontals[page_no] = []
        elif current_element[0] == "LTTextBoxHorizontal":
            textbox_id += 1
            textbox_element = {
                "textbox_id": textbox_id,
                "text": current_element[2],
                "font": current_element[3],
                "bbox": convert_coordinates_to_top_left_origin(current_element[1], page_height)
            }
            page_wise_textbox_horizontals[page_no].append(textbox_element)
    return page_wise_textbox_horizontals


if __name__ == "__main__":
    # file_path = r"1802.05574v2.pdf"
    file_path = input("file_path: ")
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    page_wise_data, all_outputs = extract_character_info(file_path)
    page_wise_words = extract_word_info(page_wise_data)

    with open(f"{filename_wo_ext}_all_outputs.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(all_outputs, indent=4))

    with open(f"{filename_wo_ext}_page_wise_data.json", "w", encoding="utf-8") as f:
        json.dump(page_wise_data, f, indent=4)

    
    with open(f"{filename_wo_ext}_page_wise_words.json", "w", encoding="utf-8") as f:
        json.dump(page_wise_words, f, indent=4)
    
    with open("page_words.txt", "w", encoding="utf-8") as f:
        for page_no in page_wise_words:
            for word in page_wise_words[page_no]:
                f.write(word["text"])
            f.write("="*150)
