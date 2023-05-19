from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json
import os


def convert_json_to_pdf(json_data, output_file):
    # Create a new PDF document
    c = canvas.Canvas(output_file, pagesize=A4)

    # Set the font for drawing text
    font_name = "Helvetica"  # Update with the desired font name
    font_size = 12  # Update with the desired font size
    c.setFont(font_name, font_size)

    # Iterate over the words in the JSON data
    for word in json_data:
        text = word["text"]
        # if text == "\n":
        #     continue
        bbox = word["bbox"]
        font = word["font"]
        font_name, font_size = font.split(" ")
        font_name = font_name.split("+")[-1]
        font_size = int(font_size.rstrip("pt"))

        # Convert the coordinates from image space to PDF space
        x1, y1, x2, y2 = bbox
        y1 = c._pagesize[1] - y1
        y2 = c._pagesize[1] - y2

        # Set the font for the word
        fallback_font = "Helvetica"  # Specify a fallback font name

        try:
            c.setFont(font_name, font_size)  # Try to set the specified font
        except Exception as e:
            print(f"Error setting font: {e}")
            print(f"Font '{font_name}' is not available. Using fallback font '{fallback_font}' instead.")
            c.setFont(fallback_font, font_size)  # Set the fallback font
        # c.setFont(font_name, font_size)

        # Draw the word on the PDF canvas
        c.drawString(x1, y1, text)

    # Save the PDF document
    c.save()


if __name__ == "__main__":
    page_wise_words_json_path = input("Enter page_wise_words_json_path: ")
    with open(page_wise_words_json_path, "r", encoding="utf-8") as f:
        page_wise_words = json.loads(f.read())
    filename = os.path.basename(page_wise_words_json_path)
    folder_path = os.path.dirname(page_wise_words_json_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    output_folder_path = os.path.join(folder_path, filename_wo_ext)
    os.makedirs(output_folder_path, exist_ok=True)
    for page_no in page_wise_words:
        current_page_data = page_wise_words[page_no]
        page_pdf_path = os.path.join(output_folder_path, f"{filename_wo_ext}_{str(page_no).zfill(3)}.pdf")
        convert_json_to_pdf(current_page_data, output_file=page_pdf_path)
    # Example JSON data
    # json_data = [
    #     {
    #         "text": "Hello",
    #         "bbox": [100, 100, 200, 120],
    #         "font": {
    #             "name": "Helvetica",
    #             "size": 12
    #         }
    #     },
    #     {
    #         "text": "World",
    #         "bbox": [250, 150, 350, 170],
    #         "font": {
    #             "name": "Helvetica",
    #             "size": 18
    #         }
    #     }
    # ]

    # # Convert the JSON data to PDF
    # output_file = "output.pdf"
    # convert_json_to_pdf(json_data, output_file)
