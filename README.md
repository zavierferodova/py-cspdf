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
3. Get help
   ```sh
   python cspdf.py -h
   ```

### Libraries
1. [PDFMiner](https://pypi.org/project/pdfminer/)
2. [TQDM Progress Bar](https://tqdm.github.io)

### Credits
Made by Zavier, enjoyy ✨
