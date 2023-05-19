# https://snyk.io/advisor/python/ghostscript/example

import os
import subprocess

# input_dir = "input"
input_dir = input("input_dir: ")
# output_dir = "output"
output_dir = input("output_dir: ")
os.makedirs(output_dir, exist_ok=True)


resolution = 96
# device = "png16m"
# extension = "png"
device = "jpeg"
image_extension = "jpg"

files = os.listdir(input_dir)
for file in files:
    file_name_wo_extension, extension = os.path.splitext(os.path.basename(file))
    file_result_folder = os.path.join(output_dir, file_name_wo_extension)
    file_path = os.path.join(input_dir, file)
    os.makedirs(file_result_folder, exist_ok=True)
    results = subprocess.run(["gswin64c.exe", "-dNOPAUSE", f"-sDEVICE={device}", f"-r{str(resolution)}", f"-sOutputFile={file_result_folder}/{file_name_wo_extension}_%03d.{image_extension}", f"{file_path}", "-dBATCH"], stdout=subprocess.PIPE, shell=True)
    print(results.stdout.decode("utf-8"))