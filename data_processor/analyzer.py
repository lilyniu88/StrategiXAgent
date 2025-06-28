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
                config = yaml.safe_load(file)
            if config is None:
                raise ValueError("Config file is empty or invalid YAML")
            return config
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
            return self._generate_landscape_summary_fallback(analyses)
            
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
            
            # Extract key information for structured analysis
            trial_info = []
            sponsors = set()
            phases = set()
            statuses = set()
            
            for analysis in valid_analyses:
                title = analysis.get('title', 'Unknown')
                sponsor = analysis.get('metadata', {}).get('sponsor', 'Unknown')
                phase = analysis.get('metadata', {}).get('phase', 'Unknown')
                status = analysis.get('metadata', {}).get('status', 'Unknown')
                
                trial_info.append(f"Title: {title} | Sponsor: {sponsor} | Phase: {phase} | Status: {status}")
                sponsors.add(sponsor)
                phases.add(phase)
                statuses.add(status)
            
            context = "\n".join(trial_info)
            
            prompt = f"""
            Based on the following clinical trial data, provide a comprehensive competitive intelligence summary:
            
            TRIAL DATA:
            {context}
            
            ANALYSIS CONTEXT:
            Total trials: {len(valid_analyses)}
            Unique sponsors: {len(sponsors)}
            Phases represented: {', '.join(phases)}
            Status distribution: {', '.join(statuses)}
            
            Please provide a detailed competitive landscape analysis including:
            
            1. EXECUTIVE SUMMARY (3-4 paragraphs):
            - Overall market dynamics and competitive intensity
            - Key therapeutic areas and indications being targeted
            - Most significant developments and emerging trends
            - Market maturity and growth potential assessment
            
            2. COMPETITIVE ANALYSIS:
            - Major pharmaceutical companies and their strategic focus
            - Pipeline depth and breadth by company
            - Most advanced drug candidates and their competitive positioning
            - Emerging players and disruptive technologies
            
            3. MARKET OPPORTUNITIES:
            - Underserved therapeutic areas
            - Partnership and collaboration opportunities
            - Investment priorities and strategic recommendations
            - Regulatory and market access considerations
            
            4. RISK ASSESSMENT:
            - Competitive threats and challenges
            - Clinical development risks
            - Market entry barriers
            - Regulatory and reimbursement challenges
            
            Format as a professional competitive intelligence report with clear sections and actionable insights.
            Focus on strategic implications and business opportunities.
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating landscape summary: {e}")
            return self._generate_landscape_summary_fallback(analyses)
            
    def _generate_landscape_summary_fallback(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Fallback landscape summary generation when AI is not available.
        
        Args:
            analyses: List of trial analysis results
            
        Returns:
            String containing fallback landscape summary
        """
        if not analyses:
            return "No trial analyses available for summary generation."
            
        # Extract key information
        trial_count = len(analyses)
        sponsors = {}
        phases = {}
        statuses = {}
        
        for analysis in analyses:
            sponsor = analysis.get('metadata', {}).get('sponsor', 'Unknown')
            phase = analysis.get('metadata', {}).get('phase', 'Unknown')
            status = analysis.get('metadata', {}).get('status', 'Unknown')
            
            sponsors[sponsor] = sponsors.get(sponsor, 0) + 1
            phases[phase] = phases.get(phase, 0) + 1
            statuses[status] = statuses.get(status, 0) + 1
        
        # Generate insights
        top_sponsors = sorted(sponsors.items(), key=lambda x: x[1], reverse=True)[:5]
        phase_distribution = sorted(phases.items(), key=lambda x: x[1], reverse=True)
        status_distribution = sorted(statuses.items(), key=lambda x: x[1], reverse=True)
        
        summary = f"""
# Competitive Landscape Summary

## Executive Summary
Analysis of {trial_count} clinical trials reveals a dynamic competitive landscape with {len(sponsors)} unique sponsors actively developing therapeutics. The market shows {phase_distribution[0][0] if phase_distribution else 'Unknown'} as the most common development phase, indicating {status_distribution[0][0] if status_distribution else 'Unknown'} as the primary trial status.

## Competitive Analysis
**Top Sponsors by Trial Count:**
"""
        
        for sponsor, count in top_sponsors:
            summary += f"- {sponsor}: {count} trials\n"
            
        summary += f"""
**Phase Distribution:**
"""
        
        for phase, count in phase_distribution:
            summary += f"- {phase}: {count} trials\n"
            
        summary += f"""
**Status Distribution:**
"""
        
        for status, count in status_distribution:
            summary += f"- {status}: {count} trials\n"
            
        summary += f"""
## Market Opportunities
- Monitor {top_sponsors[0][0] if top_sponsors else 'leading sponsors'} for partnership opportunities
- Focus on {phase_distribution[0][0] if phase_distribution else 'most active'} development phases
- Track emerging therapeutic approaches and mechanisms

## Risk Assessment
- Competitive intensity varies by therapeutic area
- Clinical development timelines and success rates
- Regulatory approval pathways and market access

*Note: This is a basic analysis. For detailed AI-powered competitive intelligence, ensure the google-generativeai package is installed and configured.*
"""
        
        return summary

    def analyze_trials(self, trials_data: List[Dict], research_topic: str) -> Dict:
        """
        Analyze clinical trials data using AI to generate competitive intelligence insights.
        
        Args:
            trials_data: List of clinical trial dictionaries
            research_topic: The research topic being analyzed
            
        Returns:
            Dictionary containing analysis results
        """
        if not trials_data:
            return {
                'summary': 'No clinical trials data available for analysis.',
                'key_insights': [],
                'competitive_landscape': {},
                'recommendations': []
            }
            
        if not GEMINI_AVAILABLE:
            return self._analyze_trials_fallback(trials_data, research_topic)
            
        try:
            # Prepare trial summaries for AI analysis
            trial_summaries = []
            for trial in trials_data:
                summary = f"Trial: {trial.get('title', 'N/A')} | "
                summary += f"Phase: {trial.get('phase', 'N/A')} | "
                summary += f"Status: {trial.get('status', 'N/A')} | "
                summary += f"Sponsor: {trial.get('sponsor', 'N/A')} | "
                summary += f"Intervention: {trial.get('intervention', 'N/A')} | "
                summary += f"Condition: {trial.get('condition', 'N/A')}"
                trial_summaries.append(summary)
            
            trials_text = "\n".join(trial_summaries)
            
            # Get model name from config
            model_name = self.config.get('gemini', {}).get('model', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            Analyze the following clinical trials data for competitive intelligence insights about: "{research_topic}"
            
            TRIALS DATA:
            {trials_text}
            
            Provide a comprehensive competitive intelligence analysis including:
            
            1. EXECUTIVE SUMMARY (2-3 paragraphs):
            - Key findings and market dynamics
            - Most significant developments and trends
            - Overall competitive landscape assessment
            
            2. KEY INSIGHTS (5-8 bullet points):
            - Major players and their strategies
            - Promising drug candidates and mechanisms
            - Clinical trial trends and patterns
            - Regulatory and market opportunities
            - Potential competitive advantages
            
            3. COMPETITIVE LANDSCAPE ANALYSIS:
            - Top pharmaceutical companies involved
            - Most advanced drug candidates by phase
            - Emerging therapeutic approaches
            - Geographic distribution of trials
            - Timeline analysis of development stages
            
            4. STRATEGIC RECOMMENDATIONS (3-5 actionable items):
            - Partnership opportunities
            - Investment priorities
            - Competitive positioning strategies
            - Risk assessment and mitigation
            
            Format the response as a structured competitive intelligence report with clear sections.
            Focus on actionable business insights and strategic implications.
            """
            
            response = model.generate_content(prompt)
            analysis_text = response.text.strip()
            
            # Parse the AI response into structured format
            analysis = self._parse_ai_analysis(analysis_text, trials_data, research_topic)
            
            logger.info(f"Generated AI analysis for {len(trials_data)} trials on topic: {research_topic}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trials with AI: {e}")
            return self._analyze_trials_fallback(trials_data, research_topic)
            
    def _parse_ai_analysis(self, analysis_text: str, trials_data: List[Dict], research_topic: str) -> Dict:
        """
        Parse AI-generated analysis text into structured format.
        
        Args:
            analysis_text: Raw AI analysis text
            trials_data: Original trials data for context
            research_topic: The research topic being analyzed
            
        Returns:
            Dictionary containing structured analysis results
        """
        try:
            # Extract key sections from AI response
            sections = {
                'summary': '',
                'key_insights': [],
                'competitive_landscape': {},
                'recommendations': []
            }
            
            # Simple parsing - look for common section headers
            lines = analysis_text.split('\n')
            current_section = 'summary'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect sections
                lower_line = line.lower()
                if 'executive summary' in lower_line or 'summary' in lower_line:
                    current_section = 'summary'
                    continue
                elif 'key insights' in lower_line or 'insights' in lower_line:
                    current_section = 'key_insights'
                    continue
                elif 'competitive landscape' in lower_line or 'landscape' in lower_line:
                    current_section = 'competitive_landscape'
                    continue
                elif 'recommendations' in lower_line or 'strategic' in lower_line:
                    current_section = 'recommendations'
                    continue
                
                # Add content to appropriate section
                if current_section == 'summary':
                    sections['summary'] += line + ' '
                elif current_section == 'key_insights':
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        sections['key_insights'].append(line.lstrip('-•* '))
                elif current_section == 'recommendations':
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        sections['recommendations'].append(line.lstrip('-•* '))
            
            # Clean up summary
            sections['summary'] = sections['summary'].strip()
            
            # If parsing failed, use the full text as summary
            if not sections['summary']:
                sections['summary'] = analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text
            
            # Ensure we have some insights
            if not sections['key_insights']:
                sections['key_insights'] = [
                    f"Analysis completed for {len(trials_data)} trials",
                    f"Research topic: {research_topic}",
                    "AI-generated competitive intelligence insights available"
                ]
            
            if not sections['recommendations']:
                sections['recommendations'] = [
                    "Review detailed analysis for strategic insights",
                    "Monitor key competitors and trial progress",
                    "Consider partnership opportunities identified"
                ]
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing AI analysis: {e}")
            # Return fallback if parsing fails
            return self._analyze_trials_fallback(trials_data, research_topic)
            
    def _analyze_trials_fallback(self, trials_data: List[Dict], research_topic: str) -> Dict:
        """
        Fallback analysis when AI is not available.
        
        Args:
            trials_data: List of clinical trial dictionaries
            research_topic: The research topic being analyzed
            
        Returns:
            Dictionary containing fallback analysis results
        """
        if not trials_data:
            return {
                'summary': 'No clinical trials data available for analysis.',
                'key_insights': [],
                'competitive_landscape': {},
                'recommendations': []
            }
            
        # Extract key information from trials
        sponsors = {}
        phases = {}
        statuses = {}
        interventions = []
        conditions = []
        
        for trial in trials_data:
            # Sponsor analysis
            sponsor = trial.get('sponsor', 'Unknown')
            sponsors[sponsor] = sponsors.get(sponsor, 0) + 1
            
            # Phase analysis
            phase = trial.get('phase', 'Unknown')
            phases[phase] = phases.get(phase, 0) + 1
            
            # Status analysis
            status = trial.get('status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
            
            # Collect interventions and conditions
            intervention = trial.get('intervention', '')
            if intervention and intervention not in interventions:
                interventions.append(intervention)
                
            condition = trial.get('condition', '')
            if condition and condition not in conditions:
                conditions.append(condition)
        
        # Generate insights
        total_trials = len(trials_data)
        top_sponsors = sorted(sponsors.items(), key=lambda x: x[1], reverse=True)[:5]
        phase_distribution = sorted(phases.items(), key=lambda x: x[1], reverse=True)
        status_distribution = sorted(statuses.items(), key=lambda x: x[1], reverse=True)
        
        # Create summary
        summary = f"Analysis of {total_trials} clinical trials related to {research_topic}. "
        summary += f"Top sponsors include: {', '.join([f'{sponsor} ({count})' for sponsor, count in top_sponsors[:3]])}. "
        summary += f"Phase distribution: {', '.join([f'{phase} ({count})' for phase, count in phase_distribution[:3]])}. "
        summary += f"Most common status: {status_distribution[0][0] if status_distribution else 'Unknown'}."
        
        # Generate key insights
        insights = []
        if top_sponsors:
            insights.append(f"Leading sponsor: {top_sponsors[0][0]} with {top_sponsors[0][1]} trials")
        if phase_distribution:
            insights.append(f"Most common phase: {phase_distribution[0][0]} ({phase_distribution[0][1]} trials)")
        if interventions:
            insights.append(f"Key interventions: {', '.join(interventions[:3])}")
        if conditions:
            insights.append(f"Target conditions: {', '.join(conditions[:3])}")
        insights.append(f"Total trials analyzed: {total_trials}")
        
        # Competitive landscape
        landscape = {
            'top_sponsors': dict(top_sponsors),
            'phase_distribution': dict(phase_distribution),
            'status_distribution': dict(status_distribution),
            'key_interventions': interventions[:5],
            'target_conditions': conditions[:5]
        }
        
        # Recommendations
        recommendations = [
            "Monitor top sponsors for partnership opportunities",
            "Focus on most active development phases",
            "Track emerging interventions and mechanisms",
            "Analyze geographic distribution of trials",
            "Assess competitive positioning in target conditions"
        ]
        
        logger.info(f"Generated fallback analysis for {len(trials_data)} trials on topic: {research_topic}")
        
        return {
            'summary': summary,
            'key_insights': insights,
            'competitive_landscape': landscape,
            'recommendations': recommendations
        } 