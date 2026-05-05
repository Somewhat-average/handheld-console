Requirements:

* Python 3.13 (recommended for compatibility)
* pip (Python package manager)

Setup Instructions:

1. Open a terminal or command prompt in the project folder.

2. Create a virtual environment using Python 3.13:
   Windows:
   py -3.13 -m venv venv
   venv\Scripts\activate

   Mac/Linux:
   python3.13 -m venv venv
   source venv/bin/activate

3. Install required packages:
   pip install -r requirements.txt

Running the Program:
Go to the virtual environment: venv\Scripts\activate
Run the main file using: python source_code/main.py

Controls:

* Arrow keys: Navigate menu
* A: Select option
* S: Return to previous menu
* D: Pause while playing Tetris

Project Structure:

* source_code: Contains all Python source files
* assets: Contains images, audio, and fonts
* documentation: Contains reports and design documents (currently empty)
* test_results: Contains testing and performance notes (currently empty)

Notes:

* Python 3.13 is required because newer versions (e.g., Python 3.14) may fail to install pygame
* Do not change folder names, as file paths are used in the code
* Ensure all dependencies are installed before running the program