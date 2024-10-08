import os
from pdf2image import convert_from_path
from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError
import io
import re
import unicodedata 
from docx2pdf import convert

def convert_docx_to_pdf(docx_path):
    pdf_path = os.path.splitext(docx_path)[0] + '.pdf'
    print(pdf_path)
    convert(docx_path, pdf_path)
    return pdf_path

def process_pdf(pdf_path, bucket_name):
    # Convert PDF to images
    images = convert_from_path(pdf_path, first_page=1, last_page=6)

    # Ensure we don't process more than 6 pages
    images = images[:6]

    s3 = boto3.client('s3')
    links_list = []
    pdf_base_name = os.path.basename(pdf_path)
    file_entry = {'File': pdf_base_name, 'Links': []}
    links_list.append(file_entry)

    for i, image in enumerate(images):
        # Determine orientation
        width, height = image.size
        is_landscape = width > height

        # Resize for full image (maintaining aspect ratio)
        if is_landscape:
            image.thumbnail((1920, 1080))
            orientation = 'landscape'
        else:
            image.thumbnail((1080, 1920))
            orientation = 'portrait'

        page_orientation = orientation 

        # Prepare file name
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        print("PDF NAME:")
        print(pdf_name)
        print(type(pdf_name))

        # Normalize Unicode characters
        pdf_name_normalized = unicodedata.normalize('NFKD', pdf_name)
        print(type(pdf_name_normalized))

        # Remove any non-ASCII characters
        pdf_name_ascii = pdf_name_normalized.encode('ASCII', 'ignore').decode('ASCII')
        # pdf_name_cleaned = re.sub(r'[^\x20-\x7E]', ' ', pdf_name_ascii)
        pdf_name_full = pdf_name_ascii.replace(" ", "")
        # Replace any whitespace (including Unicode whitespace) with a single space and strip
        # pdf_name_full = re.sub(r'\s+', ' ', pdf_name_cleaned)
        

        print("PDF NAME FIXED:")
        print(pdf_name_full)
        print(type(pdf_name_full))

        full_image_key = f"{pdf_name_full}/page_{i+1}.png"

        # Upload full image
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        s3.put_object(Bucket=bucket_name, Key=full_image_key, Body=img_byte_arr, ContentType='image/png')

        # Get public URL
        full_url = f"https://{bucket_name}.s3.us-west-2.amazonaws.com/{full_image_key}"
        file_entry['Links'].append(full_url)
        file_entry['Links'].append(page_orientation)

        #'ImageLink': full_url})
        # links_list.append(full_url)
    print(links_list)
    return links_list

def process_pdf_folder(folder_path, bucket_name):
    all_results = []

    # First, convert all DOCX files to PDF
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.docx'):
            docx_path = os.path.join(folder_path, filename)
            try:
                pdf_path = convert_docx_to_pdf(docx_path)
                print(f"Converted {filename} to PDF")
            except Exception as e:
                print(f"Error converting {filename} to PDF: {str(e)}")
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            try:
                urls = process_pdf(pdf_path, bucket_name)
                all_results.extend(urls)  # Use extend instead of creating a new dictionary
                print(f"Processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    return all_results

