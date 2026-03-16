import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

async def search_pubmed(query: str, max_results: int = 10) -> List[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
        "email": "research@iteragen.ai"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(PUBMED_SEARCH_URL, params=params)
        if response.status_code != 200:
            return []
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])

async def fetch_pubmed_abstracts(pmids: List[str]) -> List[Dict]:
    if not pmids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        "email": "research@iteragen.ai"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(PUBMED_FETCH_URL, params=params)
        if response.status_code != 200:
            return []
        return parse_pubmed_xml(response.text)

def parse_pubmed_xml(xml_text: str) -> List[Dict]:
    articles = []
    try:
        root = ET.fromstring(xml_text)
        for article in root.findall(".//PubmedArticle"):
            try:
                pmid_el = article.find(".//PMID")
                pmid = pmid_el.text if pmid_el is not None else ""

                title_el = article.find(".//ArticleTitle")
                title = title_el.text if title_el is not None else ""
                if title:
                    title = title.strip()

                abstract_parts = article.findall(".//AbstractText")
                abstract = " ".join(
                    [el.text for el in abstract_parts if el.text]
                ).strip()

                authors = []
                for author in article.findall(".//Author"):
                    last = author.find("LastName")
                    first = author.find("ForeName")
                    if last is not None:
                        name = last.text
                        if first is not None:
                            name = f"{last.text} {first.text}"
                        authors.append(name)

                journal_el = article.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else ""

                year_el = article.find(".//PubDate/Year")
                year = int(year_el.text) if year_el is not None else 0

                keywords = []
                for kw in article.findall(".//Keyword"):
                    if kw.text:
                        keywords.append(kw.text.strip())

                if pmid and title and abstract:
                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors[:5],
                        "journal": journal,
                        "year": year,
                        "keywords": keywords[:10]
                    })
            except:
                continue
    except:
        pass
    return articles

async def fetch_papers_for_target(target: str, disease: str, limit: int = 20) -> List[Dict]:
    queries = [
        f"{target} inhibitor {disease}",
        f"{target} binding site drug discovery",
        f"{disease} therapeutic target {target}",
        f"{target} kinase small molecule"
    ]
    all_pmids = []
    for query in queries:
        pmids = await search_pubmed(query, max_results=5)
        all_pmids.extend(pmids)

    unique_pmids = list(dict.fromkeys(all_pmids))[:limit]
    papers = await fetch_pubmed_abstracts(unique_pmids)
    return papers
