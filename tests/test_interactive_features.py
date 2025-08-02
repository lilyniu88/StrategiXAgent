#!/usr/bin/env python3
"""
Test script for the new interactive features of StrategiX Agent.
This script demonstrates the keyword generation and research configuration
without requiring user input.
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from unittest.mock import patch

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor.keyword_generator import KeywordGenerator
from data_processor.research_interface import ResearchInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keyword_generation():
    """Test the keyword generation functionality."""
    print("🧪 Testing Keyword Generation")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    # Initialize keyword generator
    keyword_gen = KeywordGenerator(config)
    
    # Test cases
    test_topics = [
        "PD-1 inhibitors in lung cancer",
        "Alzheimer's disease treatments", 
        "mRNA vaccines for infectious diseases",
        "CAR-T cell therapy"
    ]
    
    for topic in test_topics:
        print(f"\n📝 Research Topic: {topic}")
        keywords = keyword_gen.generate_keywords_ai(topic)
        print(f"🔍 Generated Keywords ({len(keywords)}):")
        for i, keyword in enumerate(keywords, 1):
            print(f"  {i:2d}. {keyword}")
    
    # Test drug pipeline keywords
    print(f"\n💊 Testing Drug Pipeline Keywords")
    print("-" * 30)
    drug_keywords = keyword_gen.generate_drug_pipeline_keywords("Keytruda", "lung cancer")
    print(f"Drug: Keytruda, Indication: lung cancer")
    print(f"Generated Keywords ({len(drug_keywords)}):")
    for i, keyword in enumerate(drug_keywords, 1):
        print(f"  {i:2d}. {keyword}")

def test_research_config_generation():
    """Test research configuration generation."""
    print(f"\n\n🧪 Testing Research Configuration Generation")
    print("=" * 60)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    # Initialize research interface
    research_interface = ResearchInterface(config)
    
    # Test research configuration generation
    test_cases = [
        ("PD-1 inhibitors in lung cancer", "topic", "", ""),
        ("Keytruda", "pipeline", "Keytruda", "lung cancer")
    ]
    
    for topic, research_type, drug_name, indication in test_cases:
        print(f"\n📋 Test Case: {topic} ({research_type})")
        print("-" * 40)
        
        research_config = research_interface.generate_research_config(topic, research_type, drug_name, indication)
            
        print(f"Research Name: {research_config['name']}")
        print(f"Research Type: {research_config['research_type']}")
        print(f"Original Topic: {research_config['original_topic']}")
        print(f"Keywords: {len(research_config['keywords'])} generated")
        
        if research_type == "pipeline":
            print(f"Drug: {research_config.get('drug_name', 'N/A')}")
            print(f"Indication: {research_config.get('indication', 'N/A')}")

def test_streamlined_input():
    """Test the new streamlined input process."""
    print(f"\n\n🧪 Testing Streamlined Input Process")
    print("=" * 60)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    # Initialize research interface
    research_interface = ResearchInterface(config)
    
    # Test cases with mocked input
    test_scenarios = [
        # (input_topic, is_pipeline_choice, indication, expected_type)
        ("Keytruda", "y", "lung cancer", "pipeline"),
        ("PD-1 inhibitors in lung cancer", "n", "", "topic"),
        ("Alzheimer's disease treatments", "n", "", "topic")
    ]
    
    for input_topic, pipeline_choice, indication, expected_type in test_scenarios:
        print(f"\n📋 Test Scenario: {input_topic}")
        print("-" * 40)
        
        # Mock the user input
        if expected_type == "pipeline":
            with patch('builtins.input', side_effect=[input_topic, pipeline_choice, indication]):
                topic, research_type, drug_name, indication_result = research_interface.get_research_input()
        else:
            with patch('builtins.input', side_effect=[input_topic, pipeline_choice]):
                topic, research_type, drug_name, indication_result = research_interface.get_research_input()
        
        print(f"Input Topic: {topic}")
        print(f"Research Type: {research_type}")
        print(f"Drug Name: {drug_name}")
        print(f"Indication: {indication_result}")
        print(f"Expected Type: {expected_type}")
        print(f"✅ {'PASS' if research_type == expected_type else 'FAIL'}")

def test_drug_pipeline_examples():
    """Test various drug pipeline examples."""
    print(f"\n\n💊 Testing Drug Pipeline Examples")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    # Initialize keyword generator
    keyword_gen = KeywordGenerator(config)
    
    # Example drug pipeline cases
    drug_examples = [
        ("Keytruda", "lung cancer"),
        ("Humira", "rheumatoid arthritis"),
        ("Ozempic", "diabetes"),
        ("CAR-T cell therapy", "lymphoma"),
        ("mRNA vaccine", "COVID-19"),
        ("Novo Nordisk pipeline", "obesity"),
        ("Pfizer oncology", "breast cancer"),
        ("Biogen neurology", "Alzheimer's disease")
    ]
    
    for drug_name, indication in drug_examples:
        print(f"\n💊 Drug: {drug_name}")
        print(f"🎯 Indication: {indication}")
        keywords = keyword_gen.generate_drug_pipeline_keywords(drug_name, indication)
        print(f"🔍 Generated Keywords ({len(keywords)}):")
        for i, keyword in enumerate(keywords[:10], 1):  # Show first 10 keywords
            print(f"  {i:2d}. {keyword}")
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more keywords")

def main():
    """Run all tests."""
    print("🚀 StrategiX Agent - Interactive Features Test")
    print("=" * 60)
    
    try:
        # Test keyword generation
        test_keyword_generation()
        
        # Test research configuration generation
        test_research_config_generation()
        
        # Test streamlined input process
        test_streamlined_input()
        
        # Test drug pipeline examples
        test_drug_pipeline_examples()
        
        print(f"\n✅ All tests completed successfully!")
        print(f"\n💡 To run the full interactive application:")
        print(f"   python main_optimized.py")
        print(f"\n📋 Example research topics you can try:")
        print(f"   - 'PD-1 inhibitors in lung cancer'")
        print(f"   - 'Keytruda' (will ask if it's a drug pipeline)")
        print(f"   - 'Alzheimer's disease treatments'")
        print(f"   - 'mRNA vaccines for infectious diseases'")
        print(f"   - 'CAR-T cell therapy'")
        print(f"   - 'Novo Nordisk diabetes pipeline'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    main() 