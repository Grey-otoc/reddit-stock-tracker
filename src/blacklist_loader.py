from pathlib import Path

"""
accesses blacklist files and adds each word to a list which can then be used for
ticker extraction filtering 
"""

def load_blacklist_files() -> set:
    current_dir = Path(__file__).resolve()
    blacklists_dir = current_dir.parent.parent / "blacklists"
    common_words_file = blacklists_dir / "common_words.txt"

    # if our blacklists dir or common words file do not exist, the main logic of
    # our program cannot function properly
    if not blacklists_dir.exists() or not common_words_file.exists():
        raise FileNotFoundError("FATAL ERROR: Blacklists directory or common words list does not exist.")
    
    blacklisted_words = set()
    common_words_list = set()
    for file in blacklists_dir.iterdir():
        if file.is_file() and file.suffix == ".txt" and file.name != "common_words.txt":
            with open(file) as f:
                words = f.read().strip().splitlines()
                for word in words:
                    blacklisted_words.add(word.upper())
                    
    with open(common_words_file) as f:
        common_words = f.read().strip().splitlines()
        for word in common_words:
            common_words_list.add(word.upper())

    return sorted(blacklisted_words), sorted(common_words_list)

if __name__ == "__main__":
    _, common_words = load_blacklist_files()
    for word in common_words:
        print(word)
