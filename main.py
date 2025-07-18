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
from data_processor.research_interface import ResearchInterface

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
        self.research_interface = ResearchInterface(self.config)
        
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
        
    def collect_data(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect clinical trial data for the specified research configuration."""
        logger.info("Starting data collection...")
        
        # Collect clinical trials data for the research configuration
        trials_data = self.collector.fetch_trials_for_research(research_config)
        
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
        
    def generate_summary(self, analyses: List[Dict[str, Any]], research_config: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of the competitive landscape."""
        logger.info("Generating competitive landscape summary...")
        
        summary = self.analyzer.generate_landscape_summary(analyses)
        
        logger.info("Summary generation complete.")
        return summary
        
    def save_results(self, trials_data: List[Dict[str, Any]], 
                    analyses: List[Dict[str, Any]], 
                    summary: str,
                    research_config: Dict[str, Any]):
        """Save all results to output files."""
        output_dir = self._ensure_output_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename-safe version of research name
        safe_name = "".join(c for c in research_config['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Save raw trial data
        raw_data_file = output_dir / f"raw_trials_{safe_name}_{timestamp}.yaml"
        with open(raw_data_file, 'w') as f:
            yaml.dump(trials_data, f, default_flow_style=False)
        logger.info(f"Saved raw trial data to {raw_data_file}")
        
        # Save analyses
        analyses_file = output_dir / f"analyses_{safe_name}_{timestamp}.yaml"
        with open(analyses_file, 'w') as f:
            yaml.dump(analyses, f, default_flow_style=False)
        logger.info(f"Saved analyses to {analyses_file}")
        
        # Save summary
        summary_file = output_dir / f"competitive_landscape_{safe_name}_{timestamp}.md"
        with open(summary_file, 'w') as f:
            f.write(f"# Competitive Landscape Summary\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Research Configuration\n\n")
            f.write(f"- **Research Topic**: {research_config['original_topic']}\n")
            f.write(f"- **Research Type**: {research_config['research_type'].title()}\n")
            f.write(f"- **Research Area**: {research_config['name']}\n")
            
            if research_config['research_type'] == 'pipeline':
                f.write(f"- **Drug**: {research_config['drug_name']}\n")
                if research_config['indication']:
                    f.write(f"- **Indication**: {research_config['indication']}\n")
                    
            f.write(f"- **Keywords Used**: {', '.join(research_config['keywords'])}\n\n")
            
            f.write(f"## Overview\n\n")
            f.write(summary)
            f.write(f"\n\n## Trial Counts by Research Area\n\n")
            
            # Add trial counts by research area
            area_counts = {}
            for trial in trials_data:
                area = trial.get('research_area', 'Unknown')
                area_counts[area] = area_counts.get(area, 0) + 1
                
            for area, count in area_counts.items():
                f.write(f"- **{area}**: {count} trials\n")
                
        logger.info(f"Saved summary to {summary_file}")
        
    def run(self):
        """Execute the complete StrategiX Agent workflow."""
        try:
            logger.info("Starting StrategiX Agent...")
            
            # Step 1: Get research configuration from user
            print("\n🚀 Welcome to StrategiX Agent!")
            print("Your AI-powered pharmaceutical competitive intelligence tool.")
            
            research_config = self.research_interface.get_interactive_research_config()
            
            # Step 2: Collect data
            trials_data = self.collect_data(research_config)
            
            if not trials_data:
                logger.warning("No trial data collected. Exiting.")
                print("\n❌ No relevant clinical trials found for your research topic.")
                print("Try adjusting your keywords or research focus.")
                return
                
            # Step 3: Analyze data
            analyses = self.analyze_data(trials_data)
            
            # Step 4: Generate summary
            summary = self.generate_summary(analyses, research_config)
            
            # Step 5: Save results
            self.save_results(trials_data, analyses, summary, research_config)
            
            # Step 6: Display summary to user
            print(f"\n✅ Analysis complete! Found {len(trials_data)} relevant clinical trials.")
            print(f"📊 Generated competitive landscape analysis for: {research_config['name']}")
            print(f"📁 Results saved to: {self.config['output']['save_path']}")
            
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
        print("\n\n👋 Goodbye! Thanks for using StrategiX Agent.")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 