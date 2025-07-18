#!/usr/bin/env python3
"""
Test script to demonstrate improved AI prompts and enhanced fallback logic.
"""

import os
import sys
import yaml
from typing import Dict, List, Any

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor.keyword_generator import KeywordGenerator
from data_processor.analyzer import ClinicalTrialAnalyzer

def test_keyword_generation():
    """Test the improved keyword generation with specific prompts."""
    print("🔍 Testing Improved Keyword Generation")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    generator = KeywordGenerator(config)
    
    # Test cases for different research topics
    test_topics = [
        "pembrolizumab in NSCLC",
        "HER2-positive breast cancer",
        "Alzheimer's disease treatment",
        "Type 2 diabetes management",
        "Rheumatoid arthritis biologics",
        "Cystic fibrosis gene therapy",
        "COVID-19 vaccine development",
        "Unknown therapeutic area"
    ]
    
    for topic in test_topics:
        print(f"\n📋 Research Topic: {topic}")
        keywords = generator.generate_keywords_ai(topic)
        print(f"Generated Keywords ({len(keywords)}): {', '.join(keywords)}")
        
        # Test fallback logic
        fallback_keywords = generator._generate_keywords_fallback(topic)
        print(f"Fallback Keywords ({len(fallback_keywords)}): {', '.join(fallback_keywords)}")

def test_analysis_prompts():
    """Test the improved analysis prompts and fallback logic."""
    print("\n\n📊 Testing Improved Analysis Prompts")
    print("=" * 50)
    
    analyzer = ClinicalTrialAnalyzer("config.yaml")
    
    # Mock trial data for testing
    mock_trials = [
        {
            'title': 'Study of Pembrolizumab in Advanced NSCLC',
            'phase': 'Phase 3',
            'status': 'Recruiting',
            'sponsor': 'Merck Sharp & Dohme LLC',
            'intervention': 'Pembrolizumab',
            'condition': 'Non-Small Cell Lung Cancer'
        },
        {
            'title': 'Atezolizumab Plus Chemotherapy in NSCLC',
            'phase': 'Phase 2',
            'status': 'Active, not recruiting',
            'sponsor': 'Genentech, Inc.',
            'intervention': 'Atezolizumab + Carboplatin + Pemetrexed',
            'condition': 'Non-Small Cell Lung Cancer'
        },
        {
            'title': 'Durvalumab Maintenance in NSCLC',
            'phase': 'Phase 3',
            'status': 'Completed',
            'sponsor': 'AstraZeneca',
            'intervention': 'Durvalumab',
            'condition': 'Non-Small Cell Lung Cancer'
        }
    ]
    
    # Test the new analyze_trials method
    print("\n🔬 Testing AI Analysis with Specific Prompts")
    research_topic = "PD-1/PD-L1 inhibitors in NSCLC"
    analysis = analyzer.analyze_trials(mock_trials, research_topic)
    
    print(f"Research Topic: {research_topic}")
    print(f"Summary: {analysis.get('summary', 'No summary available')[:200]}...")
    print(f"Key Insights: {len(analysis.get('key_insights', []))} insights generated")
    print(f"Recommendations: {len(analysis.get('recommendations', []))} recommendations")
    
    # Test fallback analysis
    print("\n🔄 Testing Fallback Analysis Logic")
    fallback_analysis = analyzer._analyze_trials_fallback(mock_trials, research_topic)
    
    print(f"Fallback Summary: {fallback_analysis.get('summary', 'No summary available')[:200]}...")
    print(f"Fallback Insights: {len(fallback_analysis.get('key_insights', []))} insights")
    print(f"Fallback Recommendations: {len(fallback_analysis.get('recommendations', []))} recommendations")

def test_landscape_summary():
    """Test the improved landscape summary generation."""
    print("\n\n📈 Testing Improved Landscape Summary")
    print("=" * 50)
    
    analyzer = ClinicalTrialAnalyzer("config.yaml")
    
    # Mock analyses for testing
    mock_analyses = [
        {
            'title': 'Study of Pembrolizumab in Advanced NSCLC',
            'analysis': 'Promising immunotherapy approach with strong safety profile',
            'metadata': {
                'sponsor': 'Merck Sharp & Dohme LLC',
                'phase': 'Phase 3',
                'status': 'Recruiting'
            }
        },
        {
            'title': 'Atezolizumab Plus Chemotherapy in NSCLC',
            'analysis': 'Combination therapy showing synergistic effects',
            'metadata': {
                'sponsor': 'Genentech, Inc.',
                'phase': 'Phase 2',
                'status': 'Active, not recruiting'
            }
        },
        {
            'title': 'Durvalumab Maintenance in NSCLC',
            'analysis': 'Maintenance therapy demonstrating survival benefits',
            'metadata': {
                'sponsor': 'AstraZeneca',
                'phase': 'Phase 3',
                'status': 'Completed'
            }
        }
    ]
    
    # Test landscape summary generation
    print("\n🌐 Testing AI Landscape Summary")
    summary = analyzer.generate_landscape_summary(mock_analyses)
    print(f"Summary Length: {len(summary)} characters")
    print(f"Summary Preview: {summary[:300]}...")
    
    # Test fallback landscape summary
    print("\n🔄 Testing Fallback Landscape Summary")
    fallback_summary = analyzer._generate_landscape_summary_fallback(mock_analyses)
    print(f"Fallback Summary Length: {len(fallback_summary)} characters")
    print(f"Fallback Summary Preview: {fallback_summary[:300]}...")

def test_specificity_improvements():
    """Test the specificity improvements in prompts."""
    print("\n\n🎯 Testing Specificity Improvements")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    generator = KeywordGenerator(config)
    
    # Test very specific research topics
    specific_topics = [
        "BRAF V600E mutation in melanoma",
        "EGFR exon 19 deletion in NSCLC",
        "HER2-positive metastatic breast cancer",
        "KRAS G12C mutation in colorectal cancer",
        "ALK fusion in lung adenocarcinoma"
    ]
    
    for topic in specific_topics:
        print(f"\n🎯 Specific Topic: {topic}")
        keywords = generator.generate_keywords_ai(topic)
        print(f"Specific Keywords: {', '.join(keywords)}")
        
        # Check for specific terms
        specific_terms = [kw for kw in keywords if any(term in kw.lower() for term in ['braf', 'egfr', 'her2', 'kras', 'alk', 'v600e', 'g12c', 'exon'])]
        print(f"Molecular/Target Terms: {', '.join(specific_terms)}")

def main():
    """Run all tests."""
    print("🚀 Testing Improved AI Prompts and Fallback Logic")
    print("=" * 60)
    
    try:
        # Test keyword generation improvements
        test_keyword_generation()
        
        # Test analysis prompt improvements
        test_analysis_prompts()
        
        # Test landscape summary improvements
        test_landscape_summary()
        
        # Test specificity improvements
        test_specificity_improvements()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary of Improvements:")
        print("- More specific AI prompts for keyword generation")
        print("- Enhanced fallback logic with context-sensitive keywords")
        print("- Improved analysis prompts with structured competitive intelligence")
        print("- Better fallback analysis with detailed insights")
        print("- Enhanced landscape summary with professional formatting")
        print("- Specific molecular and target-based keyword generation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 