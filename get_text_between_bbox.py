import json
import os
import xmltodict


class BBox:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def __str__(self) -> str:
        return f"{self.x1}, {self.y1}, {self.x2}, {self.y2}"
    

class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
    def __str__(self) -> str:
        return f"{self.x}, {self.y}"


def get_inside_json(outer_bbox, words_json):
    inner_json = []
    outer_bbox = BBox(*outer_bbox)
    for word_entry in words_json:
        word_bbox = word_entry["bbox"]
        word_bbox = BBox(*word_bbox)
        if contains(word_bbox, outer_bbox):
            inner_json.append(word_entry)
        else:
            continue
    return inner_json


def get_outside_json(outer_bbox, words_json):
    # it will return a json which does not include words inside the outer_bbox
    # bbox coordinates are in pdf units
    # words_json coordinates are in pdf units
    # [
    #     {
    #     "word_id": 1,
    #     "text": "Open",
    #     "font": "VMGTJT+NimbusRomNo9L-Medi 14pt",
    #     "bbox": [
    #         105.373,
    #         64.741,
    #         138.857,
    #         79.087
    #         ]
    #     },
    # ]
    outer_json = []
    outer_bbox = BBox(*outer_bbox)
    for word_entry in words_json:
        word_bbox = word_entry["bbox"]
        word_bbox = BBox(*word_bbox)
        if contains(word_bbox, outer_bbox):
            continue
        else:
            outer_json.append(word_entry)
    return outer_json


def process_bbox(bbox_str):
    # bbox_str = bbox_str[1:-1]
    # bboxes = bbox_str.split(",")
    bboxes = bbox_str
    bboxes = list(map(float, bboxes))
    bbox = BBox(*bboxes)
    return bbox


def contains(small_box: BBox, big_box: BBox):
    top_left = Point(small_box.x1, small_box.y1)
    top_right = Point(small_box.x2, small_box.y1)
    bottom_left = Point(small_box.x1, small_box.y2)
    bottom_right = Point(small_box.x2, small_box.y2)
    
    if bbox_contains_point(big_box, top_left) or bbox_contains_point(big_box, top_right) or bbox_contains_point(big_box, bottom_left) or bbox_contains_point(big_box, bottom_right):
        return True
    return False


def bbox_contains_point(bbox: BBox, point: Point):
    if point.x >= bbox.x1 and point.x <= bbox.x2 and point.y >= bbox.y1 and point.y <= bbox.y2:
        return True
    return False


def xml_to_dictionary(xml_file_path):
    with open(xml_file_path, "r", encoding="utf-8") as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        json_data = json.dumps(data_dict, indent=4)
        data_dict2 = json.loads(json_data)
        return data_dict2


def get_pdf_coordinates_from_image_coordinates(image_bbox, image_dpi, pdf_dpi=72):
    image_to_pdf_conversion_factor = pdf_dpi/image_dpi

    # image_bbox are with origin at top left corner
    x1, y1, x2, y2 = image_bbox

    # Convert image coordinates (as the image might not necessarily be in 72 dpi) to pdf units, keeping origin at top left corner, as the bboxes inside words_json are in pdf units (72 dpi) with origin at top left corner
    x1_pdf = x1 * image_to_pdf_conversion_factor
    y1_pdf = y1 * image_to_pdf_conversion_factor
    x2_pdf = x2 * image_to_pdf_conversion_factor
    y2_pdf = y2 * image_to_pdf_conversion_factor

    # the outer_bbox coordinates have origin at top left corner, and are for pdf units (72 dpi)
    return x1_pdf, y1_pdf, x2_pdf, y2_pdf



if __name__ == "__main__":
    pdf_dpi = 72
    image_dpi = 96

    bboxes_json_path = r"_objects.json"
    # bboxes_json_path = input("bboxes_json_path: ")
    with open(bboxes_json_path, "r", encoding="utf-8") as f:
        bboxes_json = json.loads(f.read())
    
    # image_bbox are with origin at top left corner
    image_bbox = bboxes_json[0]["bbox"]

    # the outer_bbox coordinates have origin at top left corner, and are for pdf units (72 dpi)
    outer_bbox = get_pdf_coordinates_from_image_coordinates(image_bbox)

    words_json_path = r"_words.json"
    # words_json_path = input("words_json_path: ")
    with open(words_json_path, "r", encoding="utf-8") as f:
        words_json = json.loads(f.read())

    # do we need to do a conversion because of the origin difference? maybe not, because the words_json are in image terms only 
    inside_json = get_inside_json(outer_bbox, words_json)
    outside_json = get_outside_json(outer_bbox, words_json)
    with open("outside_bbox.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(outside_json, indent=4))
    with open("inside_bbox.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(inside_json, indent=4))
