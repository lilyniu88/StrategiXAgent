import requests
import logging
from typing import Dict, List, Any, Optional
import time
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class FDACollector:
    """Collects drug approval and safety data from FDA APIs."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the FDA collector with configuration settings."""
        self.config = config
        fda_config = config.get('data_collection', {}).get('fda', {})
        self.base_url = fda_config.get('base_url', 'https://api.fda.gov')
        self.max_results = fda_config.get('max_results', 100)
        self.api_key = fda_config.get('api_key', '')  # Optional FDA API key
        
    def build_search_query(self, research_config: Dict[str, Any]) -> str:
        """Build FDA search query from research configuration."""
        keywords = research_config['keywords']
        query_terms = []
        
        # Add main keywords - use OR instead of AND for broader results
        for keyword in keywords:
            query_terms.append(f'"{keyword}"')
        
        # Add drug name if specified - search in generic name field
        if research_config.get('drug_name'):
            query_terms.append(f'openfda.generic_name:"{research_config["drug_name"]}"')
            
        # Add indication if specified - search in indications field
        if research_config.get('indication'):
            query_terms.append(f'indications_and_usage:"{research_config["indication"]}"')
            
        # Combine terms with OR for broader results, then limit with AND for drug name if available
        if research_config.get('drug_name'):
            # If we have a specific drug, use it as the primary filter
            drug_query = f'openfda.generic_name:"{research_config["drug_name"]}"'
            keyword_query = " OR ".join(query_terms)
            return f'({drug_query}) AND ({keyword_query})'
        else:
            # Otherwise, use OR for broader results - this will return many more results
            return " OR ".join(query_terms)
        
    def fetch_drug_approvals(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch drug approval data from FDA."""
        try:
            query = self.build_search_query(research_config)
            params = {
                'search': query,
                'limit': self.max_results,
                'sort': 'effective_time:desc'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            url = f"{self.base_url}/drug/label.json"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            approvals = []
            for result in results:
                approval = self._parse_drug_approval(result, research_config)
                if approval:
                    approvals.append(approval)
                    
            logger.info(f"Fetched {len(approvals)} drug approvals from FDA")
            return approvals
            
        except Exception as e:
            logger.error(f"Error fetching FDA drug approvals: {e}")
            return []
            
    def fetch_safety_data(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch drug safety data from FDA."""
        try:
            # Use a more flexible query for safety data
            drug_name = research_config.get('drug_name', '')
            keywords = research_config['keywords']
            
            if drug_name:
                # If we have a specific drug, search for it
                query = f'patient.drug.medicinalproduct:"{drug_name}"'
            else:
                # Use broader keyword search
                query = " OR ".join([f'"{keyword}"' for keyword in keywords[:3]])  # Use first 3 keywords
                
            params = {
                'search': query,
                'limit': min(self.max_results, 50),  # Reduce limit to avoid errors
                'sort': 'report_date:desc'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            url = f"{self.base_url}/drug/event.json"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            safety_reports = []
            for result in results:
                safety_report = self._parse_safety_data(result, research_config)
                if safety_report:
                    safety_reports.append(safety_report)
                    
            logger.info(f"Fetched {len(safety_reports)} safety reports from FDA")
            return safety_reports
            
        except Exception as e:
            logger.error(f"Error fetching FDA safety data: {e}")
            return []
            
    def fetch_recalls(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch drug recall data from FDA."""
        try:
            # Use a more flexible query for recalls
            drug_name = research_config.get('drug_name', '')
            keywords = research_config['keywords']
            
            if drug_name:
                # If we have a specific drug, search for it
                query = f'product_description:"{drug_name}"'
            else:
                # Use broader keyword search
                query = " OR ".join([f'"{keyword}"' for keyword in keywords[:3]])  # Use first 3 keywords
                
            params = {
                'search': query,
                'limit': min(self.max_results, 50),  # Reduce limit to avoid errors
                'sort': 'recall_initiation_date:desc'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            url = f"{self.base_url}/drug/enforcement.json"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            recalls = []
            for result in results:
                recall = self._parse_recall_data(result, research_config)
                if recall:
                    recalls.append(recall)
                    
            logger.info(f"Fetched {len(recalls)} recalls from FDA")
            return recalls
            
        except Exception as e:
            logger.error(f"Error fetching FDA recall data: {e}")
            return []
            
    def _parse_drug_approval(self, result: Dict[str, Any], research_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse FDA drug approval data."""
        try:
            # Extract basic information
            openfda = result.get('openfda', {})
            meta = result.get('meta', {})
            
            return {
                'fda_id': result.get('id', ''),
                'drug_name': openfda.get('generic_name', [''])[0] if openfda.get('generic_name') else '',
                'brand_name': openfda.get('brand_name', [''])[0] if openfda.get('brand_name') else '',
                'manufacturer': openfda.get('manufacturer_name', [''])[0] if openfda.get('manufacturer_name') else '',
                'substance_name': openfda.get('substance_name', [''])[0] if openfda.get('substance_name') else '',
                'indications': result.get('indications_and_usage', ['']),
                'dosage_form': openfda.get('dosage_form', ['']),
                'route': openfda.get('route', ['']),
                'approval_date': meta.get('effective_time', ''),
                'data_source': 'fda_approvals',
                'research_area': research_config['name'],
                'research_type': research_config['research_type'],
                'original_topic': research_config['original_topic']
            }
            
        except Exception as e:
            logger.error(f"Error parsing FDA drug approval: {e}")
            return None
            
    def _parse_safety_data(self, result: Dict[str, Any], research_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse FDA safety data."""
        try:
            patient = result.get('patient', {})
            drug_info = result.get('patient', {}).get('drug', [{}])[0] if result.get('patient', {}).get('drug') else {}
            
            return {
                'fda_id': result.get('id', ''),
                'drug_name': drug_info.get('medicinalproduct', ''),
                'manufacturer': drug_info.get('manufacturername', ''),
                'adverse_events': result.get('patient', {}).get('reaction', []),
                'serious': result.get('serious', ''),
                'report_date': result.get('report_date', ''),
                'data_source': 'fda_safety',
                'research_area': research_config['name'],
                'research_type': research_config['research_type'],
                'original_topic': research_config['original_topic']
            }
            
        except Exception as e:
            logger.error(f"Error parsing FDA safety data: {e}")
            return None
            
    def _parse_recall_data(self, result: Dict[str, Any], research_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse FDA recall data."""
        try:
            return {
                'fda_id': result.get('id', ''),
                'product_name': result.get('product_description', ''),
                'manufacturer': result.get('recalling_firm', ''),
                'reason': result.get('reason_for_recall', ''),
                'recall_date': result.get('recall_initiation_date', ''),
                'classification': result.get('classification', ''),
                'data_source': 'fda_recalls',
                'research_area': research_config['name'],
                'research_type': research_config['research_type'],
                'original_topic': research_config['original_topic']
            }
            
        except Exception as e:
            logger.error(f"Error parsing FDA recall data: {e}")
            return None
            
    def fetch_data_for_research(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch FDA data for a specific research configuration.
        
        Args:
            research_config: Dictionary containing research configuration
            
        Returns:
            List of FDA data dictionaries
        """
        try:
            logger.info(f"Fetching FDA data for research: {research_config['name']}")
            
            all_data = []
            
            # Fetch drug approvals
            approvals = self.fetch_drug_approvals(research_config)
            all_data.extend(approvals)
            
            # Fetch safety data
            safety_data = self.fetch_safety_data(research_config)
            all_data.extend(safety_data)
            
            # Fetch recalls
            recalls = self.fetch_recalls(research_config)
            all_data.extend(recalls)
            
            logger.info(f"Retrieved {len(all_data)} FDA records for {research_config['name']}")
            return all_data
            
        except Exception as e:
            logger.error(f"Error fetching FDA data for {research_config['name']}: {e}")
            return [] 