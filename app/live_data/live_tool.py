from ddgs import DDGS



def web_search(query, max_results=5):
  """
    Search the web using DuckDuckGo.
    """
  

  print("\nSearching web...")
  print("Query:", query)

  results = []

  with DDGS() as ddgs:
        search_results = ddgs.text(
            query,
            max_results=max_results
        )

        for result in search_results:
            results.append({
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body")
            })

  return results



if __name__ == "__main__":

    query = input("Enter your search query: ")

    results = web_search(query)

    print("\n==============================")
    print("       WEB SEARCH RESULTS")
    print("==============================")

    for i, result in enumerate(results, start=1):

        print(f"\n--- Result {i} ---")

        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Snippet:", result["snippet"])

    