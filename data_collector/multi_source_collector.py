import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from .clinical_trials_collector import ClinicalTrialsCollector
from .pubmed_collector import PubMedCollector
from .fda_collector import FDACollector

logger = logging.getLogger(__name__)

class MultiSourceDataCollector:
    """
    Multi-source data collector for pharmaceutical competitive intelligence.
    
    Collects data from multiple sources:
    - ClinicalTrials.gov (clinical trials)
    - PubMed (scientific publications)
    - FDA (drug approvals, safety data)
    - EMA (European regulatory data)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the multi-source collector with configuration."""
        self.config = config
        self.collectors = {}
        
        # Initialize individual collectors based on config
        if 'clinical_trials' in config.get('data_collection', {}):
            self.collectors['clinical_trials'] = ClinicalTrialsCollector(config)
            
        if 'pubmed' in config.get('data_collection', {}):
            self.collectors['pubmed'] = PubMedCollector(config)
            
        if 'fda' in config.get('data_collection', {}):
            self.collectors['fda'] = FDACollector(config)
            
        logger.info(f"Initialized {len(self.collectors)} data collectors: {list(self.collectors.keys())}")
        
    def collect_all_data(self, research_config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect data from all configured sources for the given research configuration.
        
        Args:
            research_config: Research configuration dictionary
            
        Returns:
            Dictionary with source names as keys and lists of data as values
        """
        all_data = {}
        start_time = time.time()
        
        logger.info(f"Starting multi-source data collection for: {research_config['name']}")
        
        for source_name, collector in self.collectors.items():
            try:
                logger.info(f"Collecting data from {source_name}...")
                source_start = time.time()
                
                if source_name == 'clinical_trials':
                    data = collector.fetch_trials_for_research(research_config)
                    # Filter to active trials
                    data = collector.filter_active_trials(data)
                else:
                    data = collector.fetch_data_for_research(research_config)
                    
                source_time = time.time() - source_start
                logger.info(f"Collected {len(data)} records from {source_name} in {source_time:.2f}s")
                all_data[source_name] = data
                
            except Exception as e:
                logger.error(f"Error collecting data from {source_name}: {e}")
                all_data[source_name] = []
                
        total_time = time.time() - start_time
        total_records = sum(len(data) for data in all_data.values())
        logger.info(f"Multi-source collection completed in {total_time:.2f}s with {total_records} total records")
        
        return all_data
        
    def get_data_summary(self, all_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Generate a summary of collected data from all sources.
        
        Args:
            all_data: Dictionary with source names as keys and lists of data as values
            
        Returns:
            Summary dictionary with statistics for each source
        """
        summary = {
            'total_sources': len(all_data),
            'total_records': sum(len(data) for data in all_data.values()),
            'sources': {},
            'collection_timestamp': datetime.now().isoformat()
        }
        
        for source_name, data in all_data.items():
            summary['sources'][source_name] = {
                'record_count': len(data),
                'status': 'success' if data else 'no_data'
            }
            
        return summary
        
    def merge_data_by_topic(self, all_data: Dict[str, List[Dict[str, Any]]], 
                           research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Merge data from different sources and organize by research topic.
        
        Args:
            all_data: Dictionary with source names as keys and lists of data as values
            research_config: Research configuration dictionary
            
        Returns:
            Merged list of data records with source information
        """
        merged_data = []
        
        for source_name, data_list in all_data.items():
            for record in data_list:
                # Add source metadata to each record
                record['data_source'] = source_name
                record['research_area'] = research_config['name']
                record['research_type'] = research_config['research_type']
                record['original_topic'] = research_config['original_topic']
                record['collection_timestamp'] = datetime.now().isoformat()
                
                merged_data.append(record)
                
        logger.info(f"Merged {len(merged_data)} records from {len(all_data)} sources")
        return merged_data
        
    def filter_relevant_data(self, data: List[Dict[str, Any]], 
                           research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter data to only include records relevant to the research topic.
        
        Args:
            data: List of data records
            research_config: Research configuration dictionary
            
        Returns:
            Filtered list of relevant data records
        """
        keywords = [k.lower() for k in research_config['keywords']]
        relevant_data = []
        
        for record in data:
            # Check if any keyword appears in the record
            record_text = str(record).lower()
            if any(keyword in record_text for keyword in keywords):
                relevant_data.append(record)
                
        logger.info(f"Filtered to {len(relevant_data)} relevant records out of {len(data)} total")
        return relevant_data 