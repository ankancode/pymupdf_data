import fitz
import os
from PIL import Image
import io


def extract_image_info(file_path, images_output_folder):
    extracted_image_json = {}
    filename = os.path.basename(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    # page_wise_data, all_outputs = extract_image_info(file_path)
    # file_output_folder = os.path.join(images_output_folder, filename_wo_ext)
    # os.makedirs(file_output_folder, exist_ok=True)

    pdf_file = fitz.open(file_path)
    image_id = 0
    for page_index in range(1, len(pdf_file)+1):
        page_images_paths = []
        page = pdf_file[page_index-1]
        # full_page_path_dest = os.path.join(file_output_folder, str(page_index))
        image_list = page.get_images()

        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            print(f"[!] No images found on page {page_index}")
        
        for image_index, img in enumerate(page.get_images(), start=1):
            image_rects = page.get_image_rects(img)
            # dealing with an exception where img is found but image_rects is empty
            if len(image_rects) == 0:
                print(f"skipping {page_index}")
                continue
            xref = img[0]
            
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]

            image_ext = "png"
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # only making folder for those pages which have at least one image inside them
            # os.makedirs(full_page_path_dest, exist_ok=True)
            image_id += 1
            image_save_path = os.path.join(images_output_folder, f"{filename_wo_ext}_{image_id}.{image_ext}")
            image.save(open(image_save_path, "wb"))
            page_images_paths.append({"image_id": image_id, "image_path": image_save_path, "bbox": list(image_rects[0])})
        extracted_image_json[page_index] = page_images_paths
    return extracted_image_json


if __name__ == "__main__":
    file_path = input("file_path: ")
    images_output_folder = input("images_output_folder: ")
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    import json
    os.makedirs(images_output_folder, exist_ok=True)
    extracted_image_json = extract_image_info(file_path, images_output_folder)
    with open(f"{filename_wo_ext}_extracted_images.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(extracted_image_json))

