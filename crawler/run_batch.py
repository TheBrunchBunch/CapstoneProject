import subprocess

# Keyword list for batch processing
keywords = [
    "Cotter pin",
    "Staple",
    "Rivet",
    "Adhesive",
    "Surface: mating",
    "Surface: press fit",
    "Snap fit",
    "Surface: press fit",
    "Surface: mould",
    "Seam fold",
    "Seal",
    "Solder",
    "Weld"
]

for keyword in keywords:
    print(f"\n=== Running query: {keyword} ===")
    try:
        # mock user input for the keyword
        input_text = f"{keyword}\ny\n"
        subprocess.run(
            ["python", "main_clawer.py"],
            input=input_text.encode("utf-8"),
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error while processing '{keyword}': {e}")
