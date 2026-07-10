def format_sources(source_documents: list) -> list[dict]:
    sources = []
    for doc in source_documents[:3]:
        sources.append({
            "title": doc.metadata.get("title", "N/A"),
            "first_date": doc.metadata.get("first_date", "N/A"),
            "url": doc.metadata.get("url", ""),
            "city": doc.metadata.get("city", "N/A"),
        })
    return sources
