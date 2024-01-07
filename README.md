# Python-CSPDF
Python Check Similarity PDF from active directory and store to csv file inspired by [diff-pdf](https://github.com/luke-cha/diff-pdf)

### Installation
```sh
pip install -r requirements.py
```

### Usage
1. Check similarity all pdf files on current active directory.
   ```sh
   python cspdf.py -a -o comparison.csv
   ```
2. Check similarity one pdf file with all pdf files on current active directory.
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
