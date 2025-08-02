import os
import yaml
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Try to import google.generativeai, but don't fail if it's not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Global flag to disable AI after rate limit detection
AI_RATE_LIMIT_HIT = False

def load_config_file(config_path: str) -> Dict[str, Any]:
    """Shared utility to load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
        if not isinstance(config, dict):
            raise ValueError("Config file must contain a dictionary")
        return config
    except Exception as e:
        raise

def setup_gemini(config: Optional[Dict[str, Any]] = None) -> bool:
    """Shared utility to set up Gemini API with API key from environment."""
    global AI_RATE_LIMIT_HIT
    
    if not GEMINI_AVAILABLE:
        return False
        
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return False
    
    # Check if AI analysis is disabled due to rate limits
    if os.getenv('DISABLE_AI_ANALYSIS') == 'true' or AI_RATE_LIMIT_HIT:
        return False
        
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        return False

class ClinicalTrialAnalyzer:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the analyzer with configuration settings."""
        # Load environment variables from .env file
        load_dotenv()
        
        self.config = load_config_file(config_path)
        if setup_gemini(self.config):
            pass
        else:
            pass        
    def analyze_trial(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single data record and generate insights.
        
        Args:
            trial_data: Dictionary containing data information (could be clinical trial, PubMed article, FDA data)
            
        Returns:
            Dictionary containing analysis results
        """
        if not GEMINI_AVAILABLE:
            return self._analyze_trial_fallback(trial_data)
            
        try:
            # Determine data source and extract relevant information
            data_source = trial_data.get('data_source', 'unknown')
            
            if data_source == 'clinical_trials':
                return self._analyze_clinical_trial(trial_data)
            elif data_source == 'pubmed':
                return self._analyze_pubmed_article(trial_data)
            elif data_source == 'fda':
                return self._analyze_fda_data(trial_data)
            else:
                return self._analyze_generic_data(trial_data)
                
        except Exception as e:
            return {
                'trial_id': trial_data.get('id', ''),
                'title': trial_data.get('title', 'Unknown'),
                'analysis': f"Analysis failed: {str(e)}",
                'metadata': {
                    'phase': 'Unknown',
                    'status': 'Unknown',
                    'sponsor': 'Unknown'
                }
            }
    
    def _analyze_clinical_trial(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze clinical trial data."""
        protocol_section = trial_data.get('protocolSection', {})
        identification = protocol_section.get('identificationModule', {})
        status = protocol_section.get('statusModule', {})
        sponsor = protocol_section.get('sponsorCollaboratorsModule', {})
        
        title = identification.get('briefTitle', '')
        status_text = status.get('overallStatus', '')
        sponsor_name = sponsor.get('leadSponsor', {}).get('name', '')
        
        # Extract phase information
        phase_info = protocol_section.get('phaseModule', {})
        phase = phase_info.get('phase', 'Unknown')
        
        # Create analysis prompt for clinical trials
        prompt = f"""
        Analyze this clinical trial and provide strategic insights:
        
        Trial Title: {title}
        Sponsor: {sponsor_name}
        Phase: {phase}
        Status: {status_text}
        
        Please provide analysis covering:
        1. Therapeutic focus and market potential
        2. Competitive positioning
        3. Development risks and opportunities
        4. Strategic implications
        
        Focus on business and competitive intelligence insights.
        """
        
        try:
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
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
            return {
                'trial_id': identification.get('nctId', ''),
                'title': title,
                'analysis': f"Analysis failed: {str(e)}",
                'metadata': {
                    'phase': phase,
                    'status': status_text,
                    'sponsor': sponsor_name
                }
            }
    
    def _analyze_pubmed_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PubMed article data."""
        title = article_data.get('title', '')
        abstract = article_data.get('abstract', '')
        authors = article_data.get('authors', [])
        journal = article_data.get('journal', '')
        publication_date = article_data.get('publication_date', '')
        
        # Create analysis prompt for PubMed articles
        prompt = f"""
        Analyze this scientific publication and provide competitive intelligence insights:
        
        Title: {title}
        Journal: {journal}
        Publication Date: {publication_date}
        Authors: {', '.join(authors) if authors else 'Unknown'}
        Abstract: {abstract}
        
        Please provide analysis covering:
        1. Scientific significance and therapeutic implications
        2. Market and competitive landscape insights
        3. Technology and innovation assessment
        4. Strategic opportunities and risks
        
        Focus on business and competitive intelligence insights from the scientific research.
        """
        
        try:
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            return {
                'trial_id': article_data.get('pmid', ''),
                'title': title,
                'analysis': response.text,
                'metadata': {
                    'phase': 'Research',
                    'status': 'Published',
                    'sponsor': journal
                }
            }
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                # Rate limit exceeded - set global flag and fail
                global AI_RATE_LIMIT_HIT
                AI_RATE_LIMIT_HIT = True
                raise Exception(f"API rate limit exceeded: {error_msg}")
            else:
                raise e
    
    def _analyze_fda_data(self, fda_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze FDA data."""
        title = fda_data.get('title', '')
        description = fda_data.get('description', '')
        data_type = fda_data.get('data_type', '')
        
        # Create analysis prompt for FDA data
        prompt = f"""
        Analyze this FDA regulatory data and provide competitive intelligence insights:
        
        Title: {title}
        Data Type: {data_type}
        Description: {description}
        
        Please provide analysis covering:
        1. Regulatory implications and market impact
        2. Competitive positioning and market dynamics
        3. Risk assessment and strategic considerations
        4. Business opportunities and challenges
        
        Focus on business and competitive intelligence insights from the regulatory data.
        """
        
        try:
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            return {
                'trial_id': fda_data.get('id', ''),
                'title': title,
                'analysis': response.text,
                'metadata': {
                    'phase': 'Regulatory',
                    'status': data_type,
                    'sponsor': 'FDA'
                }
            }
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                # Rate limit exceeded - set global flag and fail
                global AI_RATE_LIMIT_HIT
                AI_RATE_LIMIT_HIT = True
                raise Exception(f"API rate limit exceeded: {error_msg}")
            else:
                raise e
    
    def _analyze_generic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze generic data with unknown structure."""
        title = data.get('title', '')
        description = data.get('description', data.get('abstract', ''))
        
        prompt = f"""
        Analyze this data and provide competitive intelligence insights:
        
        Title: {title}
        Description: {description}
        
        Please provide analysis covering:
        1. Market and competitive implications
        2. Strategic opportunities and risks
        3. Business intelligence insights
        
        Focus on extracting competitive intelligence from the available information.
        """
        
        try:
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            return {
                'trial_id': data.get('id', ''),
                'title': title,
                'analysis': response.text,
                'metadata': {
                    'phase': 'Unknown',
                    'status': 'Unknown',
                    'sponsor': 'Unknown'
                }
            }
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                # Rate limit exceeded - set global flag and fail
                global AI_RATE_LIMIT_HIT
                AI_RATE_LIMIT_HIT = True
                raise Exception(f"API rate limit exceeded: {error_msg}")
            else:
                raise e
    
    def _analyze_trial_fallback(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available."""
        data_source = trial_data.get('data_source', 'unknown')
        title = trial_data.get('title', '')
        
        if data_source == 'pubmed':
            return {
                'trial_id': trial_data.get('pmid', ''),
                'title': title,
                'analysis': f"Basic analysis: PubMed article '{title}' published in {trial_data.get('journal', 'Unknown')}. AI analysis not available.",
                'metadata': {
                    'phase': 'Research',
                    'status': 'Published',
                    'sponsor': trial_data.get('journal', 'Unknown')
                }
            }
        elif data_source == 'fda':
            return {
                'trial_id': trial_data.get('id', ''),
                'title': title,
                'analysis': f"Basic analysis: FDA data '{title}' of type {trial_data.get('data_type', 'Unknown')}. AI analysis not available.",
                'metadata': {
                    'phase': 'Regulatory',
                    'status': trial_data.get('data_type', 'Unknown'),
                    'sponsor': 'FDA'
                }
            }
        else:
            return {
                'trial_id': trial_data.get('id', ''),
                'title': title,
                'analysis': f"Basic analysis: Data record '{title}' from {data_source}. AI analysis not available.",
                'metadata': {
                    'phase': 'Unknown',
                    'status': 'Unknown',
                    'sponsor': 'Unknown'
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
        Generate a summary of the competitive landscape based on multiple data analyses.
        
        Args:
            analyses: List of analysis results from different data sources
            
        Returns:
            String containing the landscape summary
        """
        if not GEMINI_AVAILABLE:
            raise Exception("Gemini AI not available for landscape summary generation")
            
        try:
            # Get model name from config
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            
            # Prepare context from analyses, filtering out failed analyses
            valid_analyses = []
            for analysis in analyses:
                if analysis.get('title') and analysis.get('analysis'):
                    # Check if it's a valid analysis (not a rate limit error)
                    analysis_text = analysis.get('analysis', '')
                    if not analysis_text.startswith('Analysis failed:') and not '429' in analysis_text:
                        valid_analyses.append(analysis)
            
            if not valid_analyses:
                raise Exception("No valid analyses available for summary generation. All analyses failed due to API rate limits or other errors.")
            
            # Extract key information for structured analysis
            data_info = []
            data_sources = set()
            sponsors = set()
            phases = set()
            statuses = set()
            
            for analysis in valid_analyses:
                title = analysis.get('title', 'Unknown')
                sponsor = analysis.get('metadata', {}).get('sponsor', 'Unknown')
                phase = analysis.get('metadata', {}).get('phase', 'Unknown')
                status = analysis.get('metadata', {}).get('status', 'Unknown')
                
                # Determine data source from metadata
                data_source = 'Unknown'
                if phase == 'Research' and status == 'Published':
                    data_source = 'PubMed'
                elif sponsor == 'FDA':
                    data_source = 'FDA'
                elif phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
                    data_source = 'Clinical Trials'
                else:
                    data_source = 'Other'
                
                data_info.append(f"Source: {data_source} | Title: {title} | Sponsor: {sponsor} | Phase: {phase} | Status: {status}")
                data_sources.add(data_source)
                sponsors.add(sponsor)
                phases.add(phase)
                statuses.add(status)
            
            context = "\n".join(data_info)
            
            prompt = f"""
            Based on the following multi-source data analysis, provide a comprehensive competitive intelligence summary:
            
            DATA SOURCES ANALYZED:
            {context}
            
            ANALYSIS CONTEXT:
            Total records: {len(valid_analyses)}
            Data sources: {', '.join(data_sources)}
            Unique sponsors: {len(sponsors)}
            Phases represented: {', '.join(phases)}
            Status distribution: {', '.join(statuses)}
            
            CRITICAL INSTRUCTIONS:
            - ONLY use the data provided above. Do not reference any external information, dates, or facts not present in the data.
            - Do not include any headers like "Date:", "Prepared For:", or similar report metadata.
            - Do not add any information that is not directly derived from the provided data.
            - Do not reference specific dates, companies, or facts not explicitly mentioned in the data.
            - Focus strictly on analyzing the provided multi-source information.
            - Use clear, readable formatting with proper headers and bullet points.
            
            Please provide a detailed competitive landscape analysis with the following structure:
            
            # Executive Summary
            
            Provide a 3-4 paragraph executive summary covering:
            - Overall market dynamics and competitive intensity based on the data sources
            - Key therapeutic areas and indications being targeted
            - Most significant developments and emerging trends
            - Market maturity and growth potential assessment
            
            # Competitive Analysis
            
            Analyze the competitive landscape including:
            - Major pharmaceutical companies and their strategic focus
            - Pipeline depth and breadth by company
            - Most advanced drug candidates and their competitive positioning
            - Emerging players and disruptive technologies
            
            # Market Opportunities
            
            Identify key opportunities including:
            - Underserved therapeutic areas
            - Partnership and collaboration opportunities
            - Investment priorities and strategic recommendations
            - Regulatory and market access considerations
            
            # Risk Assessment
            
            Evaluate potential risks including:
            - Competitive threats and challenges
            - Clinical development risks
            - Market entry barriers
            - Regulatory and reimbursement challenges
            
            Format the content with clear headers, bullet points, and professional language.
            Focus on strategic implications and business opportunities.
            ONLY use information that is directly derived from the provided data.
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                # Rate limit exceeded - set global flag and fail
                global AI_RATE_LIMIT_HIT
                AI_RATE_LIMIT_HIT = True
                raise Exception(f"API rate limit exceeded during landscape summary generation: {error_msg}")
            else:
                raise e 