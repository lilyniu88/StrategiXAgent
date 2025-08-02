#!/usr/bin/env python3
"""
StrategiX Agent - Optimized Main Application Entry Point

This script orchestrates the collection, analysis, and reporting of clinical trial data
for pharmaceutical competitive intelligence with improved performance and user feedback.
"""

import os
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector.multi_source_collector import MultiSourceDataCollector
from data_processor.analyzer import ClinicalTrialAnalyzer
from data_processor.keyword_generator import KeywordGenerator
from data_processor.research_interface import ResearchInterface

class OptimizedStrategiXAgent:
    """
    Optimized StrategiX Agent for pharmaceutical competitive intelligence.
    
    This agent collects data from multiple sources, analyzes it using AI,
    and generates comprehensive competitive landscape reports.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the agent with configuration."""
        self.config = self._load_config(config_path)
        self.collector = MultiSourceDataCollector(self.config)
        self.analyzer = ClinicalTrialAnalyzer(config_path)
        self.keyword_generator = KeywordGenerator(self.config)
        self.research_interface = ResearchInterface(self.config)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            if config is None:
                raise ValueError("Config file is empty or invalid YAML")
            if not isinstance(config, dict):
                raise ValueError("Config file must contain a dictionary")
            return config
        except Exception as e:
            raise
        
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        output_path = Path(self.config['output']['save_path'])
        output_path.mkdir(exist_ok=True)  # type: ignore
        return output_path
        
    def _show_progress(self, message: str, current: Optional[int] = None, total: Optional[int] = None):
        """Show progress message to user."""
        if current is not None and total is not None:
            percentage = (current / total) * 100
            print(f"🔄 {message} ({current}/{total}) - {percentage:.1f}%")
        else:
            print(f"🔄 {message}")
        
    def collect_data(self, research_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect data from multiple sources for the specified research configuration."""
        print(f"\n📊 Step 1/4: Collecting data from multiple sources...")
        start_time = time.time()
        
        # Collect data from all configured sources
        self._show_progress("Fetching data from all sources")
        all_data = self.collector.collect_all_data(research_config)
        
        # Merge data from different sources
        self._show_progress("Merging data from different sources")
        merged_data = self.collector.merge_data_by_topic(all_data, research_config)
        
        # Filter to relevant data
        self._show_progress("Filtering relevant data")
        relevant_data = self.collector.filter_relevant_data(merged_data, research_config)
        
        end_time = time.time()
        print(f"✅ Data collection completed in {end_time - start_time:.1f} seconds")
        
        # Show data summary
        summary = self.collector.get_data_summary(all_data)
        print(f"📊 Data collected from {summary['total_sources']} sources:")
        for source, info in summary['sources'].items():
            print(f"   - {source}: {info['record_count']} records")
        print(f"📊 Total relevant records: {len(relevant_data)}")
        
        return relevant_data
        
    def analyze_data(self, data_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze the collected data from multiple sources with progress indicators."""
        print(f"\n🧠 Step 2/4: Analyzing data from multiple sources...")
        start_time = time.time()
        
        # Analyze each record with progress
        analyses = []
        total_records = len(data_records)
        
        if total_records == 0:
            print("⚠️ No data to analyze")
            return []
            
        print(f"📝 Analyzing {total_records} records (this may take a few minutes)...")
        
        for i, record in enumerate(data_records, 1):
            self._show_progress("Analyzing record", i, total_records)
            analysis = self.analyzer.analyze_trial(record)
            analyses.append(analysis)
            
            # Show progress every 5 records or at the end
            if i % 5 == 0 or i == total_records:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (total_records - i) * avg_time
                print(f"   ⏱️ Estimated time remaining: {remaining:.1f} seconds")
        
        end_time = time.time()
        print(f"✅ Analysis completed in {end_time - start_time:.1f} seconds")
        print(f"🧠 Successfully analyzed {len(analyses)} records")
        
        return analyses
        
    def generate_summary(self, analyses: List[Dict[str, Any]], research_config: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of the competitive landscape."""
        print(f"\n📋 Step 3/4: Generating competitive landscape summary...")
        start_time = time.time()
        
        self._show_progress("Creating comprehensive landscape analysis")
        summary = self.analyzer.generate_landscape_summary(analyses)
        
        end_time = time.time()
        print(f"✅ Summary generation completed in {end_time - start_time:.1f} seconds")
        print(f"📝 Generated {len(summary)} character summary")
        
        return summary
        
    def save_results(self, data_records: List[Dict[str, Any]], 
                    analyses: List[Dict[str, Any]], 
                    summary: str,
                    research_config: Dict[str, Any]):
        """Save all results to output files."""
        print(f"\n💾 Step 4/4: Saving results...")
        start_time = time.time()
        
        output_dir = self._ensure_output_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename-safe version of research name
        safe_name = "".join(c for c in research_config['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Save raw data records
        self._show_progress("Saving raw data records")
        raw_data_file = output_dir / f"raw_data_{safe_name}_{timestamp}.yaml"
        with open(raw_data_file, 'w') as f:
            yaml.dump(data_records, f, default_flow_style=False)
        
        # Save analyses
        self._show_progress("Saving data analyses")
        analyses_file = output_dir / f"analyses_{safe_name}_{timestamp}.yaml"
        with open(analyses_file, 'w') as f:
            yaml.dump(analyses, f, default_flow_style=False)
        
        # Save summary
        self._show_progress("Saving competitive landscape summary")
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
            f.write(f"\n\n## Data Sources Summary\n\n")
            
            # Add data source counts
            source_counts = {}
            for record in data_records:
                source = record.get('data_source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
                
            for source, count in source_counts.items():
                f.write(f"- **{source}**: {count} records\n")
        
        end_time = time.time()
        print(f"✅ Results saved in {end_time - start_time:.1f} seconds")
        print(f"📁 Files saved to: {output_dir}")
        print(f"📄 Summary file: {summary_file}")
        
    def run(self):
        """Execute the complete StrategiX Agent workflow with progress tracking."""
        try:
            print("\n🚀 Welcome to StrategiX Agent!")
            print("Your AI-powered pharmaceutical competitive intelligence tool.")
            print("⏱️ Estimated total time: 2-5 minutes (depending on number of trials)")
            
            # Step 1: Get research configuration from user
            research_config = self.research_interface.get_interactive_research_config()
            
            # Step 2: Collect data
            data_records = self.collect_data(research_config)
            
            if not data_records:
                print("\n❌ No relevant data found for your research topic.")
                print("💡 Try adjusting your keywords or research focus.")
                return
                
            # Step 3: Analyze data
            analyses = self.analyze_data(data_records)
            
            # Step 4: Generate summary
            summary = self.generate_summary(analyses, research_config)
            
            # Step 5: Save results
            self.save_results(data_records, analyses, summary, research_config)
            
            # Step 6: Display completion message
            print(f"\n🎉 Analysis complete!")
            print(f"📊 Found and analyzed {len(data_records)} relevant records")
            print(f"📋 Generated competitive landscape for: {research_config['name']}")
            print(f"📁 All results saved to: {self.config['output']['save_path']}")
            print(f"\n💡 Next steps:")
            print(f"   - Review the competitive landscape summary")
            print(f"   - Check individual data analyses")
            print(f"   - Export data for further analysis")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            raise

def main():
    """Main entry point for the optimized application."""
    try:
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("Please create a .env file with your Google API key:")
            print("GOOGLE_API_KEY=your_api_key_here")
            return
            
        # Initialize and run the agent
        agent = OptimizedStrategiXAgent()
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using StrategiX Agent.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 