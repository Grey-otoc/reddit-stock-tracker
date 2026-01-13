from pathlib import Path

"""
accesses blacklist files and adds each word to a list which can then be used for
ticker extraction filtering 
"""

def load_blacklist_files() -> set:
    current_dir = Path(__file__).resolve()
    blacklists_dir = current_dir.parent.parent / "blacklists"
    regular_words_file = blacklists_dir / "regular_words.txt"
    random_words_dc_file = blacklists_dir / "random_dc.txt"

    # if our blacklists dir, regular_words file, or random_dc file do not exist, 
    # the main logic of our program cannot function properly
    if not blacklists_dir.exists() or not regular_words_file.exists() or not random_words_dc_file.exists():
        raise FileNotFoundError("FATAL ERROR: Blacklists directory, regular words, or random do consider lists do not exist.")
    
    blacklisted_words = set()
    regular_words_list = set()
    # random_dc stands for "random do consider", these are acronyms or slang that
    # may also be tickers...since they are usually in lowercase, we consider them if
    # they appear in uppercase form
    random_words_dc = set()
    separate_files = ["random_dc.txt", "regular_words.txt"]
    
    for file in blacklists_dir.iterdir():
        if file.is_file() and file.suffix == ".txt" and file.name not in separate_files:
            with open(file) as f:
                words = f.read().strip().splitlines()
                for word in words:
                    blacklisted_words.add(word.upper())
                    
    with open(regular_words_file) as f:
        regular_words = f.read().strip().splitlines()
        for word in regular_words:
            regular_words_list.add(word.upper())
            
    with open(random_words_dc_file) as f:
        random_do_consider = f.read().strip().splitlines()
        for word in random_do_consider:
            random_words_dc.add(word.upper())

    return sorted(blacklisted_words), sorted(regular_words_list), sorted(random_words_dc)

if __name__ == "__main__":
    _, regular_words = load_blacklist_files()
    for word in regular_words:
        print(word)
