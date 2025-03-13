from scholarly import scholarly
import csv

# search for the query
query = "discrete components disassembly"
save_path = "../links/"


def get_info_from_qurey(query, save_path):
    search_results = scholarly.search_pubs(query)
    # save the search results to a csv file
    with open(f"{save_path}article_{query}.csv", "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ['Title', 'Authors', 'Year', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for _ in range(100):
            article = next(search_results)
            writer.writerow({
                'Title': article['bib']['title'],
                'Authors': article['bib']['author'],
                'Year': article['bib']['pub_year'],
                'URL': article.get('pub_url', 'NA')
            })
    print(f"Saved to {save_path}article_{query}.csv")