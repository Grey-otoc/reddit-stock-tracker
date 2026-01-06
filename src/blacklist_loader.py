from pathlib import Path

"""
accesses blacklist files and adds each word to a list which can then be used for
ticker extraction filtering 
"""

def load_blacklist_files() -> list:
    current_dir = Path(__file__).resolve()
    blacklists_dir = current_dir.parent.parent / "blacklists"
    
    if not blacklists_dir.exists():
        print("Blacklists dir not found")
        return
    
    blacklisted_words = []
    for file in blacklists_dir.iterdir():
        if file.is_file() and file.suffix == ".txt":
            with open(file) as f:
                data = f.read().strip().splitlines()
                for word in data:
                    blacklisted_words.append(word.upper())
                    
    return list(set(blacklisted_words))
