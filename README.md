# StrategiX Agent

An AI-powered pharmaceutical competitive intelligence tool that collects clinical trial data from ClinicalTrials.gov and uses Google's Gemini AI for comprehensive analysis and insights.

## 🚀 New Features

### Interactive Research Topic Input
- **Dynamic Research Topics**: Enter any research topic or drug pipeline of interest via terminal
- **AI-Powered Keyword Generation**: Automatically generates relevant search keywords using Google's Gemini AI
- **Smart Fallback**: Uses intelligent keyword mapping when AI is unavailable

### Drug Pipeline Research
- **Specific Drug Analysis**: Research specific drugs or drug classes instead of broad therapeutic areas
- **Pipeline-Focused Keywords**: Specialized keywords for drug development stages, safety, efficacy, and clinical endpoints
- **Indication Targeting**: Specify target diseases or conditions for more focused analysis

## Features

- **Interactive Research Interface**: User-friendly terminal interface for research topic input
- **AI-Powered Analysis**: Uses Google's Gemini AI for intelligent data analysis and keyword generation
- **Clinical Trial Data Collection**: Fetches data from ClinicalTrials.gov API v2
- **Competitive Intelligence**: Generates comprehensive competitive landscape reports
- **Flexible Research Types**: Support for both general therapeutic areas and specific drug pipelines
- **Active Trial Filtering**: Focuses on recruiting and active clinical trials
- **Comprehensive Reporting**: Saves results in multiple formats (YAML, Markdown)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd StrategiXAgent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

### Interactive Mode (Recommended)
Run the main application for a guided research experience:

```bash
python main.py
```

The application will:
1. Prompt you to enter your research topic
2. Ask whether you want to research a general topic or specific drug pipeline
3. Generate AI-powered keywords for your research
4. Collect and analyze relevant clinical trials
5. Generate a comprehensive competitive landscape report

### Example Research Topics
- **General Topics**: "PD-1 inhibitors in lung cancer", "Alzheimer's disease treatments", "mRNA vaccines"
- **Drug Pipelines**: "Keytruda", "Novo Nordisk diabetes pipeline", "CAR-T cell therapy"

### Test Mode
Test the new interactive features without running the full analysis:

```bash
python test_interactive_features.py
```

## Configuration

The application uses `config.yaml` for configuration:

```yaml
# Data Collection Settings
data_collection:
  clinical_trials:
    base_url: "https://clinicaltrials.gov/api/v2/studies"
    fields:
      - "NCTId"
      - "BriefTitle"
      - "Condition"
      - "Phase"
      - "InterventionName"
      - "LeadSponsor"
      - "StartDate"
      - "CompletionDate"
    max_results: 100

# Google Gemini API Settings
gemini:
  model: "gemini-2.0-flash-exp"
  temperature: 0.7
  max_output_tokens: 1024

# Output Settings
output:
  summary_format: "markdown"
  save_path: "output/"
  update_frequency: "daily"
```

## Project Structure

```
StrategiXAgent/
├── main.py                          # Main application entry point
├── config.yaml                      # Configuration file
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (create this)
├── data_collector/                 # Data collection modules
│   ├── __init__.py
│   └── clinical_trials_collector.py
├── data_processor/                 # Data processing and analysis
│   ├── __init__.py
│   ├── analyzer.py
│   ├── keyword_generator.py        # AI-powered keyword generation
│   └── research_interface.py       # Interactive research interface
├── output/                         # Generated reports and data
└── tests/                          # Test files
```

## Key Components

### Keyword Generator (`data_processor/keyword_generator.py`)
- **AI-Powered Generation**: Uses Google's Gemini AI to generate relevant keywords
- **Drug Pipeline Keywords**: Specialized keywords for drug development research
- **Fallback System**: Intelligent keyword mapping when AI is unavailable

### Research Interface (`data_processor/research_interface.py`)
- **Interactive Input**: User-friendly terminal interface
- **Research Type Selection**: Choose between general topics and drug pipelines
- **Configuration Generation**: Creates research configurations from user input

### Clinical Trials Collector (`data_collector/clinical_trials_collector.py`)
- **Dynamic Research**: Works with any research configuration
- **Keyword Filtering**: Filters trials based on generated keywords
- **Active Trial Focus**: Prioritizes recruiting and active trials

## Output

The application generates several output files:

1. **Raw Trial Data** (`raw_trials_[topic]_[timestamp].yaml`): Collected clinical trial data
2. **Analyses** (`analyses_[topic]_[timestamp].yaml`): AI-generated trial analyses
3. **Competitive Landscape** (`competitive_landscape_[topic]_[timestamp].md`): Comprehensive summary report

## Requirements

- Python 3.8+
- Google API key for Gemini AI
- Internet connection for API access

## Dependencies

- `requests`: HTTP requests for API calls
- `pyyaml`: YAML file handling
- `python-dotenv`: Environment variable management
- `google-generativeai`: Google's Gemini AI integration (optional)

## Troubleshooting

### AI Features Not Working
If you encounter issues with AI features:
1. Ensure your Google API key is correctly set in `.env`
2. The application will automatically fall back to basic keyword generation
3. Check that you have the `google-generativeai` package installed

### No Trials Found
If no relevant trials are found:
1. Try a broader research topic
2. Check that your keywords are relevant to clinical trials
3. Verify your internet connection and API access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
