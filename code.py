# install PyMuPDF

# import libraries

import fitz

import io

from PIL import Image

 

# STEP 2

# file path you want to extract images from

# File download url: https://www.citigroup.com/citi/about/esg/download/2021/Global-ESG-Report-2021.pdf?ieNocache=248

file = "Global-ESG-Report-2021.pdf"

 

# open the file

pdf_file = fitz.open(file)

 

# STEP 3

# iterate over PDF pages

for page_index in range(len(pdf_file)):

 

  # get the page itself

  page = pdf_file[page_index]

  image_list = page.get_images()
#   texts = page.get_text("dict")["blocks"]
  texts = page.get_text().encode("utf-8")
  print(texts[0])
#   import json
  with open(f"texts/page_text_{str(page_index)}.txt", "wb") as f:
      f.write(texts)
      f.write(bytes((12,)))
 

  # printing number of images found in this page

  if image_list:

    print(f"[+] Found a total of {len(image_list)} images in page {page_index}")

  else:

    print("[!] No images found on page", page_index)

  for image_index, img in enumerate(page.get_images(), start=1):

   

    # get the XREF of the image

    xref = img[0]

   

    # extract the image bytes

    base_image = pdf_file.extract_image(xref)

    image_bytes = base_image["image"]

   

    # get the image extension

    image_ext = base_image["ext"]

 

    # load it to PIL

    image = Image.open(io.BytesIO(image_bytes))

   

    # save it to local disk

    image.save(open(f"image{page_index+1}_{image_index}.{image_ext}", "wb"))