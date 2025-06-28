#!/usr/bin/env python3
"""
Research Interface Module

This module handles interactive user input for research topics and drug pipeline research.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from .keyword_generator import KeywordGenerator

logger = logging.getLogger(__name__)

class ResearchInterface:
    """Handles interactive research topic input and configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the research interface."""
        self.config = config
        self.keyword_generator = KeywordGenerator(config)
        
    def get_research_input(self) -> Tuple[str, str, str, str]:
        """
        Get research input from user in a streamlined way.
        
        Returns:
            Tuple of (research_topic, research_type, drug_name, indication)
        """
        print("\n" + "="*60)
        print("STRATEGIX AGENT - RESEARCH INPUT")
        print("="*60)
        print("\nPlease enter your research topic or drug pipeline of interest.")
        print("Examples:")
        print("- 'PD-1 inhibitors in lung cancer' (general topic)")
        print("- 'Keytruda' (drug pipeline - will ask for indication)")
        print("- 'Alzheimer's disease treatments' (general topic)")
        print("- 'Novo Nordisk diabetes pipeline' (company pipeline)")
        print()
        
        while True:
            topic = input("Research Topic: ").strip()
            if not topic:
                print("❌ Please enter a valid research topic.")
                continue
                
            print(f"\n✓ Research topic: {topic}")
            
            # Determine if this looks like a drug pipeline or general topic
            topic_lower = topic.lower()
            
            # Check if it looks like a drug pipeline
            pipeline_indicators = [
                'pipeline', 'drug', 'therapy', 'treatment', 'inhibitor', 
                'antibody', 'vaccine', 'cell', 'gene', 'protein', 'mab', 'nib'
            ]
            
            # Common drug name patterns
            drug_patterns = [
                'keytruda', 'humira', 'ozempic', 'wegovy', 'eliquis', 'xarelto',
                'pembrolizumab', 'nivolumab', 'atezolizumab', 'durvalumab',
                'rituximab', 'trastuzumab', 'bevacizumab', 'adalimumab',
                'infliximab', 'etanercept', 'ustekinumab', 'secukinumab',
                'dupilumab', 'guselkumab', 'risankizumab', 'tildrakizumab'
            ]
            
            # Check if it's a known drug name
            is_known_drug = any(drug in topic_lower for drug in drug_patterns)
            
            # Check if it contains pipeline indicators
            has_pipeline_indicators = any(indicator in topic_lower for indicator in pipeline_indicators)
            
            # Determine if it's likely a drug pipeline
            is_likely_pipeline = is_known_drug or has_pipeline_indicators
            
            if is_likely_pipeline:
                if is_known_drug:
                    print(f"🔍 This appears to be a drug name: {topic}")
                else:
                    print(f"🔍 This looks like a drug pipeline topic.")
                    
                choice = input("Is this a specific drug/drug pipeline? (y/n): ").strip().lower()
                
                if choice in ['y', 'yes']:
                    # Extract drug name from topic
                    drug_name = topic
                    
                    # Ask for indication
                    print(f"\n💊 Drug/Pipeline: {drug_name}")
                    indication = input("Target indication/disease area (optional): ").strip()
                    
                    if indication:
                        print(f"✓ Indication: {indication}")
                    else:
                        print("✓ Indication: Not specified")
                        
                    return topic, "pipeline", drug_name, indication
                else:
                    # Treat as general topic
                    return topic, "topic", "", ""
            else:
                # Treat as general topic
                return topic, "topic", "", ""
                
    def generate_research_config(self, research_topic: str, research_type: str, drug_name: str = "", indication: str = "") -> Dict[str, Any]:
        """
        Generate research configuration based on user input.
        
        Args:
            research_topic: The research topic provided by the user
            research_type: Type of research ('topic' or 'pipeline')
            drug_name: Name of the drug (for pipeline research)
            indication: Target indication (for pipeline research)
            
        Returns:
            Dictionary containing research configuration
        """
        if research_type == "pipeline":
            keywords = self.keyword_generator.generate_drug_pipeline_keywords(drug_name, indication)
            research_name = f"{drug_name} Pipeline"
            if indication:
                research_name += f" - {indication}"
        else:
            keywords = self.keyword_generator.generate_keywords_ai(research_topic)
            research_name = research_topic
            
        # Create research configuration
        research_config = {
            "name": research_name,
            "keywords": keywords,
            "research_type": research_type,
            "original_topic": research_topic
        }
        
        if research_type == "pipeline":
            research_config["drug_name"] = drug_name
            research_config["indication"] = indication
            
        # Display generated keywords
        print(f"\n🔍 Generated {len(keywords)} keywords for search:")
        for i, keyword in enumerate(keywords, 1):
            print(f"  {i:2d}. {keyword}")
            
        return research_config
        
    def confirm_research_config(self, research_config: Dict[str, Any]) -> bool:
        """
        Ask user to confirm the research configuration.
        
        Args:
            research_config: The generated research configuration
            
        Returns:
            True if user confirms, False otherwise
        """
        print(f"\n📋 Research Configuration Summary:")
        print(f"   Topic: {research_config['name']}")
        print(f"   Type: {research_config['research_type'].title()}")
        print(f"   Keywords: {len(research_config['keywords'])} generated")
        
        if research_config['research_type'] == 'pipeline':
            print(f"   Drug: {research_config['drug_name']}")
            if research_config['indication']:
                print(f"   Indication: {research_config['indication']}")
                
        print("\nProceed with this configuration?")
        while True:
            choice = input("Enter 'y' to continue or 'n' to restart: ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' or 'n'.")
                
    def get_interactive_research_config(self) -> Dict[str, Any]:
        """
        Get complete research configuration through streamlined interactive input.
        
        Returns:
            Dictionary containing the complete research configuration
        """
        while True:
            # Get research input (topic, type, drug, indication)
            research_topic, research_type, drug_name, indication = self.get_research_input()
            
            # Generate configuration
            research_config = self.generate_research_config(research_topic, research_type, drug_name, indication)
            
            # Confirm configuration
            if self.confirm_research_config(research_config):
                return research_config
            else:
                print("\n🔄 Restarting research configuration...")
                continue 