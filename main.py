#!/usr/bin/env python3
"""
StrategiX Agent - Main Application Entry Point

This script orchestrates the collection, analysis, and reporting of clinical trial data
for pharmaceutical competitive intelligence.
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector.clinical_trials_collector import ClinicalTrialsCollector
from data_processor.analyzer import ClinicalTrialAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strategix_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StrategiXAgent:
    """Main application class for the StrategiX Agent."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the StrategiX Agent with configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        self.collector = ClinicalTrialsCollector(self.config)
        self.analyzer = ClinicalTrialAnalyzer(config_path)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            if config is None:
                raise ValueError("Config file is empty or invalid YAML")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
            
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        output_path = Path(self.config['output']['save_path'])
        output_path.mkdir(exist_ok=True)  # type: ignore
        return output_path
        
    def collect_data(self) -> List[Dict[str, Any]]:
        """Collect clinical trial data from all sources."""
        logger.info("Starting data collection...")
        
        # Collect clinical trials data
        trials_data = self.collector.fetch_all_trials()
        
        # Filter to active trials only
        active_trials = self.collector.filter_active_trials(trials_data)
        
        logger.info(f"Data collection complete. Found {len(active_trials)} active trials.")
        return active_trials
        
    def analyze_data(self, trials_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze the collected clinical trial data."""
        logger.info("Starting data analysis...")
        
        # Analyze each trial
        analyses = self.analyzer.analyze_trials_batch(trials_data)
        
        logger.info(f"Analysis complete. Analyzed {len(analyses)} trials.")
        return analyses
        
    def generate_summary(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive summary of the competitive landscape."""
        logger.info("Generating competitive landscape summary...")
        
        summary = self.analyzer.generate_landscape_summary(analyses)
        
        logger.info("Summary generation complete.")
        return summary
        
    def save_results(self, trials_data: List[Dict[str, Any]], 
                    analyses: List[Dict[str, Any]], 
                    summary: str):
        """Save all results to output files."""
        output_dir = self._ensure_output_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw trial data
        raw_data_file = output_dir / f"raw_trials_{timestamp}.yaml"
        with open(raw_data_file, 'w') as f:
            yaml.dump(trials_data, f, default_flow_style=False)
        logger.info(f"Saved raw trial data to {raw_data_file}")
        
        # Save analyses
        analyses_file = output_dir / f"analyses_{timestamp}.yaml"
        with open(analyses_file, 'w') as f:
            yaml.dump(analyses, f, default_flow_style=False)
        logger.info(f"Saved analyses to {analyses_file}")
        
        # Save summary
        summary_file = output_dir / f"competitive_landscape_{timestamp}.md"
        with open(summary_file, 'w') as f:
            f.write(f"# Competitive Landscape Summary\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Overview\n\n")
            f.write(summary)
            f.write(f"\n\n## Trial Counts by Therapeutic Area\n\n")
            
            # Add trial counts by therapeutic area
            area_counts = {}
            for trial in trials_data:
                area = trial.get('therapeutic_area', 'Unknown')
                area_counts[area] = area_counts.get(area, 0) + 1
                
            for area, count in area_counts.items():
                f.write(f"- **{area}**: {count} trials\n")
                
        logger.info(f"Saved summary to {summary_file}")
        
    def run(self):
        """Execute the complete StrategiX Agent workflow."""
        try:
            logger.info("Starting StrategiX Agent...")
            
            # Step 1: Collect data
            trials_data = self.collect_data()
            
            if not trials_data:
                logger.warning("No trial data collected. Exiting.")
                return
                
            # Step 2: Analyze data
            analyses = self.analyze_data(trials_data)
            
            # Step 3: Generate summary
            summary = self.generate_summary(analyses)
            
            # Step 4: Save results
            self.save_results(trials_data, analyses, summary)
            
            logger.info("StrategiX Agent execution completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            raise

def main():
    """Main entry point for the application."""
    try:
        # Check if .env file exists
        if not os.path.exists('.env'):
            logger.error("No .env file found. Please create one with your GOOGLE_API_KEY.")
            print("Please create a .env file with your Google API key:")
            print("GOOGLE_API_KEY=your_api_key_here")
            return
            
        # Initialize and run the agent
        agent = StrategiXAgent()
        agent.run()
        
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user.")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 