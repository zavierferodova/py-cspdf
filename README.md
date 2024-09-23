# Python-CSPDF
Python Check Similarity PDF from active directory and store it to csv file. Project inspired by [diff-pdf](https://github.com/luke-cha/diff-pdf)

### Installation
```sh
pip install -r requirements.py
```

### Before Use !!
1. Install all required depedencies.
2. Copy `cspdf.py` into directory that contains pdf file to be compared.
3. Run `cspdf.py` script.
4. Note: This script just work on pdf files only, if you have word document please convert it into pdf first.

### Usage
1. Check similarity all pdf files on current active directory
   ```sh
   python cspdf.py -a -o comparison.csv
   ```
2. Check similarity one pdf file then compare with all pdf files on current active directory
   ```sh
   python cspdf.py -t a.pdf -o comparison.csv
   ```
3. Check similarity including image comparison (slow processing)
   ```sh
   # Just add -i or --image argument
   python cspdf.py -i -t a.pdf -o comparison.csv
   ```
5. Get help
   ```sh
   python cspdf.py -h
   ```

### Similarity Check Methods 
1. Text similarity with Sequence Matcher
2. Image similarity with Structural Similarity Index (SSIM)

### Libraries
1. [PDFMiner](https://pypi.org/project/pdfminer/)
2. [PyMuPDF](https://pymupdf.readthedocs.io/)
3. [OpenCV Python](https://opencv.org/get-started/)
4. [Scikit Image](https://scikit-image.org)
5. [TQDM Progress Bar](https://tqdm.github.io)

### Credits
Made by Zavier, enjoyy ✨
