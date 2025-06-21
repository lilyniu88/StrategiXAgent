import os
import yaml
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import google.generativeai, but don't fail if it's not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google.generativeai not available. AI analysis features will be disabled.")

class ClinicalTrialAnalyzer:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the analyzer with configuration settings."""
        # Load environment variables from .env file
        load_dotenv()
        
        self.config = self._load_config(config_path)
        if GEMINI_AVAILABLE:
            self._setup_gemini()
        else:
            logger.warning("Gemini AI not available - analysis features disabled")
        
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
        if not GEMINI_AVAILABLE:
            return
            
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
        if not GEMINI_AVAILABLE:
            # Return basic analysis without AI
            protocol_section = trial_data.get('protocolSection', {})
            identification = protocol_section.get('identificationModule', {})
            status = protocol_section.get('statusModule', {})
            sponsor = protocol_section.get('sponsorCollaboratorsModule', {})
            
            title = identification.get('briefTitle', '')
            status_text = status.get('overallStatus', '')
            sponsor_name = sponsor.get('leadSponsor', {}).get('name', '')
            
            return {
                'trial_id': identification.get('nctId', ''),
                'title': title,
                'analysis': f"Basic analysis: Trial {title} by {sponsor_name} is in {status_text} status. AI analysis not available.",
                'metadata': {
                    'phase': 'Not analyzed',
                    'status': status_text,
                    'sponsor': sponsor_name
                }
            }
            
        try:
            # Extract relevant information from the new API structure
            protocol_section = trial_data.get('protocolSection', {})
            identification = protocol_section.get('identificationModule', {})
            status = protocol_section.get('statusModule', {})
            sponsor = protocol_section.get('sponsorCollaboratorsModule', {})
            
            title = identification.get('briefTitle', '')
            status_text = status.get('overallStatus', '')
            sponsor_name = sponsor.get('leadSponsor', {}).get('name', '')
            
            # Get phase information
            design_module = protocol_section.get('designModule', {})
            phases = design_module.get('phases', [])
            phase = ', '.join(phases) if phases else 'Not specified'
            
            # Get model name from config
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            
            # Generate analysis using Gemini
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            Analyze this clinical trial and provide insights:
            Title: {title}
            Phase: {phase}
            Status: {status_text}
            Sponsor: {sponsor_name}
            
            Please provide:
            1. Key therapeutic focus
            2. Potential market impact
            3. Competitive positioning
            4. Risk assessment
            """
            
            response = model.generate_content(prompt)
            
            return {
                'trial_id': identification.get('nctId', ''),
                'title': title,
                'analysis': response.text,
                'metadata': {
                    'phase': phase,
                    'status': status_text,
                    'sponsor': sponsor_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trial: {e}")
            return {
                'trial_id': trial_data.get('protocolSection', {}).get('identificationModule', {}).get('nctId', ''),
                'title': trial_data.get('protocolSection', {}).get('identificationModule', {}).get('briefTitle', 'Unknown'),
                'analysis': f"Analysis failed: {str(e)}",
                'metadata': {
                    'phase': 'Error',
                    'status': 'Error',
                    'sponsor': 'Error'
                }
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
        if not GEMINI_AVAILABLE:
            # Generate basic summary without AI
            trial_count = len(analyses)
            sponsors = set()
            for analysis in analyses:
                sponsor = analysis.get('metadata', {}).get('sponsor', 'Unknown')
                if sponsor and sponsor != 'Error':
                    sponsors.add(sponsor)
            
            return f"""
            Basic Competitive Landscape Summary (AI analysis not available)
            
            Total trials analyzed: {trial_count}
            Number of unique sponsors: {len(sponsors)}
            Sponsors: {', '.join(sponsors) if sponsors else 'None identified'}
            
            Note: For detailed AI-powered analysis, install google-generativeai package.
            """
            
        try:
            # Get model name from config
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            
            # Prepare context from analyses, filtering out failed analyses
            valid_analyses = []
            for analysis in analyses:
                if analysis.get('title') and analysis.get('analysis') and not analysis.get('analysis', '').startswith('Analysis failed:'):
                    valid_analyses.append(analysis)
            
            if not valid_analyses:
                return "No valid analyses available for summary generation."
            
            context = "\n\n".join([
                f"Trial: {analysis.get('title', 'Unknown')}\nAnalysis: {analysis.get('analysis', 'No analysis available')}"
                for analysis in valid_analyses
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