""" HANGMAN GAME FOR DATHEON INTERNSHIP TASKS """

import random
import os

# ASCII stages for the gallows (0 to 6 incorrect attempts)
GALLOWS_STAGES = [
    """
       ------
       |    |
            |
            |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
            |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
       |    |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|    |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|\\   |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|\\   |
      /     |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|\\   |
      / \\   |
            |
    =========
    """
]

def load_words(filename="words.txt"):
    """
    Read and validate words from the external .txt file.
    Ensures path is relative to the script location and filters for pure English A-Z words.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The required word list file '{filename}' was not found in: {script_dir}")
        
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            words = []
            for line in file:
                word = line.strip().upper()
                if word.isascii() and word.isalpha():
                    words.append(word)
            
        if not words:
            raise ValueError(f"The file '{filename}' is empty or contains no valid English alphabetic words.")
            
        return words
    except OSError as e:
        raise RuntimeError(f"An error occurred while accessing '{filename}': {e}")

def display_gallows(incorrect_count):
    """Display the appropriate ASCII gallows stage."""
    print(GALLOWS_STAGES[incorrect_count])

def display_word(secret_word, guessed_set):
    """Show correctly guessed letters and underscores for unguessed ones."""
    displayed = []
    for letter in secret_word:
        if letter in guessed_set:
            displayed.append(letter)
        else:
            displayed.append("_")
    return " ".join(displayed)

def play_game(word_list):
    """Manage the core gameplay loop."""
    secret_word = random.choice(word_list)
    guessed_letters = set()
    incorrect_guesses = 0
    max_attempts = 6

    print("\n" + "=" * 45)
    print("      WELCOME TO TERMINAL HANGMAN (DATHEON)     ")
    print("=" * 45)

    while incorrect_guesses < max_attempts:
        display_gallows(incorrect_guesses)
        
        # Display game status
        current_masked_word = display_word(secret_word, guessed_letters)
        print(f"\nWord: {current_masked_word}")
        
        # Format and display guessed letters tracker
        sorted_guesses = sorted(guessed_letters)
        print(f"Guessed Letters: {', '.join(sorted_guesses) if sorted_guesses else 'None'}")
        print(f"Remaining Attempts: {max_attempts - incorrect_guesses}")
        
        # Check for victory condition
        if set(secret_word).issubset(guessed_letters):
            print("\n" + "=" * 45)
            print(f"🎉 VICTORY! You successfully guessed the word: {secret_word}")
            print("=" * 45)
            return True

        # Input validation loop (Strict single English letter A-Z check)
        while True:
            guess = input("\nGuess a single letter: ").strip().upper()
            
            if len(guess) != 1 or not guess.isascii() or not guess.isalpha():
                print("❌ Invalid input. Please enter a single English alphabetic letter (A-Z).")
                continue
            
            if guess in guessed_letters:
                print(f"⚠️ You already guessed '{guess}'. No penalty applied. Try a different letter.")
                print(f"Word: {current_masked_word}")
                continue
                
            break

        # Process the valid new guess
        guessed_letters.add(guess)

        if guess in secret_word:
            print(f"✅ Great job! '{guess}' is in the word.")
        else:
            incorrect_guesses += 1
            print(f"❌ Incorrect! '{guess}' is not in the word.")

    # Defeat screen
    display_gallows(incorrect_guesses)
    print("\n" + "=" * 45)
    print("💀 DEFEAT! You ran out of attempts")
    print(f"The secret word was: {secret_word}")
    print("=" * 45)
    return False

def main():
    """Start the application, handle initialization errors, and manage replay with validation."""
    try:
        word_list = load_words("words.txt")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\n[Initialization Error]: {e}")
        print("Please verify that your 'words.txt' file is present and properly formatted.")
        return
    
    while True:
        play_game(word_list)
        
        # Strict replay validation loop
        while True:
            replay = input("\nWould you like to play another round? (y/n): ").strip().lower()
            if replay in ('y', 'n'):
                break
            print("❌ Invalid input. Please enter 'y' for yes or 'n' for no.")
            
        if replay != 'y':
            print("\nThanks for playing! Good luck with your Datheon internship tasks! 🚀")
            break

if __name__ == "__main__":
    main()