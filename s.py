from pathlib import Path

p = Path.cwd() / "TWI-BIBLE"

for file in p.glob("*.txt"):
    with open(file, "r") as f:
        content = f.read()
    if not content.strip():
        print("Empty file: ", file)
