import subprocess
import time


# batch processing keywords
keywords = [
    "Bundling"
    "Spring",
    "Screw",
    "Bolt",
    "Nut",
    "Washer",
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
    keyword = keyword+" industry disassembly"
    print(f"\n Processing keyword: {keyword}")
    
    # call google_search.py to perform Google search with the keyword
    try:
        subprocess.run(
            ["python", "google_search.py"],
            input=f"{keyword}\n".encode("utf-8"),
            check=True
        )
    except subprocess.CalledProcessError:
        print(f"Searching Error: {keyword}")
        continue
    # call web_scraping.py to extract text and update the content field

    # delay = 2 
    time.sleep(2)
try:
    subprocess.run(["python", "web_scraping.py"], check=True)
except subprocess.CalledProcessError:
    print(f"Web scraping Error: {keyword}")

print("\n Finished")
