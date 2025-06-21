# StrategiX Agent - Pharmaceutical Competitive Intelligence Tool

An AI-powered assistant that helps commercial teams track the competitive landscape in specific therapeutic areas using Google's Gemini API.

## Features

- **Automated Data Collection**: Fetches clinical trial data from ClinicalTrials.gov API
- **AI-Powered Analysis**: Uses Google Gemini to analyze trial phases, mechanisms of action, and sponsor information
- **Competitive Intelligence**: Generates comprehensive summaries of the competitive landscape
- **Configurable Therapeutic Areas**: Easy configuration for different disease areas
- **Structured Output**: Saves results in multiple formats (YAML, Markdown)

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free tier available)

### 2. Setup

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/StrategiXAgent.git
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

4. **Set up your API key**:
```bash
cp env.example .env
# Edit .env and add your Google API key
```

Get your Google Gemini API key from: https://makersuite.google.com/app/apikey

### 3. Configuration

Edit `config.yaml` to configure your therapeutic areas of interest:

```yaml
therapeutic_areas:
  - name: "Oncology"
    keywords:
      - "cancer"
      - "tumor"
      - "oncology"
      - "neoplasm"
      - "malignant"
      - "carcinoma"
  - name: "Cardiovascular"
    keywords:
      - "heart"
      - "cardiovascular"
      - "cardiac"
      - "hypertension"
      - "atherosclerosis"
```

### 4. Run the Application

```bash
python main.py
```

The application will:
1. Collect clinical trial data from ClinicalTrials.gov
2. Analyze each trial using AI
3. Generate a competitive landscape summary
4. Save results to the `output/` directory

## Project Structure

```
StrategiXAgent/
├── main.py                          # Main application entry point
├── config.yaml                      # Configuration settings
├── requirements.txt                 # Python dependencies
├── env.example                      # Environment variables template
├── data_collector/                  # Data collection modules
│   ├── __init__.py
│   └── clinical_trials_collector.py # ClinicalTrials.gov API client
├── data_processor/                  # Data processing modules
│   └── analyzer.py                  # AI analysis using Gemini
├── output/                          # Generated reports and data
└── tests/                           # Test files
```

## Configuration Options

### Therapeutic Areas
Configure disease areas to monitor in `config.yaml`:

```yaml
therapeutic_areas:
  - name: "Area Name"
    keywords: ["keyword1", "keyword2", "keyword3"]
```

### Data Collection Settings
```yaml
data_collection:
  clinical_trials:
    base_url: "https://clinicaltrials.gov/api/v2/studies"
    fields: ["NCTId", "BriefTitle", "Condition", "Phase", ...]
    max_results: 100
```

### AI Analysis Settings
```yaml
gemini:
  model: "gemini-pro"
  temperature: 0.7
  max_output_tokens: 1024
```

## Output Files

The application generates several output files in the `output/` directory:

- `raw_trials_YYYYMMDD_HHMMSS.yaml`: Raw clinical trial data
- `analyses_YYYYMMDD_HHMMSS.yaml`: AI analysis results for each trial
- `competitive_landscape_YYYYMMDD_HHMMSS.md`: Comprehensive competitive landscape summary

## API Usage

### ClinicalTrials.gov API
- **Rate Limits**: The application includes delays between requests to respect API limits
- **Data Fields**: Configurable fields to collect (see `config.yaml`)
- **Query Building**: Automatic query construction from therapeutic area keywords

### Google Gemini API
- **Model**: Uses `gemini-pro` for analysis
- **Cost**: Free tier available with generous limits
- **Analysis**: Provides insights on therapeutic focus, market impact, and competitive positioning

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your `.env` file contains a valid `GOOGLE_API_KEY`
2. **No Data Collected**: Check your therapeutic area keywords and internet connection
3. **Rate Limiting**: The application includes built-in delays, but you may need to adjust for high-volume usage

### Logs
Check `strategix_agent.log` for detailed execution logs.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
