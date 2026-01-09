from pathlib import Path

"""
accesses blacklist files and adds each word to a list which can then be used for
ticker extraction filtering 
"""

def load_blacklist_files() -> set:
    current_dir = Path(__file__).resolve()
    blacklists_dir = current_dir.parent.parent / "blacklists"
    
    if not blacklists_dir.exists():
        print("NON-FATAL ERROR: Blacklists dir not found.")
        return set()
    
    blacklisted_words = set()
    for file in blacklists_dir.iterdir():
        if file.is_file() and file.suffix == ".txt":
            with open(file) as f:
                words = f.read().strip().splitlines()
                for word in words:
                    blacklisted_words.add(word.upper())
                    
    return sorted(blacklisted_words)

if __name__ == "__main__":
    blacklist = load_blacklist_files()
    for word in blacklist:
        print(word)
