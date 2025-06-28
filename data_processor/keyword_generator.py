#!/usr/bin/env python3
"""
Keyword Generator Module

This module generates relevant keywords for clinical trial searches based on user-provided
research topics using Google's Gemini AI.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class KeywordGenerator:
    """Generates keywords for clinical trial searches using AI."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the keyword generator with configuration."""
        self.config = config
        self.gemini_config = config.get('gemini', {})
        self.model_name = self.gemini_config.get('model', 'gemini-2.0-flash-exp')
        self.temperature = self.gemini_config.get('temperature', 0.7)
        self.max_tokens = self.gemini_config.get('max_output_tokens', 1024)
        
        # Initialize Gemini AI if available
        self.gemini = self._initialize_gemini()
        
    def _initialize_gemini(self) -> Optional[Any]:
        """Initialize Google Gemini AI client."""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found in environment variables")
                return None
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            logger.info(f"Gemini AI initialized with model: {self.model_name}")
            return model
            
        except ImportError:
            logger.warning("Google Generative AI package not installed. Using fallback keyword generation.")
            return None
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {e}")
            return None
            
    def generate_keywords_ai(self, research_topic: str) -> List[str]:
        """
        Generate keywords using AI for a given research topic.
        
        Args:
            research_topic: The research topic provided by the user
            
        Returns:
            List of generated keywords
        """
        if not self.gemini:
            return self._generate_keywords_fallback(research_topic)
            
        try:
            prompt = f"""
            Generate 10-15 highly specific keywords for searching clinical trials about: "{research_topic}"
            
            Focus on:
            - Drug names and synonyms (e.g., pembrolizumab, Keytruda)
            - Disease subtypes and specific conditions (e.g., NSCLC, HER2-positive)
            - Mechanisms of action (e.g., PD-1 inhibitor, checkpoint inhibitor)
            - Biomarkers and molecular targets (e.g., EGFR, ALK)
            - Clinical endpoints and outcomes (e.g., PFS, OS, ORR)
            - Treatment approaches (e.g., immunotherapy, targeted therapy)
            
            Exclude generic terms like "cancer", "trial", "treatment", "therapy" unless they are part of a specific term.
            
            Return only the keywords as a comma-separated list, no explanations.
            Example format: keyword1, keyword2, keyword3
            """
            
            response = self.gemini.generate_content(prompt)
            keywords_text = response.text.strip()
            
            # Parse the response
            keywords = [kw.strip().lower() for kw in keywords_text.split(',')]
            keywords = [kw for kw in keywords if kw]  # Remove empty strings
            
            # Filter out generic terms
            generic_terms = {
                'cancer', 'tumor', 'disease', 'trial', 'therapy', 'treatment', 
                'drug', 'medication', 'clinical', 'study', 'research', 'patient',
                'medical', 'health', 'care', 'medicine', 'pharmaceutical'
            }
            keywords = [kw for kw in keywords if kw not in generic_terms]
            
            # Ensure we have at least some keywords
            if not keywords:
                keywords = self._generate_keywords_fallback(research_topic)
            
            logger.info(f"Generated {len(keywords)} keywords for topic: {research_topic}")
            return keywords
            
        except Exception as e:
            logger.error(f"Error generating keywords with AI: {e}")
            return self._generate_keywords_fallback(research_topic)
            
    def _generate_keywords_fallback(self, research_topic: str) -> List[str]:
        """
        Fallback keyword generation when AI is not available.
        
        Args:
            research_topic: The research topic provided by the user
            
        Returns:
            List of basic keywords
        """
        topic_lower = research_topic.lower()
        
        # Enhanced keyword mappings for common research areas
        keyword_mappings = {
            # Oncology
            'cancer': {
                'lung': ['nsclc', 'non-small cell lung cancer', 'sclc', 'small cell lung cancer', 'pembrolizumab', 'keytruda', 'nivolumab', 'opdivo', 'atezolizumab', 'tecentriq', 'durvalumab', 'imfinzi', 'checkpoint inhibitor', 'pd-1', 'pd-l1', 'immunotherapy'],
                'breast': ['her2-positive', 'her2-negative', 'triple-negative', 'trastuzumab', 'herceptin', 'pertuzumab', 'perjeta', 'adc', 'antibody-drug conjugate', 'endocrine therapy', 'aromatase inhibitor'],
                'colorectal': ['crc', 'colorectal cancer', 'kras', 'braf', 'msi-high', 'mss', 'cetuximab', 'erbitux', 'bevacizumab', 'avastin', 'regorafenib', 'stivarga'],
                'melanoma': ['braf', 'mek', 'vemurafenib', 'zelboraf', 'dabrafenib', 'tafinlar', 'trametinib', 'mekinist', 'immunotherapy', 'checkpoint inhibitor'],
                'prostate': ['castration-resistant', 'crpc', 'androgen receptor', 'enzalutamide', 'xtandi', 'abiraterone', 'zytiga', 'psa', 'bone metastasis'],
                'leukemia': ['aml', 'all', 'cll', 'cml', 'acute myeloid leukemia', 'chronic lymphocytic leukemia', 'tyrosine kinase inhibitor', 'tki', 'imatinib', 'gleevec', 'dasatinib', 'sprycel'],
                'lymphoma': ['dlbcl', 'diffuse large b-cell lymphoma', 'hodgkin', 'non-hodgkin', 'car-t', 'chimeric antigen receptor', 'cd19', 'rituximab', 'rituxan']
            },
            
            # Neurology
            'alzheimer': ['amyloid beta', 'tau protein', 'cognitive decline', 'aducanumab', 'aduhelm', 'lecanemab', 'lecanemab-irmb', 'donanemab', 'neurodegeneration', 'biomarker', 'pet scan', 'cerebrospinal fluid', 'csf'],
            'parkinson': ['dopamine', 'levodopa', 'carbidopa', 'sinemet', 'deep brain stimulation', 'dbs', 'alpha-synuclein', 'motor symptoms', 'tremor', 'bradykinesia'],
            'multiple sclerosis': ['ms', 'relapsing-remitting', 'rrms', 'progressive', 'interferon beta', 'glatiramer acetate', 'copaxone', 'natalizumab', 'tysabri', 'fingolimod', 'gilenya'],
            
            # Diabetes
            'diabetes': ['type 2 diabetes', 't2dm', 'glp-1', 'glucagon-like peptide', 'sglt2', 'sodium-glucose cotransporter', 'dpp-4', 'dipeptidyl peptidase', 'metformin', 'insulin', 'hba1c', 'glycemic control'],
            
            # Cardiovascular
            'cardiovascular': ['heart failure', 'hfref', 'hfpef', 'reduced ejection fraction', 'preserved ejection fraction', 'ace inhibitor', 'angiotensin receptor blocker', 'arb', 'beta blocker', 'statin', 'aspirin'],
            'hypertension': ['blood pressure', 'systolic', 'diastolic', 'ace inhibitor', 'calcium channel blocker', 'ccb', 'diuretic', 'amlodipine', 'lisinopril'],
            
            # Immunology
            'rheumatoid arthritis': ['ra', 'dmard', 'disease-modifying antirheumatic drug', 'methotrexate', 'adalimumab', 'humira', 'etanercept', 'enbrel', 'infliximab', 'remicade', 'tumor necrosis factor', 'tnf'],
            'psoriasis': ['psa', 'psoriatic arthritis', 'biologic', 'ustekinumab', 'stelara', 'secukinumab', 'cosentyx', 'ixekizumab', 'taltz', 'il-17', 'interleukin-17'],
            
            # Respiratory
            'asthma': ['bronchodilator', 'inhaled corticosteroid', 'ics', 'long-acting beta agonist', 'laba', 'short-acting beta agonist', 'saba', 'feNO', 'fractional exhaled nitric oxide', 'eosinophilic'],
            'copd': ['chronic obstructive pulmonary disease', 'bronchodilator', 'long-acting muscarinic antagonist', 'lama', 'long-acting beta agonist', 'laba', 'triple therapy', 'fev1'],
            
            # Infectious Diseases
            'covid': ['sars-cov-2', 'coronavirus', 'mrna vaccine', 'pfizer', 'moderna', 'johnson & johnson', 'janssen', 'antiviral', 'paxlovid', 'molnupiravir', 'remdesivir', 'viread'],
            'hiv': ['human immunodeficiency virus', 'antiretroviral', 'art', 'protease inhibitor', 'integrase inhibitor', 'nucleoside reverse transcriptase inhibitor', 'nrti', 'prep', 'pep'],
            
            # Rare Diseases
            'cystic fibrosis': ['cf', 'cystic fibrosis transmembrane conductance regulator', 'cftr', 'ivacaftor', 'kalydeco', 'lumacaftor', 'orkambi', 'elexacaftor', 'trikafta', 'sweat chloride'],
            'sickle cell': ['sickle cell disease', 'scd', 'hemoglobin', 'hydroxyurea', 'hydroxycarbamide', 'blood transfusion', 'bone marrow transplant', 'gene therapy', 'crispr']
        }
        
        # Try to match the research topic with known areas
        for area, subcategories in keyword_mappings.items():
            if area in topic_lower:
                if isinstance(subcategories, dict):
                    # Check for specific subcategories
                    for subcategory, keywords in subcategories.items():
                        if subcategory in topic_lower:
                            logger.info(f"Using specific {subcategory} keywords for topic: {research_topic}")
                            return keywords
                    # If no specific subcategory found, return general area keywords
                    general_keywords = []
                    for subcategory, keywords in subcategories.items():
                        general_keywords.extend(keywords[:3])  # Take first 3 from each subcategory
                    logger.info(f"Using general {area} keywords for topic: {research_topic}")
                    return general_keywords[:10]  # Limit to 10 keywords
                elif isinstance(subcategories, list):
                    logger.info(f"Using general {area} keywords for topic: {research_topic}")
                    return subcategories[:12]  # Limit to 12 keywords
                
        # If no match found, create context-specific keywords
        context_keywords = []
        
        # Extract potential drug names (words that look like drug names)
        words = research_topic.split()
        for word in words:
            word_lower = word.lower()
            # Common drug name patterns
            if any(pattern in word_lower for pattern in ['mab', 'nib', 'tinib', 'umab', 'izumab', 'omab', 'umab']):
                context_keywords.append(word_lower)
            elif word_lower in ['keytruda', 'humira', 'ozempic', 'wegovy', 'eliquis', 'xarelto']:
                context_keywords.append(word_lower)
        
        # Add disease-specific terms
        if any(term in topic_lower for term in ['cancer', 'tumor', 'oncology']):
            context_keywords.extend(['clinical trial', 'phase', 'safety', 'efficacy'])
        elif any(term in topic_lower for term in ['diabetes', 'diabetic']):
            context_keywords.extend(['glucose', 'insulin', 'metabolic', 'glycemic'])
        elif any(term in topic_lower for term in ['alzheimer', 'dementia']):
            context_keywords.extend(['cognitive', 'memory', 'amyloid', 'tau'])
        elif any(term in topic_lower for term in ['arthritis', 'inflammatory']):
            context_keywords.extend(['inflammation', 'immune', 'autoimmune'])
        
        # Add the original topic as a keyword
        context_keywords.append(research_topic.lower())
        
        # Remove duplicates and limit length
        context_keywords = list(set(context_keywords))
        context_keywords = [kw for kw in context_keywords if len(kw) > 2]  # Remove very short terms
        
        logger.info(f"Using context-specific keywords for topic: {research_topic}")
        return context_keywords[:12]  # Limit to 12 keywords
        
    def generate_drug_pipeline_keywords(self, drug_name: str, indication: str = "") -> List[str]:
        """
        Generate keywords specifically for drug pipeline research.
        
        Args:
            drug_name: Name of the drug or drug class
            indication: Target indication or disease area
            
        Returns:
            List of drug pipeline specific keywords
        """
        base_keywords = [
            drug_name.lower(),
            'clinical trial',
            'phase',
            'safety',
            'efficacy',
            'pharmacokinetics',
            'pharmacodynamics',
            'dose',
            'administration'
        ]
        
        if indication:
            base_keywords.extend([
                indication.lower(),
                'treatment',
                'therapy'
            ])
            
        # Add drug-specific terms
        drug_keywords = [
            'mechanism of action',
            'target',
            'receptor',
            'pathway',
            'biomarker',
            'endpoint',
            'outcome',
            'adverse event',
            'side effect',
            'tolerability'
        ]
        
        all_keywords = base_keywords + drug_keywords
        
        logger.info(f"Generated {len(all_keywords)} drug pipeline keywords for {drug_name}")
        return all_keywords 