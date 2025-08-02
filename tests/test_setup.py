#!/usr/bin/env python3
"""
Test script to verify StrategiX Agent setup and configuration.
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required modules can be imported."""
    logger.info("Testing imports...")
    
    try:
        import requests
        logger.info("✓ requests imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import requests: {e}")
        return False
        
    try:
        import google.generativeai as genai
        logger.info("✓ google.generativeai imported successfully")
    except ImportError as e:
        logger.warning(f"⚠ google.generativeai not installed: {e}")
        logger.info("  You can install it with: pip install google-generativeai")
        
    try:
        from data_collector.clinical_trials_collector import ClinicalTrialsCollector
        logger.info("✓ ClinicalTrialsCollector imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import ClinicalTrialsCollector: {e}")
        return False
        
    try:
        from data_processor.analyzer import ClinicalTrialAnalyzer
        logger.info("✓ ClinicalTrialAnalyzer imported successfully")
    except ImportError as e:
        logger.warning(f"⚠ ClinicalTrialAnalyzer import failed (likely due to missing google package): {e}")
        logger.info("  This will be resolved when google-generativeai is installed")
        
    return True

def test_config():
    """Test configuration file loading."""
    logger.info("Testing configuration...")
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        if config is None:
            logger.error("✗ Config file is empty or invalid YAML")
            return False
            
        # Check required sections
        required_sections = ['therapeutic_areas', 'data_collection', 'gemini', 'output']
        for section in required_sections:
            if section not in config:
                logger.error(f"✗ Missing required config section: {section}")
                return False
                
        logger.info("✓ Configuration file loaded successfully")
        logger.info(f"  - Therapeutic areas: {len(config['therapeutic_areas'])}")
        logger.info(f"  - Max results per area: {config['data_collection']['clinical_trials']['max_results']}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to load configuration: {e}")
        return False

def test_env():
    """Test environment variables."""
    logger.info("Testing environment variables...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.warning("⚠ No .env file found. Please create one with your GOOGLE_API_KEY")
        return False
        
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("✗ GOOGLE_API_KEY not found in environment variables")
        return False
        
    if api_key == 'your_google_api_key_here':
        logger.error("✗ Please replace the placeholder API key with your actual Google API key")
        return False
        
    logger.info("✓ Environment variables configured correctly")
    return True

def test_output_directory():
    """Test output directory creation."""
    logger.info("Testing output directory...")
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        if config is None:
            logger.error("✗ Config file is empty or invalid YAML")
            return False
        output_path = Path(config['output']['save_path'])
        output_path.mkdir(exist_ok=True)  # type: ignore
        
        logger.info(f"✓ Output directory ready: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to create output directory: {e}")
        return False

def test_api_connection():
    """Test basic API connectivity."""
    logger.info("Testing API connectivity...")
    
    try:
        import requests
        
        # Test ClinicalTrials.gov API v2 with correct parameters (no pageToken for first page)
        response = requests.get('https://clinicaltrials.gov/api/v2/studies', 
                              params={'pageSize': '1'},
                              timeout=10)
        response.raise_for_status()
        
        logger.info("✓ ClinicalTrials.gov API accessible")
        
        # Test Google Gemini API (basic check) - skip if not installed
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key and api_key != 'your_google_api_key_here':
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                # Try a simple test with the correct model name
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content("Hello, this is a test.")
                
                logger.info("✓ Google Gemini API accessible")
            else:
                logger.warning("⚠ Skipping Google Gemini API test (no valid API key)")
        except ImportError:
            logger.warning("⚠ Google Generative AI not installed - skipping Gemini API test")
        except Exception as e:
            logger.warning(f"⚠ Google Gemini API test failed: {e}")
            
        return True
        
    except Exception as e:
        logger.error(f"✗ API connectivity test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting StrategiX Agent setup verification...")
    logger.info("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Environment Variables", test_env),
        ("Output Directory", test_output_directory),
        ("API Connectivity", test_api_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
        logger.info("-" * 30)
    
    logger.info(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! StrategiX Agent is ready to use.")
        logger.info("Run 'python main_optimized.py' to start the application.")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above before running the application.")
        sys.exit(1)

if __name__ == "__main__":
    main() 