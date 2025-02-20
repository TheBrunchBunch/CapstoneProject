from scholarly import scholarly

# search for the query
query = "aviation disassembly"
search_results = scholarly.search_pubs(query)



# save the search results to a file
with open(f"links/article_{query}.txt", "w", encoding="utf-8") as f:
    for i in range(100):
        article = next(search_results)
        # save the article to a file
        f.write(f"Title: {article['bib']['title']}\n")
        f.write(f"Authors: {article['bib']['author']}\n")
        f.write(f"Year: {article['bib']['pub_year']}\n")
        url = article.get('pub_url', 'N/A')  
        f.write(f"URL: {url}\n")