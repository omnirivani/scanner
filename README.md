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

## Installation

1. **Clone or download this repository.**
   - If downloading the zip, be sure to unzip the folder before running.

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

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

## Troubleshooting

- If you see errors about missing modules, run `pip install -r requirements.txt` again.
- Sometimes a search query will not return a result, even though that card technically exists in TCGplayer. 
      - This is because TCGplayer may move product listings around randomly.
      - As this program checks a specified number of pages, the card of interest may be placed in a deeper page.
      - Rerunning the query can fix this issue.
- If you encounter any bugs or errors, please let me know so I can fix them. Contact: omnirivani@gmail.com

