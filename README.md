# TCGPlayer Sales Data Scanner

This program allows you to search for Pokémon cards on TCGPlayer, select the correct product from search results, and view recent sales data for the selected card and condition. Card traders may find this tool useful at card shows.

## Features

- Search for cards by name, number, and condition (e.g., `sylveon vmax #075/203 nm`)
- Select from multiple matching products (with set and market price info)
- View recent sales data (price, date, quantity, condition)
- Outputs sales data in a readable table

## Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (matching your Chrome version)

## Installation

1. **Clone or download this repository.**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install ChromeDriver:**
   - Download ChromeDriver from [chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
   - Make sure the version matches your installed Chrome browser.
   - Place the `chromedriver` executable in your PATH (e.g., `/usr/local/bin`).

## Usage

1. **Run the program:**
   ```bash
   python scanner.py
   ```
   - You will be prompted for a card search in the format: "[card name] #[number] [condition]"
        - You can omit the condition to default to Near Mint (nm).
        - Example: Enter card search (or type 'exit' to quit): charizard ex #001/021 lp
        - This searches for the term "charizard ex", looks for the number "001/021", and in the condition "Lightly Played".
   - The browser will open and load TCGPlayer search results.
   - If multiple products match, you will be prompted in the terminal to select one. 
        - Click away from brower and into terminal, then type the selection.

2. **View Results:**
   - The five most recent sales data will be displayed in the terminal.

## Notes

- The browser window will open during execution. You may need to click back into your terminal to enter your selection.
- If you encounter issues with ChromeDriver, ensure it matches your Chrome version and is in your PATH.

## Troubleshooting

- If you see errors about missing modules, run `pip install -r requirements.txt` again.
- If the browser does not open, check your ChromeDriver installation.
- If you encounter any bugs or errors, please let me know so I can fix them. Contact: omnirivani@gmail.com

