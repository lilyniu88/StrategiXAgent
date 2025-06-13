# StrategiX Agent - Pharmaceutical Competitive Intelligence Tool

An AI-powered assistant that helps commercial teams track the competitive landscape in specific therapeutic areas using Google's Gemini API.

## Features

- Automated data collection from multiple sources:
  - ClinicalTrials.gov
  - Company press releases
  - Pharma pipeline trackers
- AI-powered analysis of:
  - Trial phases
  - Mechanisms of action
  - Sponsor information
- Concise summary generation
- Competitive landscape tracking

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StrategiXAgent.git
cd StrategiXAgent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
GOOGLE_API_KEY=your_google_api_key
```

## Usage

1. Configure your therapeutic area of interest in `config.yaml`
2. Run the main script:
```bash
python main.py
```

## Project Structure

- `main.py`: Main application entry point
- `data_collector/`: Modules for data collection from various sources
- `data_processor/`: Data processing and analysis modules
- `config.yaml`: Configuration settings
- `requirements.txt`: Project dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.