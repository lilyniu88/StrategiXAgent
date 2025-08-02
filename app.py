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
    
    if not agent:
        analysis_progress[session_id] = {'step': 'Error', 'progress': 0, 'message': 'Agent not initialized'}
        analysis_status[session_id] = 'error'
        return
        
    try:
        analysis_progress[session_id] = {'step': 'Starting', 'progress': 0, 'message': 'Initializing analysis...'}
        
        # Step 1: Collect data
        analysis_progress[session_id] = {'step': 'Data Collection', 'progress': 10, 'message': 'Collecting data from multiple sources...'}
        data_records = agent.collect_data(research_config)
        
        if not data_records:
            analysis_progress[session_id] = {'step': 'Error', 'progress': 0, 'message': 'No relevant data found'}
            return
        
        analysis_progress[session_id] = {'step': 'Data Collection', 'progress': 30, 'message': f'Collected {len(data_records)} records from multiple sources'}
        
        # Step 2: Analyze data
        analysis_progress[session_id] = {'step': 'Analysis', 'progress': 40, 'message': 'Analyzing data with AI...'}
        analyses = agent.analyze_data(data_records)
        
        analysis_progress[session_id] = {'step': 'Analysis', 'progress': 70, 'message': f'Analyzed {len(analyses)} records'}
        
        # Step 3: Generate summary
        analysis_progress[session_id] = {'step': 'Summary', 'progress': 80, 'message': 'Generating competitive landscape summary...'}
        summary = agent.generate_summary(analyses, research_config)
        
        analysis_progress[session_id] = {'step': 'Summary', 'progress': 90, 'message': 'Summary generated successfully'}
        
        # Step 4: Save results
        analysis_progress[session_id] = {'step': 'Saving', 'progress': 95, 'message': 'Saving results...'}
        agent.save_results(data_records, analyses, summary, research_config)
        
        # Store results in global storage for the main thread to access
        research_configs[session_id] = {
            'data_records_count': len(data_records),
            'analyses_count': len(analyses),
            'summary': summary,
            'research_topic': research_config['name'],
            'timestamp': datetime.now().isoformat()
        }
        
        analysis_progress[session_id] = {'step': 'Complete', 'progress': 100, 'message': 'Analysis completed successfully!'}
        analysis_status[session_id] = 'completed'
        
    except Exception as e:
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
            # Get form data
            research_topic = request.form.get('research_topic', '').strip()
            research_type = request.form.get('research_type', 'topic')
            drug_name = request.form.get('drug_name', '').strip()
            indication = request.form.get('indication', '').strip()
            
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
            
            return jsonify({
                'success': True,
                'message': 'Research configuration created successfully',
                'redirect': url_for('analysis')
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('research.html')

@app.route('/analysis')
def analysis():
    """Analysis page with progress tracking."""
    if 'research_config' not in session:
        return redirect(url_for('index'))
    
    return render_template('analysis.html')

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """Start the analysis process."""
    
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 500
    
    try:
        research_config = session.get('research_config')
        
        if not research_config:
            return jsonify({'error': 'No research configuration found'}), 400
        
        # Generate unique session ID for progress tracking
        session_id = f"analysis_{int(time.time())}"
        analysis_status[session_id] = 'running'
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=run_analysis_with_progress,
            args=(research_config, session_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Analysis started',
            'session_id': session_id
        })
        
    except Exception as e:
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
            session['analysis_results'] = results
    
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
    # Try to get results from session first (for backward compatibility)
    results = session.get('analysis_results')
    
    # If not in session, check if we have any completed analysis
    if not results:
        # Find the most recent completed analysis
        completed_sessions = [sid for sid, status in analysis_status.items() if status == 'completed']
        if completed_sessions:
            # Get the most recent one
            latest_session = max(completed_sessions, key=lambda x: int(x.split('_')[1]))
            results = research_configs.get(latest_session)
            if results:
                # Store in session for the template
                session['analysis_results'] = results
    
    if not results:
        return redirect(url_for('index'))
    
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