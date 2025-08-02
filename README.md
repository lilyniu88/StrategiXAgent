# StrategiX Agent

An AI-powered pharmaceutical competitive intelligence tool that collects data from multiple sources (ClinicalTrials.gov, PubMed, FDA) and uses Google's Gemini AI for comprehensive analysis and insights.

## Features

### Multi-Source Data Collection
- **Clinical Trials Data**: Fetches data from ClinicalTrials.gov API v2
- **PubMed Articles**: Collects scientific publications and research papers
- **FDA Regulatory Data**: Gathers drug approvals, safety alerts, and regulatory information
- **Intelligent Data Merging**: Combines data from multiple sources for comprehensive analysis

### AI-Powered Analysis
- **Google Gemini AI Integration**: Uses advanced AI for intelligent data analysis and insights
- **Competitive Intelligence**: Generates comprehensive competitive landscape reports
- **Smart Fallback Analysis**: Provides meaningful insights even when AI is unavailable
- **Rate Limit Handling**: Gracefully handles API quotas with intelligent fallback analysis

### Interactive Research Interface
- **Dynamic Research Topics**: Enter any research topic or drug pipeline of interest
- **AI-Powered Keyword Generation**: Automatically generates relevant search keywords using AI
- **Smart Fallback**: Uses intelligent keyword mapping when AI is unavailable
- **Flexible Research Types**: Support for both general therapeutic areas and specific drug pipelines

### Drug Pipeline Research
- **Specific Drug Analysis**: Research specific drugs or drug classes instead of broad therapeutic areas
- **Pipeline-Focused Keywords**: Specialized keywords for drug development stages, safety, efficacy, and clinical endpoints
- **Indication Targeting**: Specify target diseases or conditions for more focused analysis

### Web Interface
- **Modern Web UI**: Flask-based web interface with Bootstrap 5 styling
- **Real-time Progress Tracking**: Visual progress indicators and status updates
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive Forms**: Dynamic research configuration with example topics

### Comprehensive Reporting
- **Multiple Output Formats**: Saves results in YAML and Markdown formats
- **Structured Analysis**: Detailed competitive landscape summaries
- **Data Source Tracking**: Tracks which sources contributed to the analysis
- **Professional Formatting**: Clean, readable reports with proper headers and bullet points

### Advanced Features
- **Active Trial Filtering**: Focuses on recruiting and active clinical trials
- **Error Handling**: Robust error handling with graceful degradation
- **Session Management**: Maintains user state across web interface sessions
- **Example Topics**: Pre-configured research topics for quick start

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
python main_optimized.py
```

The application will:
1. Prompt you to enter your research topic
2. Ask whether you want to research a general topic or specific drug pipeline
3. Generate AI-powered keywords for your research
4. Collect and analyze relevant clinical trials
5. Generate a comprehensive competitive landscape report

### Web Interface
For a modern web interface, run:

```bash
python app.py
```

Then open your browser to `http://localhost:5001`

### Example Research Topics
- **General Topics**: "PD-1 inhibitors in lung cancer", "Alzheimer's disease treatments", "mRNA vaccines"
- **Drug Pipelines**: "Keytruda", "Novo Nordisk diabetes pipeline", "CAR-T cell therapy"

### Test Mode
Test the new interactive features without running the full analysis:

```bash
python tests/test_interactive_features.py
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
  max_tokens: 1000
  temperature: 0.7

# Output Settings
output:
  save_path: "output"
  formats: ["yaml", "markdown"]
```

## Project Structure

```
StrategiXAgent/
├── main_optimized.py              # Main application entry point
├── app.py                         # Web interface
├── config.yaml                    # Configuration file
├── requirements.txt               # Python dependencies
├── data_collector/               # Data collection modules
│   ├── clinical_trials_collector.py
│   ├── pubmed_collector.py
│   ├── fda_collector.py
│   └── multi_source_collector.py
├── data_processor/               # Data processing modules
│   ├── analyzer.py
│   ├── keyword_generator.py
│   └── research_interface.py
├── templates/                    # Web interface templates
├── static/                       # Web interface assets
└── tests/                       # Test scripts
```

## Testing

Run the test suite to verify everything is working:

```bash
python tests/test_setup.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
