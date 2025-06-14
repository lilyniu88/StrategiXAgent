import yaml
import requests
import json

def test_new_api():
    # Read config
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Get API settings
    base_url = config['data_collection']['clinical_trials']['base_url']
    print(f"Testing URL: {base_url}")
    
    # New API query format
    query = {
        "query.term": "cancer",
        "pageSize": 5,
        "format": "json"
    }
    
    # Print the full URL we're trying to access
    full_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in query.items())}"
    print(f"\nFull URL: {full_url}")
    
    try:
        response = requests.get(base_url, params=query)
        print(f"\nStatus code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print summary
            print(f"\nFound {data.get('totalCount', 0)} total trials")
            print(f"Showing {len(data.get('studies', []))} trials on this page")
            
            # Print each trial's details
            for study in data.get('studies', []):
                print("\n" + "="*50)
                print(f"Trial ID: {study.get('NCTId', 'N/A')}")
                print(f"Title: {study.get('BriefTitle', 'N/A')}")
                print(f"Condition: {study.get('Condition', 'N/A')}")
                print(f"Phase: {study.get('Phase', 'N/A')}")
                print(f"Sponsor: {study.get('LeadSponsor', 'N/A')}")
                print(f"Start Date: {study.get('StartDate', 'N/A')}")
                print(f"Completion Date: {study.get('CompletionDate', 'N/A')}")
            
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {str(e)}")

if __name__ == "__main__":
    test_new_api()