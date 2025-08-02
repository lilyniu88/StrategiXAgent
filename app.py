#!/usr/bin/env python3
"""
StrategiX Agent Web Frontend

A Flask-based web interface for the StrategiX Agent pharmaceutical competitive intelligence tool.
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

from main_optimized import OptimizedStrategiXAgent
from data_processor.research_interface import ResearchInterface

app = Flask(__name__)
app.secret_key = 'strategix_agent_secret_key_2024'

# Global agent instance
agent = None

# Progress tracking
analysis_progress = {}
analysis_status = {}
research_configs = {}  # Store research configs by session ID

def load_latest_analysis_results():
    """Load the most recent analysis results from output files."""
    try:
        import glob
        import yaml
        
        # Find the most recent summary file
        summary_files = glob.glob('output/competitive_landscape_*.md')
        if not summary_files:
            return None
        
        # Get the most recent file
        latest_file = max(summary_files, key=os.path.getctime)
        
        # Only load files created after the app started (within last 5 minutes)
        file_age = time.time() - os.path.getctime(latest_file)
        if file_age > 300:  # 5 minutes
            print(f"DEBUG: Skipping old analysis file (age: {file_age:.1f}s)")
            return None
            
        print(f"DEBUG: Loading latest analysis from: {latest_file}")
        
        # Extract topic name from filename
        filename = os.path.basename(latest_file)
        # Remove extension and prefix
        topic_part = filename.replace('competitive_landscape_', '').replace('.md', '')
        # Extract the topic name (before the timestamp)
        if '_' in topic_part:
            topic_name = topic_part.rsplit('_', 2)[0]  # Remove timestamp parts
        else:
            topic_name = topic_part
        
        # Read the summary content
        with open(latest_file, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # Try to find corresponding analysis file
        analysis_file = latest_file.replace('competitive_landscape_', 'analyses_').replace('.md', '.yaml')
        analyses_count = 0
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analyses_data = yaml.safe_load(f)
                if analyses_data and isinstance(analyses_data, list):
                    analyses_count = len(analyses_data)
        
        # Try to find corresponding raw data file
        raw_data_file = latest_file.replace('competitive_landscape_', 'raw_data_').replace('.md', '.yaml')
        data_records_count = 0
        if os.path.exists(raw_data_file):
            with open(raw_data_file, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
                if raw_data and isinstance(raw_data, list):
                    data_records_count = len(raw_data)
        
        # Create a mock session ID for the loaded results
        session_id = f"loaded_{int(time.time())}"
        
        # Store the results
        research_configs[session_id] = {
            'data_records_count': data_records_count,
            'analyses_count': analyses_count,
            'summary': summary_content,
            'research_topic': topic_name,
            'timestamp': datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
        }
        
        analysis_status[session_id] = 'completed'
        print(f"DEBUG: Loaded analysis results for topic: {topic_name}")
        print(f"DEBUG: Data records: {data_records_count}, Analyses: {analyses_count}")
        
        return session_id
        
    except Exception as e:
        print(f"DEBUG: Error loading latest analysis: {e}")
        return None

def initialize_agent():
    """Initialize the StrategiX Agent."""
    global agent
    try:
        agent = OptimizedStrategiXAgent()
        return True
    except Exception as e:
        return False

def run_analysis_with_progress(research_config, session_id):
    """Run analysis with progress tracking."""
    global agent
    print(f"DEBUG: Starting analysis for session {session_id}")
    
    if not agent:
        print(f"DEBUG: Agent not initialized for session {session_id}")
        analysis_progress[session_id] = {'step': 'Error', 'progress': 0, 'message': 'Agent not initialized'}
        analysis_status[session_id] = 'error'
        return
        
    try:
        print(f"DEBUG: Step 1 - Initializing analysis for session {session_id}")
        analysis_progress[session_id] = {'step': 'Starting', 'progress': 0, 'message': 'Initializing analysis...'}
        
        # Step 1: Collect data
        print(f"DEBUG: Step 2 - Starting data collection for session {session_id}")
        analysis_progress[session_id] = {'step': 'Data Collection', 'progress': 10, 'message': 'Collecting data from multiple sources...'}
        data_records = agent.collect_data(research_config)
        print(f"DEBUG: Data collection completed for session {session_id}: {len(data_records)} records")
        
        if not data_records:
            print(f"DEBUG: No data records found for session {session_id}")
            analysis_progress[session_id] = {'step': 'Error', 'progress': 0, 'message': 'No relevant data found'}
            return
        
        analysis_progress[session_id] = {'step': 'Data Collection', 'progress': 30, 'message': f'Collected {len(data_records)} records from multiple sources'}
        
        # Step 2: Analyze data
        print(f"DEBUG: Step 3 - Starting data analysis for session {session_id}")
        analysis_progress[session_id] = {'step': 'Analysis', 'progress': 40, 'message': 'Analyzing data with AI...'}
        
        # Limit the number of records to analyze to prevent getting stuck
        max_records_to_analyze = 10  # Limit to 10 records for web interface
        if len(data_records) > max_records_to_analyze:
            data_records = data_records[:max_records_to_analyze]
            analysis_progress[session_id] = {'step': 'Analysis', 'progress': 40, 'message': f'Analyzing {max_records_to_analyze} records (limited for web interface)...'}
        
        print(f"DEBUG: Starting analysis of {len(data_records)} records for session {session_id}")
        analyses = agent.analyze_data(data_records)
        print(f"DEBUG: Analysis completed for session {session_id}: {len(analyses)} analyses")
        
        analysis_progress[session_id] = {'step': 'Analysis', 'progress': 70, 'message': f'Analyzed {len(analyses)} records'}
        
        # Step 3: Generate summary
        print(f"DEBUG: Step 4 - Starting summary generation for session {session_id}")
        analysis_progress[session_id] = {'step': 'Summary', 'progress': 80, 'message': 'Generating competitive landscape summary...'}
        summary = agent.generate_summary(analyses, research_config)
        print(f"DEBUG: Summary generation completed for session {session_id}: {len(summary)} characters")
        
        analysis_progress[session_id] = {'step': 'Summary', 'progress': 90, 'message': 'Summary generated successfully'}
        
        # Step 4: Save results
        print(f"DEBUG: Step 5 - Starting results save for session {session_id}")
        analysis_progress[session_id] = {'step': 'Saving', 'progress': 95, 'message': 'Saving results...'}
        agent.save_results(data_records, analyses, summary, research_config)
        print(f"DEBUG: Results save completed for session {session_id}")
        
        # Store results in global storage for the main thread to access
        research_configs[session_id] = {
            'data_records_count': len(data_records),
            'analyses_count': len(analyses),
            'summary': summary,
            'research_topic': research_config['name'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"DEBUG: Analysis completed successfully for session {session_id}")
        analysis_progress[session_id] = {'step': 'Complete', 'progress': 100, 'message': 'Analysis completed successfully!'}
        analysis_status[session_id] = 'completed'
        
    except Exception as e:
        print(f"DEBUG: Analysis error for session {session_id}: {e}")
        analysis_progress[session_id] = {'step': 'Error', 'progress': 0, 'message': f'Error: {str(e)}'}
        analysis_status[session_id] = 'error'

@app.route('/')
def index():
    """Main page with research form."""
    return render_template('index.html')

@app.route('/research', methods=['GET', 'POST'])
def research():
    """Handle research form submission."""
    if request.method == 'POST':
        try:
            print("DEBUG: Received research form submission")
            # Get form data
            research_topic = request.form.get('research_topic', '').strip()
            research_type = request.form.get('research_type', 'topic')
            drug_name = request.form.get('drug_name', '').strip()
            indication = request.form.get('indication', '').strip()
            
            print(f"DEBUG: Form data - topic: {research_topic}, type: {research_type}, drug: {drug_name}")
            
            if not research_topic:
                return jsonify({'error': 'Research topic is required'}), 400
            
            # Create research configuration
            research_config = {
                'name': research_topic,
                'research_type': research_type,
                'original_topic': research_topic,
                'drug_name': drug_name if research_type == 'pipeline' else '',
                'indication': indication if research_type == 'pipeline' else '',
                'keywords': [research_topic.lower()]  # Will be enhanced by keyword generator
            }
            
            # Store in session for later use
            session['research_config'] = research_config
            session['research_topic'] = research_topic
            
            print(f"DEBUG: Stored research config in session: {research_config}")
            
            return jsonify({
                'success': True,
                'message': 'Research configuration created successfully',
                'redirect': url_for('analysis')
            })
            
        except Exception as e:
            print(f"DEBUG: Error in research form: {e}")
            return jsonify({'error': str(e)}), 500
    
    return render_template('research.html')

@app.route('/analysis')
def analysis():
    """Analysis page with progress tracking."""
    print(f"DEBUG: Analysis page requested. Session keys: {list(session.keys())}")
    print(f"DEBUG: Session research_config: {session.get('research_config')}")
    
    if 'research_config' not in session:
        print("DEBUG: No research_config in session, redirecting to index")
        return redirect(url_for('index'))
    
    print("DEBUG: Research config found in session, rendering analysis page")
    return render_template('analysis.html')

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """Start the analysis process."""
    print("DEBUG: Received start_analysis request")
    print(f"DEBUG: Session keys: {list(session.keys())}")
    print(f"DEBUG: Session research_config: {session.get('research_config')}")
    
    if not agent:
        print("DEBUG: Agent not initialized")
        return jsonify({'error': 'Agent not initialized'}), 500
    
    try:
        research_config = session.get('research_config')
        print(f"DEBUG: Research config from session: {research_config is not None}")
        
        if not research_config:
            print("DEBUG: No research configuration found in session")
            return jsonify({'error': 'No research configuration found'}), 400
        
        # Clear any old analysis results from session
        session.pop('analysis_results', None)
        print("DEBUG: Cleared old analysis results from session")
        
        # Generate unique session ID for progress tracking
        session_id = f"analysis_{int(time.time())}"
        analysis_status[session_id] = 'running'
        print(f"DEBUG: Starting analysis with session_id: {session_id}")
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=run_analysis_with_progress,
            args=(research_config, session_id)
        )
        thread.daemon = True
        thread.start()
        
        print(f"DEBUG: Analysis thread started for session_id: {session_id}")
        return jsonify({
            'success': True,
            'message': 'Analysis started',
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"DEBUG: Error starting analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<session_id>')
def get_progress(session_id):
    """Get analysis progress."""
    if session_id not in analysis_progress:
        return jsonify({'error': 'Session not found'}), 404
    
    progress_data = analysis_progress[session_id]
    status = analysis_status.get(session_id, 'unknown')
    
    # If analysis is completed, store results in session
    if status == 'completed':
        results = research_configs.get(session_id)
        if results:
            # Clear any old analysis results from session
            session.pop('analysis_results', None)
            # Store the new results
            session['analysis_results'] = results
            print(f"DEBUG: Stored new analysis results in session for {session_id}")
    
    return jsonify({
        'progress': progress_data['progress'],
        'step': progress_data['step'],
        'message': progress_data['message'],
        'status': status
    })

def cleanup_old_sessions():
    """Clean up old session data."""
    current_time = time.time()
    sessions_to_remove = []
    
    for session_id in analysis_progress.keys():
        # Extract timestamp from session_id (format: analysis_1234567890)
        try:
            timestamp = int(session_id.split('_')[1])
            # Remove sessions older than 1 hour
            if current_time - timestamp > 3600:
                sessions_to_remove.append(session_id)
        except (IndexError, ValueError):
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        analysis_progress.pop(session_id, None)
        analysis_status.pop(session_id, None)
        research_configs.pop(session_id, None)

@app.route('/results')
def results():
    """Display analysis results."""
    print(f"DEBUG: Results page requested")
    print(f"DEBUG: Session keys: {list(session.keys())}")
    print(f"DEBUG: Session analysis_results: {session.get('analysis_results')}")
    print(f"DEBUG: Analysis status: {analysis_status}")
    print(f"DEBUG: Research configs keys: {list(research_configs.keys())}")
    
    # Try to get results from session first (for backward compatibility)
    results = session.get('analysis_results')
    
    # If not in session, check if we have any completed analysis
    if not results:
        print(f"DEBUG: No results in session, checking completed sessions")
        # Find the most recent completed analysis
        completed_sessions = [sid for sid, status in analysis_status.items() if status == 'completed']
        print(f"DEBUG: Completed sessions: {completed_sessions}")
        if completed_sessions:
            # Get the most recent one
            latest_session = max(completed_sessions, key=lambda x: int(x.split('_')[1]))
            print(f"DEBUG: Latest session: {latest_session}")
            results = research_configs.get(latest_session)
            print(f"DEBUG: Results from latest session: {results}")
            if results:
                # Store in session for the template
                session['analysis_results'] = results
                print(f"DEBUG: Stored results in session")
    
    if not results:
        print(f"DEBUG: No results found, redirecting to index")
        return redirect(url_for('index'))
    
    print(f"DEBUG: Returning results template with data: {results}")
    return render_template('results.html', results=results)

@app.route('/api/status')
def status():
    """Get system status."""
    return jsonify({
        'agent_initialized': agent is not None,
        'config_loaded': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/examples')
def examples():
    """Get example research topics."""
    return jsonify({
        'examples': [
            {
                'topic': 'CAR-T cell therapy in hematologic malignancies',
                'type': 'topic',
                'description': 'Research on CAR-T cell therapies for blood cancers'
            },
            {
                'topic': 'Ozempic',
                'type': 'pipeline',
                'description': 'Drug pipeline research for Ozempic (semaglutide)'
            },
            {
                'topic': 'Rare disease gene therapy approaches',
                'type': 'topic',
                'description': 'Research on gene therapy for rare genetic disorders'
            },
            {
                'topic': 'Pfizer oncology pipeline',
                'type': 'pipeline',
                'description': 'Company-specific oncology pipeline research'
            },
            {
                'topic': 'mRNA vaccine technology platforms',
                'type': 'topic',
                'description': 'Research on mRNA vaccine development and applications'
            },
            {
                'topic': 'Humira biosimilars market',
                'type': 'topic',
                'description': 'Competitive landscape of Humira biosimilars'
            },
            {
                'topic': 'Moderna respiratory pipeline',
                'type': 'pipeline',
                'description': 'Company-specific respiratory disease pipeline'
            },
            {
                'topic': 'CRISPR gene editing therapeutics',
                'type': 'topic',
                'description': 'Research on CRISPR-based therapeutic approaches'
            }
        ]
    })

@app.route('/api/test_agent')
def test_agent():
    """Test if the agent is working properly."""
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 500
    
    try:
        # Simple test configuration
        test_config = {
            'name': 'test',
            'research_type': 'topic',
            'original_topic': 'test',
            'keywords': ['test']
        }
        
        # Test data collection
        data_records = agent.collect_data(test_config)
        
        return jsonify({
            'success': True,
            'agent_working': True,
            'data_records_count': len(data_records) if data_records else 0,
            'message': 'Agent is working properly'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'agent_working': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize agent
    if initialize_agent():
        print("🚀 StrategiX Agent Web Frontend Starting...")
        print("📊 Agent initialized successfully")
        
        # Load latest analysis results if available
        loaded_session = load_latest_analysis_results()
        if loaded_session:
            print(f"📋 Loaded latest analysis results (session: {loaded_session})")
        else:
            print("📋 No previous analysis results found")
        
        print("🌐 Starting web server")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5002,
            debug=True,
            use_reloader=False  # Disable reloader to avoid duplicate agent initialization
        )
    else:
        print("❌ Failed to initialize agent. Check configuration and dependencies.")
        sys.exit(1) 