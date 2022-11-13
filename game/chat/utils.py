import random
from xkcdpass import xkcd_password as xp


word_file = xp.locate_wordfile()
words = xp.generate_wordlist(wordfile=word_file, min_length=5, max_length=8)


def generate_room_name():
    return xp.generate_xkcdpassword(words, numwords=4).title().replace(" ", "")


def generate_username():
    num_words = random.randint(1, 3)
    cases = [
        str.upper,
        str.title,
        str.lower,
    ]
    name_words = xp.generate_xkcdpassword(wordlist=words, numwords=num_words)
    name_words = "".join([random.choice(cases)(word) for word in name_words.split()])
    random_int = random.randint(0, 99999)
    return f"{name_words}{random_int}"


