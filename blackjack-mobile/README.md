# Blackjack Mobile Game

## Overview
This project is a mobile version of the classic Blackjack game implemented in Python. It features a simple user interface and game logic that allows players to enjoy the game on their mobile devices.

## Project Structure
```
blackjack-mobile
├── src
│   ├── main.py          # Entry point of the application
│   ├── game
│   │   ├── __init__.py  # Marks the game directory as a package
│   │   ├── blackjack.py  # Contains the Blackjack game logic
│   │   └── utils.py      # Utility functions for the game
│   ├── ui
│   │   ├── __init__.py   # Marks the ui directory as a package
│   │   └── screens.py     # User interface management
│   └── assets
│       └── cards         # Directory for card images
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd blackjack-mobile
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Game
To start the game, run the following command:
```
python src/main.py
```

## Gameplay
- The game follows standard Blackjack rules.
- Players can hit, stand, or double down.
- The goal is to get as close to 21 without going over.

## Contributing
Feel free to submit issues or pull requests for improvements or bug fixes. 

## License
This project is licensed under the MIT License.