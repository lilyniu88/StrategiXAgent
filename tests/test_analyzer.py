import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables from .env file
load_dotenv()

from data_processor.analyzer import ClinicalTrialAnalyzer

def test_analyzer():
    # Sample clinical trial data
    sample_trial = {
        "NCTId": "NCT12345678",
        "BriefTitle": "A Study of Novel HER2-Targeted Therapy in Advanced Breast Cancer",
        "Phase": "Phase 2",
        "OverallStatus": "Recruiting",
        "LeadSponsor": {
            "Name": "PharmaCorp Inc."
        },
        "BriefSummary": "This study evaluates a new HER2-targeted therapy in patients with advanced breast cancer.",
        "Condition": "Breast Cancer",
        "Intervention": {
            "Name": "Experimental Drug X",
            "Type": "Drug"
        }
    }

    # Initialize analyzer
    analyzer = ClinicalTrialAnalyzer(config_path=str(project_root / "tests/test_config.yaml"))

    # Test single trial analysis
    print("\nTesting single trial analysis...")
    result = analyzer.analyze_trial(sample_trial)
    print(json.dumps(result, indent=2))

    # Test batch analysis
    print("\nTesting batch analysis...")
    sample_trials = [sample_trial] * 2  # Create a list with two identical trials for testing
    batch_results = analyzer.analyze_trials_batch(sample_trials)
    print(f"Processed {len(batch_results)} trials in batch")

    # Test landscape summary
    print("\nTesting landscape summary generation...")
    summary = analyzer.generate_landscape_summary(batch_results)
    print("\nLandscape Summary:")
    print(summary)

if __name__ == "__main__":
    # Ensure GOOGLE_API_KEY is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("Error: GOOGLE_API_KEY not found in environment variables. Please create a .env file with your API key.")
        sys.exit(1)
    
    test_analyzer() 