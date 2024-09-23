import os
import difflib
import csv
from io import StringIO
import sys
import argparse
from tqdm import tqdm
import fitz
import cv2
import numpy as np
from skimage import metrics

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

def cv2_pdf_images(filepath):
    pdf_file = fitz.open(filepath)
    cv_imgs = []

    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)
        image_list = page.get_images(full=True)

        for img in image_list:
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_array = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            cv_imgs.append(image)

    return cv_imgs

def compare_ssim(image1, image2):
    # Resize image2 to match image1's dimensions
    image2_resized = cv2.resize(image2, (image1.shape[1], image1.shape[0]), interpolation=cv2.INTER_AREA)
    
    # Convert both images to grayscale
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2_resized, cv2.COLOR_BGR2GRAY)

    # Calculate SSIM between the two grayscale images
    ssim_score, _ = metrics.structural_similarity(image1_gray, image2_gray, full=True)

    return round(ssim_score, 2)

def calculate_images_similarity(images1, images2):
    scores = []
    for img in images1:
        sim_scores = []
        
        for img2 in images2:
            sim_scores.append(compare_ssim(img, img2))

        max_score = max(sim_scores)
        scores.append(max_score)

    avg = sum(scores) / len(scores) * 100
    return round(avg, 2)

def convert_pdf_to_text(pdf_path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    with open(pdf_path, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, check_extractable=True):
            interpreter.process_page(page)
    text = retstr.getvalue()
    retstr.close()
    return text

def calculate_text_similarity(text1, text2):
    seq_matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity_ratio = seq_matcher.ratio()
    similarity_percentage = round(similarity_ratio * 100, 2)
    return similarity_percentage

def compare_with_all_pdfs(
        target_pdf, 
        output_csv,
        compare_image=False
    ):
    current_directory = os.getcwd()
    pdf_files = [file for file in os.listdir(current_directory) if file.lower().endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    target_text = convert_pdf_to_text(target_pdf)

    if (compare_image):
        target_imgs = cv2_pdf_images(target_pdf)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        if (compare_image):
            csv_writer.writerow(['Source PDF', 'Compared PDF', 'Text Similarity Percentage', 'Image Similarity Percentage'])
        else:
            csv_writer.writerow(['Source PDF', 'Compared PDF', 'Text Similarity Percentage'])

        pbar = tqdm(total=len(pdf_files) - 1, desc="Comparing PDFs", unit="pair")

        for pdf_file in pdf_files:
            if pdf_file != target_pdf:
                compare_text = convert_pdf_to_text(pdf_file)
                similarity_percentage = calculate_text_similarity(target_text, compare_text)

                if (compare_image):
                    compare_imgs = cv2_pdf_images(pdf_file)
                    img_similarity_percentage = calculate_images_similarity(target_imgs, compare_imgs)
                    csv_writer.writerow([target_pdf, pdf_file, similarity_percentage, img_similarity_percentage])
                else:
                    csv_writer.writerow([target_pdf, pdf_file, similarity_percentage])

                if not pbar is None:
                    pbar.update(1)
        if not pbar is None:
            pbar.close()

    print(f"\nComparison results exported to {output_csv}")

def compare_all_pdfs(
        pdf_files,
        output_csv,
        compare_image=False
    ):
    total_comparisons = len(pdf_files) * (len(pdf_files) - 1) // 2
    compared_pairs = set()

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        if (compare_image):
            csv_writer.writerow(['PDF 1', 'PDF 2', 'Text Similarity Percentage', 'Image Similarity Percentage'])
        else:
            csv_writer.writerow(['PDF 1', 'PDF 2', 'Text Similarity Percentage'])

        with tqdm(total=total_comparisons, desc="Comparing PDFs", unit="pair") as pbar:
            for i in range(len(pdf_files)):
                pdf1 = pdf_files[i]
                for j in range(i + 1, len(pdf_files)):
                    pdf2 = pdf_files[j]

                    # Check if the basenames are different
                    if os.path.basename(pdf1) != os.path.basename(pdf2):
                        pair_key = tuple(sorted([pdf1, pdf2]))

                        if pair_key not in compared_pairs:
                            text1 = convert_pdf_to_text(pdf1)
                            text2 = convert_pdf_to_text(pdf2)
                            similarity_percentage = calculate_text_similarity(text1, text2)

                            if (compare_image):
                                imgs1 = cv2_pdf_images(pdf1)
                                imgs2 = cv2_pdf_images(pdf2)
                                image_similarity_percentage = calculate_images_similarity(imgs1, imgs2)
                                csv_writer.writerow([pdf1, pdf2, similarity_percentage, image_similarity_percentage])
                            else:
                                csv_writer.writerow([pdf1, pdf2, similarity_percentage])
                            compared_pairs.add(pair_key)

                            pbar.update(1)

    print(f"\nComparison results exported to {output_csv}")

if __name__ == "__main__":
    description = "Compare and get the similarity percentage between all PDF files in the current directory."
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--all', action='store_true', help="compare all PDF files with each other")
    parser.add_argument('-i', '--image', action='store_true', help="comparing pdf including image similarity, slow process")
    parser.add_argument('-o', '--output', default="comparison_results.csv", type=str, help="output CSV file to store the comparison results")
    parser.add_argument('-t', '--target', default=None, type=str, help="target PDF file to compare with all other PDF files")

    args = parser.parse_args()

    if args.all:
        current_directory = os.getcwd()
        pdf_files = [file for file in os.listdir(current_directory) if file.lower().endswith('.pdf')]

        if not pdf_files:
            print("No PDF files found in the current directory.")
            sys.exit(1)

        if (args.image):
            compare_all_pdfs(pdf_files, args.output, compare_image=True)
        else:
            compare_all_pdfs(pdf_files, args.output)
    elif (not args.target is None):
        if (args.image):
            compare_with_all_pdfs(args.target, args.output, compare_image=True)
        else:
            compare_with_all_pdfs(args.target, args.output)
    else:
        print("Usage: python cspdf.py [-t <target_pdf>] [-o <output_csv>]")
        sys.exit(1)
        