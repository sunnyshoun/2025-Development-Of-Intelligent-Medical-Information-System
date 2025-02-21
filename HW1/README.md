# Chinese Text Segmentation Project

## Installation
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

2. Download the model:
   - Go to [this link](https://drive.google.com/drive/folders/105IKCb88evUyLKlLondvDBoh7Dy_I1tm) to download the model files.
   - Extract the downloaded files and rename the folder to `model`.
   - Place the `model` folder in the same directory as `main.py`.

3. Run the script:
   ```sh
   python main.py
   ```

## Output Files
The results will be saved in the `result` folder, containing the following files:

- `select_text.txt`: The original selected text from the JSON file.
- `cc_convert.txt`: The text after converting Simplified Chinese to Traditional Chinese.
- `WS_result.txt`: The final segmented result using CKIPtagger.

## Dependencies
- Python 3.10.X
- CKIPtagger
- OpenCC (for Simplified-Traditional Chinese conversion)

## Notes
Ensure that the CKIPtagger model files are placed in the correct directory (e.g., `./model`).

## References
- CKIPtagger: [GitHub Repository](https://github.com/ckiplab/ckiptagger?tab=readme-ov-file)
