import requests
import logging
from typing import Dict, List, Any, Optional
import time
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class PubMedCollector:
    """Collects scientific publication data from PubMed/NCBI."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the PubMed collector with configuration settings."""
        self.config = config
        pubmed_config = config.get('data_collection', {}).get('pubmed', {})
        self.base_url = pubmed_config.get('base_url', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/')
        self.max_results = pubmed_config.get('max_results', 50)
        self.api_key = pubmed_config.get('api_key', '')  # Optional NCBI API key
        
    def build_search_query(self, research_config: Dict[str, Any]) -> str:
        """Build PubMed search query from research configuration."""
        keywords = research_config['keywords']
        query_terms = []
        
        # Add main keywords
        query_terms.extend(keywords)
        
        # Add drug name if specified
        if research_config.get('drug_name'):
            query_terms.append(research_config['drug_name'])
            
        # Add indication if specified
        if research_config.get('indication'):
            query_terms.append(research_config['indication'])
            
        # Add date filter for recent publications (last 5 years)
        query_terms.append("(\"2020\"[Date - Publication] : \"3000\"[Date - Publication])")
        
        # Combine terms with AND
        return " AND ".join(query_terms)
        
    def search_pubmed(self, query: str) -> List[str]:
        """Search PubMed and return list of PMIDs."""
        try:
            # Build search URL
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': self.max_results,
                'retmode': 'xml',
                'sort': 'date'  # Most recent first
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            search_url = f"{self.base_url}esearch.fcgi"
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            id_list = root.find('.//IdList')
            
            if id_list is not None:
                pmids = [id_elem.text for id_elem in id_list.findall('Id') if id_elem.text is not None]
                logger.info(f"Found {len(pmids)} PubMed articles for query: {query}")
                return pmids
            else:
                logger.warning("No PMIDs found in PubMed search response")
                return []
                
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
            
    def fetch_article_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed information for PubMed articles."""
        if not pmids:
            return []
            
        try:
            # Fetch article details
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml',
                'rettype': 'abstract'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            fetch_url = f"{self.base_url}efetch.fcgi"
            response = requests.get(fetch_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            articles = []
            
            for pubmed_article in root.findall('.//PubmedArticle'):
                article = self._parse_pubmed_article(pubmed_article)
                if article:
                    articles.append(article)
                    
            logger.info(f"Fetched details for {len(articles)} PubMed articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching PubMed article details: {e}")
            return []
            
    def _parse_pubmed_article(self, pubmed_article: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a single PubMed article from XML."""
        try:
            # Extract basic information
            medline_citation = pubmed_article.find('.//MedlineCitation')
            if medline_citation is None:
                return None
                
            article = medline_citation.find('.//Article')
            if article is None:
                return None
                
            # Extract PMID
            pmid_elem = medline_citation.find('PMID')
            pmid = pmid_elem.text if pmid_elem is not None else ''
            
            # Extract title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ''
            
            # Extract abstract
            abstract_elem = article.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ''
            
            # Extract authors
            authors = []
            author_list = article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('Author'):
                    last_name = author.find('LastName')
                    first_name = author.find('ForeName')
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
                        
            # Extract journal information
            journal_elem = article.find('.//Journal')
            journal_title = ''
            if journal_elem is not None:
                title_elem = journal_elem.find('.//Title')
                if title_elem is not None:
                    journal_title = title_elem.text
                    
            # Extract publication date
            pub_date = article.find('.//PubDate')
            publication_date = ''
            if pub_date is not None:
                year_elem = pub_date.find('Year')
                if year_elem is not None:
                    publication_date = year_elem.text
                    
            # Extract keywords
            keywords = []
            mesh_headings = medline_citation.findall('.//MeshHeadingList/MeshHeading')
            for mesh in mesh_headings:
                descriptor = mesh.find('DescriptorName')
                if descriptor is not None and descriptor.text:
                    keywords.append(descriptor.text)
                    
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal_title,
                'publication_date': publication_date,
                'keywords': keywords,
                'data_source': 'pubmed',
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ''
            }
            
        except Exception as e:
            logger.error(f"Error parsing PubMed article: {e}")
            return None
            
    def fetch_data_for_research(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch PubMed data for a specific research configuration.
        
        Args:
            research_config: Dictionary containing research configuration
            
        Returns:
            List of PubMed article data dictionaries
        """
        try:
            logger.info(f"Fetching PubMed articles for research: {research_config['name']}")
            
            # Build search query
            query = self.build_search_query(research_config)
            logger.info(f"PubMed search query: {query}")
            
            # Search for articles
            pmids = self.search_pubmed(query)
            
            if not pmids:
                logger.warning("No PubMed articles found for the search query")
                return []
                
            # Fetch article details
            articles = self.fetch_article_details(pmids)
            
            # Add research metadata
            for article in articles:
                article['research_area'] = research_config['name']
                article['research_type'] = research_config['research_type']
                article['original_topic'] = research_config['original_topic']
                
            logger.info(f"Retrieved {len(articles)} PubMed articles for {research_config['name']}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching PubMed data for {research_config['name']}: {e}")
            return [] 