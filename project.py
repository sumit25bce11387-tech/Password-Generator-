import argparse
import secrets
import string
import math
import sys

WORD_LIST = [
    "apple","river","mountain","sunset","guitar","coffee","pencil","flower","ocean","forest",
    "moon","star","school","rocket","butter","bridge","winter","summer","garden","island",
    "stone","bird","cloud","planet","music","silent","bright","image","friend","wonder"
]

AMBIGUOUS = set("lI1O0o")

def make_pools(avoid, upper, digits, symbols):
    pools = []
    pools.append([c for c in string.ascii_lowercase if not (avoid and c in AMBIGUOUS)])
    if upper:
        pools.append([c for c in string.ascii_uppercase if not (avoid and c in AMBIGUOUS)])
    if digits:
        pools.append([c for c in string.digits if not (avoid and c in AMBIGUOUS)])
    if symbols:
        pools.append([c for c in "!@#$%^&*()-_=+[]{};:,.<>?/"])
    return pools

def combined(pools):
    x = []
    for p in pools: x.extend(p)
    out, seen = [], set()
    for c in x:
        if c not in seen:
            out.append(c)
            seen.add(c)
    return out

def make_password(length, upper, digits, symbols, avoid):
    pools = make_pools(avoid, upper, digits, symbols)
    for p in pools:
        if not p:
            raise ValueError("Character set is empty.")
    base = [secrets.choice(p) for p in pools]
    if length < len(base):
        base = base[:length]
        secrets.SystemRandom().shuffle(base)
        return ''.join(base)
    left = length - len(base)
    alphabet = combined(pools)
    base += [secrets.choice(alphabet) for _ in range(left)]
    secrets.SystemRandom().shuffle(base)
    return ''.join(base)

def entropy(length, alphabet_size):
    if alphabet_size <= 1: return 0.0
    return length * math.log2(alphabet_size)

def make_passphrase(words, sep="-"):
    return sep.join(secrets.choice(WORD_LIST) for _ in range(words))

def ask_int(msg, default, minv=None, maxv=None):
    while True:
        x = input(f"{msg} [{default}]: ").strip()
        if x == "": return default
        try:
            v = int(x)
            if minv is not None and v < minv: continue
            if maxv is not None and v > maxv: continue
            return v
        except:
            pass

def ask_yn(msg, default):
    while True:
        x = input(f"{msg} ({'Y/n' if default else 'y/N'}): ").strip().lower()
        if x == "": return default
        if x in ("y","yes"): return True
        if x in ("n","no"): return False

def menu():
    settings = {
        "mode": "char",
        "length": 12,
        "upper": True,
        "digits": True,
        "symbols": False,
        "avoid": False,
        "words": 4,
        "sep": "-",
        "number": 1
    }

    last = []

    while True:
        print("\n=== PASSWORD GENERATOR ===")
        print("1) Generate")
        print("2) Change settings")
        print("3) Show settings")
        print("4) Show last result")
        print("5) Exit")

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            last = []
            if settings["mode"] == "char":
                for _ in range(settings["number"]):
                    pwd = make_password(
                        settings["length"],
                        settings["upper"],
                        settings["digits"],
                        settings["symbols"],
                        settings["avoid"]
                    )
                    pools = make_pools(settings["avoid"], settings["upper"], settings["digits"], settings["symbols"])
                    alph = len(combined(pools))
                    bits = entropy(len(pwd), alph)
                    print(pwd)
                    print(f" -> length={len(pwd)}, alphabet={alph}, entropy={bits:.1f} bits\n")
                    last.append((pwd, alph, bits))
            else:
                for _ in range(settings["number"]):
                    phrase = make_passphrase(settings["words"], settings["sep"])
                    print(phrase)
                    last.append((phrase, None, None))

        elif choice == "2":
            print("\n1) Character Password")
            print("2) Passphrase")
            mode = input("Mode (1/2): ").strip()
            if mode == "2":
                settings["mode"] = "pass"
                settings["words"] = ask_int("Words per passphrase", settings["words"], 2, 12)
                sep = input(f"Separator [{settings['sep']}]: ").strip()
                if sep: settings["sep"] = sep
                settings["number"] = ask_int("How many", settings["number"], 1, 50)
            else:
                settings["mode"] = "char"
                settings["length"] = ask_int("Password length", settings["length"], 4, 128)
                settings["upper"] = ask_yn("Include uppercase?", settings["upper"])
                settings["digits"] = ask_yn("Include digits?", settings["digits"])
                settings["symbols"] = ask_yn("Include symbols?", settings["symbols"])
                settings["avoid"] = ask_yn("Avoid ambiguous characters?", settings["avoid"])
                settings["number"] = ask_int("How many", settings["number"], 1, 50)

            print("\nSettings updated.")

        elif choice == "3":
            print("\nCurrent settings:")
            for k, v in settings.items():
                print(f" {k}: {v}")

        elif choice == "4":
            if not last:
                print("No passwords generated yet.")
            else:
                for i, item in enumerate(last, 1):
                    print(i, ")", item[0])

        elif choice == "5":
            print("Goodbye!")
            return
        else:
            print("Invalid choice.")

def parse():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("mode", nargs="?")
    return parser.parse_args()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse()
        print("Menu disabled when using arguments.")
    else:
        menu()
