import requests
import logging
from typing import Dict, List, Any, Optional
import time
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class ClinicalTrialsCollector:
    """Collects clinical trial data from ClinicalTrials.gov API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the collector with configuration settings."""
        self.config = config
        self.base_url = config['data_collection']['clinical_trials']['base_url']
        self.fields = config['data_collection']['clinical_trials']['fields']
        self.max_results = config['data_collection']['clinical_trials']['max_results']
        
    def build_query_params(self, research_config: Dict[str, Any]) -> Dict[str, str]:
        """Build query parameters for the ClinicalTrials.gov API v2."""
        # Only use pageSize for the first page
        return {
            'pageSize': str(min(self.max_results, 100))
        }
        
    def fetch_trials(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch clinical trials for a specific research configuration.
        
        Args:
            research_config: Dictionary containing research configuration
            
        Returns:
            List of clinical trial data dictionaries
        """
        try:
            logger.info(f"Fetching trials for research: {research_config['name']}")
            
            # Build query parameters
            params = self.build_query_params(research_config)
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            studies = data.get('studies', [])
            
            # Filter studies by research keywords
            filtered_studies = []
            keywords = [k.lower() for k in research_config['keywords']]
            
            for study in studies:
                # Check if any keyword appears in the study data
                study_text = str(study).lower()
                if any(keyword in study_text for keyword in keywords):
                    study['research_area'] = research_config['name']
                    study['research_type'] = research_config['research_type']
                    study['original_topic'] = research_config['original_topic']
                    filtered_studies.append(study)
            
            logger.info(f"Retrieved {len(filtered_studies)} relevant trials for {research_config['name']} out of {len(studies)} total")
            
            return filtered_studies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trials for {research_config['name']}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching trials for {research_config['name']}: {e}")
            return []
            
    def fetch_trials_for_research(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch clinical trials for a specific research configuration.
        
        Args:
            research_config: Research configuration dictionary
            
        Returns:
            List of clinical trial data dictionaries
        """
        trials = self.fetch_trials(research_config)
        
        logger.info(f"Total trials collected for {research_config['name']}: {len(trials)}")
        return trials
        
    def filter_active_trials(self, trials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter trials to only include active/recruiting trials.
        
        Args:
            trials: List of clinical trial data dictionaries
            
        Returns:
            Filtered list of active trials
        """
        active_trials = []
        
        for trial in trials:
            # Check status in the new API structure
            status_module = trial.get('protocolSection', {}).get('statusModule', {})
            status = status_module.get('overallStatus', '').lower()
            
            if any(active_status in status for active_status in ['recruiting', 'active', 'enrolling']):
                active_trials.append(trial)
                
        logger.info(f"Filtered to {len(active_trials)} active trials out of {len(trials)} total")
        return active_trials
        
    def get_trial_summary(self, trial: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from a trial for summary purposes.
        
        Args:
            trial: Clinical trial data dictionary
            
        Returns:
            Dictionary with key trial information
        """
        # Extract data from the new API structure
        protocol_section = trial.get('protocolSection', {})
        identification = protocol_section.get('identificationModule', {})
        status = protocol_section.get('statusModule', {})
        sponsor = protocol_section.get('sponsorCollaboratorsModule', {})
        
        return {
            'nct_id': identification.get('nctId', ''),
            'title': identification.get('briefTitle', ''),
            'condition': trial.get('condition', ''),
            'phase': trial.get('phase', ''),
            'status': status.get('overallStatus', ''),
            'sponsor': sponsor.get('leadSponsor', {}).get('name', ''),
            'intervention': trial.get('intervention', ''),
            'start_date': status.get('startDateStruct', {}).get('date', ''),
            'completion_date': status.get('completionDateStruct', {}).get('date', ''),
            'research_area': trial.get('research_area', ''),
            'research_type': trial.get('research_type', ''),
            'original_topic': trial.get('original_topic', '')
        } 