#!/usr/bin/env python3
"""
Test script for the multi-source data collector.
"""

import yaml
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector.multi_source_collector import MultiSourceDataCollector

def test_multi_source_collector():
    """Test the multi-source data collector."""
    
    # Load configuration
    with open('config.yaml', 'r') as f:
        config_data = yaml.safe_load(f)
        
    if not isinstance(config_data, dict):
        raise ValueError("Config file must contain a dictionary")
    
    config = config_data
    
    # Create test research configuration
    test_research_config = {
        'name': 'Test Research',
        'research_type': 'pipeline',
        'original_topic': 'Cancer immunotherapy',
        'drug_name': '',  # Remove specific drug name to get broader results
        'indication': 'Cancer treatment',
        'keywords': ['cancer', 'immunotherapy', 'treatment', 'therapy']
    }
    
    print("🧪 Testing Multi-Source Data Collector...")
    
    try:
        # Initialize collector
        collector = MultiSourceDataCollector(config)
        print(f"✅ Initialized collector with {len(collector.collectors)} data sources")
        
        # Test data collection
        print("\n📊 Testing data collection...")
        all_data = collector.collect_all_data(test_research_config)
        
        # Show results
        summary = collector.get_data_summary(all_data)
        print(f"\n📈 Data Collection Results:")
        print(f"   Total sources: {summary['total_sources']}")
        print(f"   Total records: {summary['total_records']}")
        
        for source, info in summary['sources'].items():
            print(f"   - {source}: {info['record_count']} records ({info['status']})")
        
        # Test data merging
        print("\n🔄 Testing data merging...")
        merged_data = collector.merge_data_by_topic(all_data, test_research_config)
        print(f"   Merged {len(merged_data)} records from {len(all_data)} sources")
        
        # Show some sample data with dates
        print("\n📅 Sample Data Dates:")
        for i, record in enumerate(merged_data[:3]):
            print(f"   Record {i+1}: {record.get('data_source', 'Unknown')}")
            print(f"      Keys: {list(record.keys())}")
            
            if record.get('data_source') == 'clinical_trials':
                protocol = record.get('protocolSection', {})
                print(f"      Protocol keys: {list(protocol.keys())}")
                if 'statusModule' in protocol:
                    status = protocol['statusModule']
                    print(f"      Status keys: {list(status.keys())}")
                    if 'startDateStruct' in status:
                        print(f"      Start date: {status['startDateStruct']}")
                    if 'completionDateStruct' in status:
                        print(f"      Completion date: {status['completionDateStruct']}")
            
            if 'publication_date' in record:
                print(f"      PubMed date: {record['publication_date']}")
            elif 'approval_date' in record:
                print(f"      FDA date: {record['approval_date']}")
            elif 'start_date' in record:
                print(f"      ClinicalTrials date: {record['start_date']}")
            elif 'effective_time' in record:
                print(f"      FDA effective_time: {record['effective_time']}")
            else:
                print(f"      No date found")
            print()
        
        # Test filtering
        print("\n🔍 Testing data filtering...")
        relevant_data = collector.filter_relevant_data(merged_data, test_research_config)
        print(f"   Filtered to {len(relevant_data)} relevant records")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_source_collector() 