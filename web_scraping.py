# from serpapi import GoogleSearch

# params = {
#     "engine": "google_scholar",
#     "q": "deep learning for medical image analysis",
#     "api_key": "0f1b549db6de719ab5704f425c728683af739aa2c11b919b14557153c494c315"
# }

# search = GoogleSearch(params)
# results = search.get_dict()

# # 获取论文信息
# for article in results["organic_results"][:5]:
#     print(f"Title: {article['title']}")
#     print(f"Authors: {article.get('publication_info', {}).get('summary', 'N/A')}")
#     print(f"Link: {article['link']}\n")

from scholarly import scholarly

# 搜索关键词
query = "aviation disassembly"
search_results = scholarly.search_pubs(query)



# 获取前100篇文章的信息
with open(f"article_{query}.txt", "w", encoding="utf-8") as f:
    for i in range(100):
        article = next(search_results)
        # save the article to a file
        f.write(f"Title: {article['bib']['title']}\n")
        f.write(f"Authors: {article['bib']['author']}\n")
        f.write(f"Year: {article['bib']['pub_year']}\n")
        url = article.get('pub_url', 'N/A')  
        f.write(f"URL: {url}\n")

        print(f"Title: {article['bib']['title']}")
        print(f"Authors: {article['bib']['author']}")
        print(f"Year: {article['bib']['pub_year']}")
        print(f"URL: {url}\n")