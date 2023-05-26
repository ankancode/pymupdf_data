# https://snyk.io/advisor/python/ghostscript/example

import os
import subprocess


def convert_pdf_to_image(file_path, output_folder, resolution=96, image_extension="jpg"):
    if image_extension == "jpeg":
        device = "jpeg"
    elif image_extension == "png":
        device = "png16m"
    else:
        device = "png16m"
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    file_result_folder = os.path.join(output_folder, filename_wo_ext)
    os.makedirs(file_result_folder, exist_ok=True)
    results = subprocess.run(["gswin64c.exe", "-dNOPAUSE", f"-sDEVICE={device}", f"-r{str(resolution)}", f"-sOutputFile={file_result_folder}/{filename_wo_ext}_%03d.{image_extension}", f"{file_path}", "-dBATCH"], stdout=subprocess.PIPE, shell=True)
    print(results.stdout.decode("utf-8"))


if __name__ == "__main__":
    file_path = input("file_path: ")
    output_folder = input("output_folder: ")
    os.makedirs(output_folder, exist_ok=True)
    convert_pdf_to_image(file_path, output_folder)
