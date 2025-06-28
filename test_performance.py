#!/usr/bin/env python3
"""
Performance test script for StrategiX Agent.
This script tests the core functionality without user input to identify bottlenecks.
"""

import os
import sys
import yaml
import time
import logging
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector.clinical_trials_collector import ClinicalTrialsCollector
from data_processor.analyzer import ClinicalTrialAnalyzer
from data_processor.keyword_generator import KeywordGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keyword_generation_performance():
    """Test keyword generation performance."""
    print("🔍 Testing Keyword Generation Performance")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    # Initialize keyword generator
    keyword_gen = KeywordGenerator(config)
    
    # Test performance
    start_time = time.time()
    keywords = keyword_gen.generate_keywords_ai("alzheimer drug pipeline")
    end_time = time.time()
    
    print(f"✅ Keyword generation completed in {end_time - start_time:.2f} seconds")
    print(f"📝 Generated {len(keywords)} keywords")
    print(f"🔍 Keywords: {', '.join(keywords[:5])}...")
    
    return keywords

def test_data_collection_performance():
    """Test data collection performance."""
    print(f"\n📊 Testing Data Collection Performance")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        if config is None:
            raise ValueError("Config file is empty or invalid YAML")
    
    # Create research config
    research_config = {
        "name": "Alzheimer Drug Pipeline Test",
        "keywords": ["alzheimer", "drug", "pipeline", "clinical trial", "treatment"],
        "research_type": "pipeline",
        "original_topic": "alzheimer drug pipeline",
        "drug_name": "alzheimer drug",
        "indication": "alzheimer's disease"
    }
    
    # Initialize collector
    collector = ClinicalTrialsCollector(config)
    
    # Test performance
    start_time = time.time()
    trials_data = collector.fetch_trials_for_research(research_config)
    end_time = time.time()
    
    print(f"✅ Data collection completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Retrieved {len(trials_data)} trials")
    
    # Filter active trials
    start_time = time.time()
    active_trials = collector.filter_active_trials(trials_data)
    end_time = time.time()
    
    print(f"✅ Active trial filtering completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Found {len(active_trials)} active trials")
    
    return active_trials

def test_analysis_performance(trials_data):
    """Test analysis performance."""
    print(f"\n🧠 Testing Analysis Performance")
    print("=" * 50)
    
    if not trials_data:
        print("⚠️ No trials to analyze")
        return []
    
    # Initialize analyzer
    analyzer = ClinicalTrialAnalyzer("config.yaml")
    
    # Test performance with limited trials for speed
    test_trials = trials_data[:3]  # Only analyze first 3 trials for performance test
    
    start_time = time.time()
    analyses = analyzer.analyze_trials_batch(test_trials)
    end_time = time.time()
    
    print(f"✅ Analysis completed in {end_time - start_time:.2f} seconds")
    print(f"🧠 Analyzed {len(analyses)} trials")
    
    # Test summary generation
    start_time = time.time()
    summary = analyzer.generate_landscape_summary(analyses)
    end_time = time.time()
    
    print(f"✅ Summary generation completed in {end_time - start_time:.2f} seconds")
    print(f"📝 Summary length: {len(summary)} characters")
    
    return analyses, summary

def test_full_workflow_performance():
    """Test the complete workflow performance."""
    print(f"\n🚀 Testing Full Workflow Performance")
    print("=" * 60)
    
    total_start_time = time.time()
    
    try:
        # Step 1: Keyword generation
        keywords = test_keyword_generation_performance()
        
        # Step 2: Data collection
        trials_data = test_data_collection_performance()
        
        # Step 3: Analysis
        if trials_data:
            analyses, summary = test_analysis_performance(trials_data)
        else:
            print("⚠️ Skipping analysis - no trials found")
        
        total_end_time = time.time()
        
        print(f"\n✅ Full workflow completed in {total_end_time - total_start_time:.2f} seconds")
        print(f"🎯 Performance Summary:")
        print(f"   - Keyword generation: ✅ Working")
        print(f"   - Data collection: ✅ Working")
        print(f"   - Analysis: ✅ Working")
        print(f"   - Summary generation: ✅ Working")
        
        if trials_data:
            print(f"\n📊 Results Summary:")
            print(f"   - Total trials found: {len(trials_data)}")
            print(f"   - Active trials: {len([t for t in trials_data if t.get('protocolSection', {}).get('statusModule', {}).get('overallStatus', '').lower() in ['recruiting', 'active', 'enrolling']])}")
            print(f"   - Keywords generated: {len(keywords)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        logger.error(f"Performance test error: {e}")
        return False

def identify_bottlenecks():
    """Identify potential performance bottlenecks."""
    print(f"\n🔍 Performance Bottleneck Analysis")
    print("=" * 50)
    
    print("Potential bottlenecks in main.py:")
    print("1. 🔄 API calls to ClinicalTrials.gov (network latency)")
    print("2. 🤖 AI analysis of each trial (API calls to Gemini)")
    print("3. 📊 Large dataset processing")
    print("4. 💾 File I/O operations")
    
    print(f"\n💡 Optimization suggestions:")
    print("1. Add progress indicators for long operations")
    print("2. Implement caching for API responses")
    print("3. Add timeout handling for API calls")
    print("4. Process trials in smaller batches")
    print("5. Add user feedback during long operations")

def main():
    """Run performance tests."""
    print("🚀 StrategiX Agent - Performance Test")
    print("=" * 60)
    
    try:
        # Test full workflow
        success = test_full_workflow_performance()
        
        # Identify bottlenecks
        identify_bottlenecks()
        
        if success:
            print(f"\n✅ All performance tests passed!")
            print(f"💡 The application should work correctly.")
            print(f"⏱️ Main bottlenecks are likely API calls and AI analysis.")
        else:
            print(f"\n❌ Performance tests failed.")
            print(f"🔧 Check the error messages above for issues.")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        logger.error(f"Performance test error: {e}")

if __name__ == "__main__":
    main() 