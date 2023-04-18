"""Solve the daily Wordle"""
import random
from nltk.corpus import brown
import requests
import nltk
from config import MODULE_SUBDIR, WORDLE_API_KEY, TIME

from discord.ext import commands


def todays_wordle():
    """Send GET request to get the Wordle of the day"""
    url = "https://wordle-answers-solutions.p.rapidapi.com/answers"
    headers = {
        "X-RapidAPI-Key": WORDLE_API_KEY,
        "X-RapidAPI-Host": "wordle-answers-solutions.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    return response.json().get('data')[0]

def download_wordlist():
    """Download some NLTK things that could be used """
    nltk.download('words')
    nltk.download('brown')
    return nltk.corpus.words.words()

def sort_plurals(word):
    """Option within sort_textfile to have plural words looked at last"""
    if word[-1] == 's':
        return True     # Move to end of file
    return False        # Pass

def sort_repeats(word):
    with open('wordlists/wordles-so-far.txt', 'r', encoding="utf-8") as previous_wordles:
        if word in previous_wordles.read() and word[-1] != 's':
            return True     # Move to end of file
        return False        # Pass

def sort_textfile(subdir='wordlists/',
                  infile='valid-wordle-words.txt',
                  outfile='sorted-valid-wordle-words.txt',
                  filter_plurals=False,
                  filter_repeats=False):
    """Standalone function that sorts a textfile by most common words (Brown Corpus)"""
    # Open and read the original text file
    with open(subdir + infile, "r", encoding="utf-8") as my_infile:
        data_list = my_infile.read().split("\n")
    # Sort the file based on frequency in Brown Corpus
    frequency = nltk.FreqDist([w.lower() for w in brown.words()])
    wordlist_sorted = sorted(data_list, key=lambda x: frequency[x.lower()], reverse=True)

    if filter_repeats:
        # If word has been a Wordle already, move to end of the guess list
        wordlist_sorted = sorted(wordlist_sorted, key=sort_repeats)

    if filter_plurals:
        # If the word ends in a plural, move to the end of the guess list
        wordlist_sorted = sorted(wordlist_sorted, key=sort_plurals)

    # Write sorted list to new text file
    with open(subdir + outfile, "w", encoding="utf-8") as my_outfile:
        for word in wordlist_sorted:
            my_outfile.write(word + "\n")

def sort_textfile(subdir='wordlists/',
                  infile='valid-wordle-words.txt',
                  outfile='sorted-valid-wordle-words.txt',
                  plurals=False):
    """Standalone function that sorts a textfile by most common words (Brown Corpus)"""
    # Open and read the original text file as data_list
    with open(subdir + infile, "r", encoding="utf-8") as my_infile:
        data_list = my_infile.read().split("\n")
    # Sort the file based on frequency in Brown Corpus
    frequency = nltk.FreqDist([w.lower() for w in brown.words()])
    wordlist_sorted = sorted(data_list, key=lambda x: frequency[x.lower()], reverse=True)
    if plurals:
        wordlist_sorted = sorted(wordlist_sorted, key=sort_plurals)
    # Write sorted list to new text file
    with open(subdir + outfile, "w", encoding="utf-8") as my_outfile:
        for word in wordlist_sorted:
            my_outfile.write(word + "\n")

def first_word():
    """Select the first word to play"""
    wordlist = ['adieu', 'media', 'crate', 'radio', 'least']
    return random.choice(wordlist)

def generate_five_letter(wordlist, green_letters, yellow_letters, discard_pile, guess_history):
    """Generate all 5 letter words. Might not all be Wordle-approved
       Remove words that don't match parameters determined by compare_words()
       """
    banlist = []
    five_letter_words = [word.lower() for word in wordlist if len(word) == 5]
    # Remove words from the list that don't match the correct letter placements
    # Does not remove words that aren't possible due to close/yellow letters
    for word in five_letter_words.copy():
        for j, letter in enumerate(word):
            # Remove word if it is not a valid Wordle word
            if word in banlist:
                five_letter_words.remove(word)
                break
            # Remove already guessed words from possible list
            if word in guess_history:
                five_letter_words.remove(word)
                break
            # Remove words with any discarded letters from list
            if letter in discard_pile:
                five_letter_words.remove(word)
                break
            # Remove words that have incorrect letters in previously solved positions
            if letter != green_letters[j] and green_letters[j] is not None:
                five_letter_words.remove(word)
                break
    for word in five_letter_words.copy():
        for i in yellow_letters:
            if i not in word:
                five_letter_words.remove(word)
                break
    # for word in five_letter_words:
    #     print('✔️  ', word)
    # print(f"Possible words remaining: {len(five_letter_words)}")
    return five_letter_words

def compare_words(todays_word, wordle_guess, close_history):
    """Compare a submitted word against the days Wordle"""
    emoji_output = ""
    result, wrong_letters, close_letters = [], [], []

    if wordle_guess == todays_word:
        result = [char for char in todays_word]
        emoji_output = "🟩🟩🟩🟩🟩"
        return result, [], [], todays_word, emoji_output

    for i in range(5):
        # If the letter in todays_word matches the guess, add to result list
        if todays_word[i] == wordle_guess[i]:
            result.append(todays_word[i])
            # Update yellow letter list when a match is found.
            # Note some inefficiency around words using a letter multiple times
            if todays_word[i] in close_history:
                close_history.remove(todays_word[i])
            emoji_output = emoji_output + "🟩"
        # If the letter is anywhere within the guess, add to the close
        elif wordle_guess[i] in todays_word:
            result.append(None)  # None gets added if there is no exact match to keep position
            close_letters.append(wordle_guess[i])
            emoji_output = emoji_output + "🟨"
        # If the letter is neither correct or misplaced, add to the discard pile
        else:
            result.append(None)
            wrong_letters.append(wordle_guess[i])
            emoji_output = emoji_output + "⬛"
    wrong_letters = [*set(wrong_letters)]           # Remove repeats from the discard pile
    return result, close_letters, wrong_letters, wordle_guess, emoji_output

def green_letter_check(word, green_letters):
    """Filter the wordlist through the known green letters"""
    for i in range(len(word)):
        # Compare positions of random word with matched letters to find viable words
        if word[i] is not green_letters[i] and green_letters[i] is not None:
            return False
    return True

def yellow_letter_check(word, green_letters, yellow_letters):
    """Filter the wordlist through known yellow letters"""
    # Enumeration of unmatched letters
    open_spots = [i for i, x in enumerate(green_letters) if x is None]
    # List of each letter in the word being tested
    current_word = [char for char in word]

    if any(current_word[i] in yellow_letters for i in open_spots):
        return True
    return False

def next_word(wordlist, green_letters, yellow_letters,
              discard_pile, guess_history, method):
    """Choose the next best word from remaining wordlist"""
    next_guess = None
    wordlist_sorted = []
    generated_wordlist = generate_five_letter(wordlist, green_letters, yellow_letters,
                                              discard_pile, guess_history)
    for word in generated_wordlist:
        # Compare current matched letters to generated list of five letter words
        if green_letter_check(word, green_letters):
            if yellow_letter_check(word, green_letters, yellow_letters):
                next_guess = word
            else:
                if next_guess is None:
                    next_guess = word
        wordlist_sorted.append(next_guess)

    if method == 'brown':
        frequency = nltk.FreqDist([w.lower() for w in brown.words()])
        wordlist_sorted = sorted(wordlist_sorted, key=lambda x: frequency[x.lower()], reverse=True)
    return wordlist_sorted[0], generated_wordlist

def play_wordle(
        starting_word=first_word(),
        custom_list=False,
        wordle=todays_wordle()['answer'],
        method='quick',
        print_output=False):
    """Solve the daily Wordle"""

    discard_pile, guess_history, close_history = [], [], []

    if custom_list:
        with open(custom_list, "r", encoding="utf-8") as my_infile:
            wordlist = my_infile.read().split("\n")
    else:
        wordlist = download_wordlist()

    todays_word = wordle.lower()
    wordle_num = todays_wordle()['num']
    guess = starting_word.lower()
    emoji_block = ""

    # Since starting and goal word can be custom, they need to be validated
    if guess not in wordlist or todays_word not in wordlist:
        return print('Error: Invalid word choice')

    if print_output:
        print(f"{'='*40}\n\nOpening guess: {guess}\n")

    for i in range(20):
        # Compare the guess word with the wordle of the day
        (result, close_letters, wrong_letters,
         wordle_guess, emoji_output) = compare_words(todays_word, guess, close_history)
        discard_pile.extend(wrong_letters)      # List of letters that are not in the Wordle
        close_history.extend(close_letters)     # List of letters in the Wordle out of order
        guess_history.append(wordle_guess)      # List of guess attempt at the Wordle

        close_history = [*set(close_history)]   # Remove dupllicates from close_history

        emoji_block = f"{emoji_block}\n{emoji_output}"

        if result == [char for char in todays_word]:
            if print_output:
                print(f"{'='*40}\n\nWORDLE {wordle_num} {i+1}/6* "
                      f"{guess_history[-1].upper()}{emoji_block}\n"
                      f"Path: {' > '.join(guess_history)}\n")
            break

        # Update the guess word based on previous results and remamining words
        guess, wordlist = next_word(wordlist, result, close_history,
                                    discard_pile, guess_history, method)
        if print_output:
            print(f"{'='*40}\n"
                f"Next guess:     {guess}\n"
                f"Current board:  {result}\n"
                f"Yellow letters: {close_history}\n"
                f"Discard pile:   {discard_pile}\n"
                f"Guess history:  {guess_history}\n"
                f"{emoji_block}\n")

    wordle_dictionary = {
        "wordle": wordle,
        "wordle_num": wordle_num,
        "emoji_block": emoji_block,
        "guess_history": guess_history,
        "guess_count": i+1,
        "guess_path": " > ".join(guess_history),
        "discard_pile": discard_pile
    }
    return wordle_dictionary


class WordleLoser(commands.Cog):
    """Wordle themed content"""

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def wordle(self, context):
        """More directly Wordle themed content"""
        message = context.message.content.split(" ", 1)[1].lower()
        if message == "path":
            wrdl = play_wordle(custom_list='data/wordlists/sorted-valid-wordle-words.txt',
                               print_output=False)
            self.bot.reload_extension(f'{MODULE_SUBDIR}.wordle')
            print(f'{TIME}: Reloaded Wordle module (wordle command)')
            return await context.send(f"Here's how I got **Wordle {int(wrdl['wordle_num'])+3}**:\n"
                                      f"||{wrdl['guess_path']}||")
        else:
            return await context.send("Try `.wordle path`")

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(WordleLoser(bot))