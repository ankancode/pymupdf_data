import json
import tabula


def convert_to_tabula_coordinates(bbox, image_dpi, margin=(0, 0, 0, 0), pdf_dpi=72):
    """
    Convert bounding box from image coordinates to PDF coordinates.

    Args:
        bbox (tuple): Bounding box coordinates in image coordinates (x1, y1, x2, y2).
        image_dpi (tuple): Image resolution in dots per inch (DPI).
        pdf_resolution (tuple): PDF resolution in dots per inch (DPI).

    Returns:
        tuple: Bounding box coordinates in the area format required by tabula (top, left, bottom, right).
    """
    pdf_dpi = 72
    # image_dpi = 72
    image_to_pdf_conversion_factor = pdf_dpi/image_dpi

    x1, y1, x2, y2 = bbox
    x1, y1, x2, y2 = x1 - margin[0], y1 - margin[1], x2 + margin[2], y2 + margin[3]

    # Convert image coordinates to PDF coordinates
    x1_pdf = x1 * image_to_pdf_conversion_factor
    y1_pdf = y1 * image_to_pdf_conversion_factor
    x2_pdf = x2 * image_to_pdf_conversion_factor
    y2_pdf = y2 * image_to_pdf_conversion_factor

    top = y1_pdf
    left = x1_pdf
    bottom = y2_pdf
    right = x2_pdf

    return (top, left, bottom, right)


def extract_tables_with_coordinates(file_path, coordinates, page_number=1, tabula_server_url="http://localhost:8080"):
    top, left, bottom, right = map(float, coordinates)
    java_options = "-Dfile.encoding=UTF8 -Dtabula.server={}".format(tabula_server_url)
    # Guess tables from a pdf
    # stream_tables = tabula.read_pdf(file_path, pages=page_number, stream=True, guess=True, java_options=java_options)
    # lattice_tables = tabula.read_pdf(file_path, pages=page_number, lattice=True, guess=True, java_options=java_options)
    # Extract table from the specified area
    stream_tables = tabula.read_pdf(file_path, pages=page_number, stream=True, area=(top, left, bottom, right), java_options=java_options)
    lattice_tables = tabula.read_pdf(file_path, pages=page_number, lattice=True, area=(top, left, bottom, right), java_options=java_options)
    return stream_tables, lattice_tables


if __name__ == "__main__":
    file_path = input("pdf_path: ")
    # image_bbox, image_dpi = (60, 140, 445, 390), 72
    # image_bbox, image_dpi = (80, 190, 590, 515), 96
    tables_detection_json_path = r""
    with open(tables_detection_json_path, "r", encoding="utf-8") as f:
        tables_detection_json = json.loads(f.read())
    image_bbox = tables_detection_json[0]["bbox"]
    image_dpi = 96
    tabula_bbox = convert_to_tabula_coordinates(image_bbox, image_dpi, margin=(10, 10, 10, 10))
    print(image_bbox)
    print(tabula_bbox)
    tabula_server_url = "http://localhost:8080"
    stream_tables, lattice_tables = extract_tables_with_coordinates(file_path, tabula_bbox, 18, tabula_server_url)
    print(stream_tables)
    print(lattice_tables)