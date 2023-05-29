import json
import os
import subprocess
from process_pdf_pdfminer_to_table_transformer import create_words_json
from ghostscript_pdf_to_image import convert_pdf_to_image
from get_text_between_bbox import get_pdf_coordinates_from_image_coordinates, get_inside_json, get_outside_json
from create_pdf_from_ocr_json import convert_json_to_pdf


def run_table_detection(image_dir, words_dir, out_dir):
    python_path = r"D:\Envs\table_transformer_env\Scripts\python.exe"
    script_home = r"src"
    script_path = r"src\inference.py"
    script_name = r"inference.py"
    detection_config_path = r"detection_config.json"
    detection_model_path = r"../pubtables1m_detection_detr_r18.pth"
    detection_device = "cpu"
    crop_padding = 10
    options = "-l -o -p -z -m -c"
    # results = subprocess.run([f"{python_path}", f"{script_path}", "--mode detect", f"--detection_config_path {detection_config_path}", f"--detection_model_path {detection_model_path}", f"--detection_device {detection_device}", f"--image_dir {image_dir}", f"--out_dir {out_dir}", f"--words_dir {words_dir}", f"--crop_padding {crop_padding}"], stdout=subprocess.PIPE, shell=True, cwd=script_home)
    # print(results.stdout.decode("utf-8"))
    print(f"\"{python_path}\" {script_name} --mode detect --detection_config_path \"{detection_config_path}\" --detection_model_path \"{detection_model_path}\" --detection_device \"{detection_device}\" --image_dir \"{image_dir}\" --out_dir \"{out_dir}\" --words_dir \"{words_dir}\" --crop_padding {crop_padding} {options}")


def run_pipeline(file_path, images_output_folder, words_json_output_folder, bboxes_json_output_folder, inside_json_output_folder, outside_json_output_folder, inside_pdf_output_folder, outside_pdf_output_folder):
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)

    images_home = os.path.join(images_output_folder, filename_wo_ext)
    words_json_home = os.path.join(words_json_output_folder, filename_wo_ext)
    bboxes_json_home = os.path.join(bboxes_json_output_folder, filename_wo_ext)
    inside_json_home = os.path.join(inside_json_output_folder, filename_wo_ext)
    outside_json_home = os.path.join(outside_json_output_folder, filename_wo_ext)
    inside_pdf_home = os.path.join(inside_pdf_output_folder, filename_wo_ext)
    outside_pdf_home = os.path.join(outside_pdf_output_folder, filename_wo_ext)
    os.makedirs(bboxes_json_home, exist_ok=True)
    os.makedirs(inside_json_home, exist_ok=True)
    os.makedirs(outside_json_home, exist_ok=True)
    os.makedirs(inside_pdf_home, exist_ok=True)
    os.makedirs(outside_pdf_home, exist_ok=True)

    pdf_dpi = 72
    image_dpi = 96
    fill_char = "0"

    convert_pdf_to_image(file_path, images_output_folder, resolution=image_dpi, image_extension="jpg")
    pages = create_words_json(file_path, words_json_output_folder)
    run_table_detection(images_home, words_json_home, bboxes_json_home)
    # exit()
    import time
    time.sleep(60)


    for page_no in range(1, pages+1):
        z_filled_page_no = "{:{fill_char}3}".format(page_no, fill_char=fill_char)
        words_json_filename = f"{filename_wo_ext}_{z_filled_page_no}_words.json"
        words_json_path = os.path.join(words_json_home, words_json_filename)
        
        bboxes_json_filename = f"{filename_wo_ext}_{z_filled_page_no}_objects.json"
        bboxes_json_path = os.path.join(bboxes_json_home, bboxes_json_filename)

        with open(bboxes_json_path, "r", encoding="utf-8") as f:
            bboxes_json = json.loads(f.read())

        with open(words_json_path, "r", encoding="utf-8") as f:
            words_json = json.loads(f.read())

        for table_no in range(len(bboxes_json)):
            z_filled_table_no = "{:{fill_char}3}".format(table_no, fill_char=fill_char)
            # image_bbox are with origin at top left corner
            image_bbox = bboxes_json[table_no]["bbox"]
            score = bboxes_json[table_no]["score"]
            if score < 0.95:
                print(z_filled_page_no, z_filled_table_no, score)
                continue


            # the outer_bbox coordinates have origin at top left corner, and are for pdf units (72 dpi)
            outer_bbox = get_pdf_coordinates_from_image_coordinates(image_bbox, image_dpi)

            # do we need to do a conversion because of the origin difference? maybe not, because the words_json are in image terms only 
            inside_json = get_inside_json(outer_bbox, words_json)
            outside_json = get_outside_json(outer_bbox, words_json)

            inside_json_filename = f"{filename_wo_ext}_{z_filled_page_no}_inside_bbox_{z_filled_table_no}"
            outside_json_filename = f"{filename_wo_ext}_{z_filled_page_no}_outside_bbox_{z_filled_table_no}"

            inside_json_path = os.path.join(inside_json_home, f"{inside_json_filename}.json")
            outside_json_path = os.path.join(outside_json_home, f"{outside_json_filename}.json")

            with open(inside_json_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(inside_json, indent=4))
            with open(outside_json_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(outside_json, indent=4))

            inside_pdf_path = os.path.join(inside_pdf_home, f"{inside_json_filename}.pdf")
            outside_pdf_path = os.path.join(outside_pdf_home, f"{outside_json_filename}.pdf")
            # convert_json_to_pdf(inside_json, inside_pdf_path)
            # convert_json_to_pdf(outside_json, outside_pdf_path)


if __name__ == "__main__":
    file_path = input("file_path: ")
    images_output_folder = get_folder_path_input("images_output_folder")
    words_json_output_folder = get_folder_path_input("words_json_output_folder")
    bboxes_json_output_folder = get_folder_path_input("bboxes_json_output_folder")
    inside_json_output_folder = get_folder_path_input("inside_json_output_folder")
    outside_json_output_folder = get_folder_path_input("outside_json_output_folder")
    inside_pdf_output_folder = get_folder_path_input("inside_pdf_output_folder")
    outside_pdf_output_folder = get_folder_path_input("outside_pdf_output_folder")

    run_pipeline(file_path, images_output_folder, words_json_output_folder, bboxes_json_output_folder, inside_json_output_folder, outside_json_output_folder, inside_pdf_output_folder, outside_pdf_output_folder)
