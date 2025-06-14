import os
import yaml
import google.generativeai as genai
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClinicalTrialAnalyzer:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the analyzer with configuration settings."""
        # Load environment variables from .env file
        load_dotenv()
        
        self.config = self._load_config(config_path)
        self._setup_gemini()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
            
    def _setup_gemini(self):
        """Set up Gemini API with API key from environment."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please create a .env file with your API key.")
        genai.configure(api_key=api_key)
        
    def analyze_trial(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single clinical trial and generate insights.
        
        Args:
            trial_data: Dictionary containing trial information
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract relevant information
            title = trial_data.get('BriefTitle', '')
            phase = trial_data.get('Phase', '')
            status = trial_data.get('OverallStatus', '')
            sponsor = trial_data.get('LeadSponsor', {}).get('Name', '')
            
            # Generate analysis using Gemini
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Analyze this clinical trial and provide insights:
            Title: {title}
            Phase: {phase}
            Status: {status}
            Sponsor: {sponsor}
            
            Please provide:
            1. Key therapeutic focus
            2. Potential market impact
            3. Competitive positioning
            4. Risk assessment
            """
            
            response = model.generate_content(prompt)
            
            return {
                'trial_id': trial_data.get('NCTId', ''),
                'title': title,
                'analysis': response.text,
                'metadata': {
                    'phase': phase,
                    'status': status,
                    'sponsor': sponsor
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trial: {e}")
            return {
                'trial_id': trial_data.get('NCTId', ''),
                'error': str(e)
            }
            
    def analyze_trials_batch(self, trials_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple clinical trials in batch.
        
        Args:
            trials_data: List of dictionaries containing trial information
            
        Returns:
            List of dictionaries containing analysis results
        """
        results = []
        for trial in trials_data:
            analysis = self.analyze_trial(trial)
            results.append(analysis)
        return results
        
    def generate_landscape_summary(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the competitive landscape based on multiple trial analyses.
        
        Args:
            analyses: List of trial analysis results
            
        Returns:
            String containing the landscape summary
        """
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare context from analyses
            context = "\n\n".join([
                f"Trial: {analysis['title']}\nAnalysis: {analysis['analysis']}"
                for analysis in analyses
            ])
            
            prompt = f"""
            Based on the following clinical trial analyses, provide a comprehensive summary of the competitive landscape:
            
            {context}
            
            Please include:
            1. Overall market trends
            2. Key players and their strategies
            3. Emerging therapeutic approaches
            4. Potential market opportunities
            5. Risk factors and challenges
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating landscape summary: {e}")
            return f"Error generating summary: {str(e)}" 