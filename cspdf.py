import os
import difflib
import csv
from io import StringIO
import sys
import argparse
from tqdm import tqdm

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

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

def calculate_similarity(text1, text2):
    seq_matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity_ratio = seq_matcher.ratio()
    similarity_percentage = round(similarity_ratio * 100, 2)
    return similarity_percentage

def compare_with_all_pdfs(target_pdf, output_csv, verbose=False):
    current_directory = os.getcwd()
    pdf_files = [file for file in os.listdir(current_directory) if file.lower().endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    target_text = convert_pdf_to_text(target_pdf)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Compared PDF', 'Similar PDF', 'Similarity Percentage'])
        pbar = None

        if not verbose:
            pbar = tqdm(total=len(pdf_files) - 1, desc="Comparing PDFs", unit="pair")

        for pdf_file in pdf_files:
            if pdf_file != target_pdf:
                compare_text = convert_pdf_to_text(pdf_file)
                similarity_percentage = calculate_similarity(target_text, compare_text)
                csv_writer.writerow([target_pdf, pdf_file, similarity_percentage])
                if not verbose and not pbar is None:
                    pbar.update(1)
        if not pbar is None:
            pbar.close()

    if verbose:
        print("Comparison Results:")
        print('{:<30} {:<30} {:<20}'.format('Compared PDF', 'Similar PDF', 'Similarity Percentage'))
        print('-' * 80)

        for pdf_file in pdf_files:
            if pdf_file != target_pdf:
                compare_text = convert_pdf_to_text(pdf_file)
                similarity_percentage = calculate_similarity(target_text, compare_text)
                print(f'{target_pdf:<30} {pdf_file:<30} {similarity_percentage:<20}')

    print(f"Comparison results exported to {output_csv}")

def compare_all_pdfs(pdf_files, output_csv):
    total_comparisons = len(pdf_files) * (len(pdf_files) - 1) // 2
    compared_pairs = set()

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Compared PDF 1', 'Compared PDF 2', 'Similarity Percentage'])

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

                            similarity_percentage = calculate_similarity(text1, text2)

                            csv_writer.writerow([pdf1, pdf2, similarity_percentage])
                            compared_pairs.add(pair_key)

                            pbar.update(1)

    print(f"\nComparison results exported to {output_csv}")

if __name__ == "__main__":
    description = "Compare and get the similarity percentage between all PDF files in the current directory."
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--all', action='store_true', help="compare all PDF files with each other.")
    parser.add_argument('-o', '--output', default="comparison_results.csv", type=str, help="output CSV file to store the comparison results.")
    parser.add_argument('-t', '--target', default=None, type=str, help="target PDF file to compare with all other PDF files.")
    parser.add_argument('-v', '--verbose', action='store_true', help="print the comparison results to the console.")

    args = parser.parse_args()

    if args.all:
        current_directory = os.getcwd()
        pdf_files = [file for file in os.listdir(current_directory) if file.lower().endswith('.pdf')]

        if not pdf_files:
            print("No PDF files found in the current directory.")
            sys.exit(1)

        compare_all_pdfs(pdf_files, args.output)
    elif (not args.target is None):
        compare_with_all_pdfs(args.target, args.output, args.verbose)
    else:
        print("Usage: python cspdf.py [-t <target_pdf>] [-o <output_csv>]")
        sys.exit(1)
        