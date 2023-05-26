from process_pdf_pdfminer_to_table_transformer import create_words_json
from ghostscript_pdf_to_image import convert_pdf_to_image


if __name__ == "__main__":
    file_path = input("file_path: ")
    images_output_folder = input("images_output_folder: ")
    words_json_output_folder = input("words_json_output_folder: ")
    convert_pdf_to_image(file_path, images_output_folder, resolution=96, image_extension="jpg")
    create_words_json(file_path, words_json_output_folder)
