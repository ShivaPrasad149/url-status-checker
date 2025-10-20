from flask import Flask, jsonify, render_template
from prometheus_client import generate_latest, Counter, Histogram, Gauge
import requests
import time
from datetime import datetime
import os
import json

app = Flask(__name__)

URLS_CATEGORIES = {
    # --- Popular global services ---
    'https://www.google.com': 'Global',
    'https://www.github.com': 'Global',
    'https://www.stackoverflow.com': 'Global',
    'https://www.wikipedia.org': 'Global',
    'https://www.nytimes.com': 'News',
    'https://www.bbc.com': 'News',
    'https://www.netflix.com': 'Entertainment',
    'https://www.cloudflare.com': 'Cloud',
    'https://www.digitalocean.com': 'Cloud',

    # --- API endpoints ---
    'https://api.github.com': 'API',
    'https://api.openweathermap.org': 'API',
    'https://dog.ceo/api/breeds/image/random': 'API',
    'https://catfact.ninja/fact': 'API',
    'https://jsonplaceholder.typicode.com/posts': 'API',

    # --- Educational / data science sites ---
    'https://www.kaggle.com': 'Education',
    'https://www.coursera.org': 'Education',

    # --- AI and ML services ---
    'https://huggingface.co': 'AI',
    'https://www.tensorflow.org': 'AI',
    'https://pytorch.org': 'AI',

    # --- Miscellaneous ---
    'https://news.ycombinator.com': 'News',
    'https://developer.mozilla.org': 'Documentation',
    'https://www.python.org': 'Programming'
}

# Flatten list for iteration
URLS_TO_MONITOR = list(URLS_CATEGORIES.keys())

# Initialize metrics as None first, then create them in a function
URL_CHECK_COUNTER = None
URL_RESPONSE_TIME = None
URL_STATUS_GAUGE = None
URL_UP_GAUGE = None

# Store recent check history for the frontend
recent_checks = []

def initialize_metrics():
    """Initialize Prometheus metrics to avoid duplicate registration"""
    global URL_CHECK_COUNTER, URL_RESPONSE_TIME, URL_STATUS_GAUGE, URL_UP_GAUGE
    
    if URL_CHECK_COUNTER is None:
        URL_CHECK_COUNTER = Counter('url_check_total', 'Total number of URL checks', ['url', 'status_code'])
        URL_RESPONSE_TIME = Histogram('url_response_time_seconds', 'URL response time in seconds', ['url'])
        URL_STATUS_GAUGE = Gauge('url_status_code', 'Current status code of URL', ['url'])
        URL_UP_GAUGE = Gauge('url_up', 'URL is up (1) or down (0)', ['url'])

def add_to_recent_checks(result):
    """Add check result to recent checks history (keep last 50)"""
    global recent_checks
    recent_checks.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'url': result['url'],
        'status_code': result['status_code'],
        'response_time': result['response_time'],
        'success': result['success'],
        'message': result.get('message', '')
    })
    # Keep only last 50 entries
    if len(recent_checks) > 50:
        recent_checks = recent_checks[-50:]

def check_single_url(url):
    """
    Check a single URL and return metrics
    This function is called for each URL in our list
    """
    # Ensure metrics are initialized
    initialize_metrics()
    
    start_time = time.time()
    try:
        # Make HTTP request with timeout
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'URL-Monitor-Bot/1.0'
        })
        response_time = time.time() - start_time
        status_code = response.status_code
        
        # Update Prometheus metrics
        URL_CHECK_COUNTER.labels(url=url, status_code=str(status_code)).inc()
        URL_RESPONSE_TIME.labels(url=url).observe(response_time)
        URL_STATUS_GAUGE.labels(url=url).set(status_code)
        
        # Set uptime gauge: 1 if successful (200-399), 0 if error
        is_up = 1 if 200 <= status_code < 400 else 0
        URL_UP_GAUGE.labels(url=url).set(is_up)
        
        result = {
            'url': url,
            'status_code': status_code,
            'response_time': round(response_time, 3),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': is_up == 1,
            'message': 'UP' if is_up == 1 else 'DOWN'
        }
        
        # Add to recent checks
        add_to_recent_checks(result)
        return result
        
    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        response_time = time.time() - start_time
        error_type = type(e).__name__
        
        # Update metrics for failed request
        URL_CHECK_COUNTER.labels(url=url, status_code='error').inc()
        URL_RESPONSE_TIME.labels(url=url).observe(response_time)
        URL_STATUS_GAUGE.labels(url=url).set(0)
        URL_UP_GAUGE.labels(url=url).set(0)
        
        result = {
            'url': url,
            'status_code': 0,
            'response_time': round(response_time, 3),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': False,
            'message': f'Error: {error_type}',
            'error': str(e)
        }
        
        # Add to recent checks
        add_to_recent_checks(result)
        return result

@app.route('/')
def home():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api')
def api_info():
    """API information page"""
    return jsonify({
        'message': '🚀 URL Status Checker API - Dockerized',
        'version': '1.0.0',
        'environment': 'Docker Container',
        'endpoints': {
            '/': 'Dashboard frontend',
            '/api': 'This information page',
            '/api/check': 'Check all URLs once and return results',
            '/api/metrics': 'Prometheus metrics (for monitoring)',
            '/api/health': 'Health check endpoint',
            '/api/urls': 'List of monitored URLs',
            '/api/history': 'Recent check history'
        },
        'status': 'running'
    })

@app.route('/api/check')
def check_urls():
    """
    Check all URLs and return detailed results
    Access this at: http://localhost:5000/api/check
    """
    results = []
    total_checks = len(URLS_TO_MONITOR)
    successful_checks = 0
    
    print(f"🔍 Checking {total_checks} URLs...")
    
    for url in URLS_TO_MONITOR:
        result = check_single_url(url)
        results.append(result)
        
        if result['success']:
            successful_checks += 1
            print(f"✅ {url} - Status: {result['status_code']} - Time: {result['response_time']}s")
        else:
            print(f"❌ {url} - Error: {result.get('message', 'Unknown error')}")
    
    # Summary statistics
    uptime_percentage = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
    
    return jsonify({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_urls_checked': total_checks,
            'successful': successful_checks,
            'failed': total_checks - successful_checks,
            'uptime_percentage': round(uptime_percentage, 2)
        },
        'results': results
    })

@app.route('/api/metrics')
def metrics():
    """
    Endpoint for Prometheus to scrape metrics
    This provides data for our monitoring dashboard
    """
    return generate_latest()

@app.route('/api/health')
def health():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'service': 'URL Status Checker',
        'environment': 'Docker Container'
    })

@app.route('/api/urls')
def list_urls():
    """Return the list of monitored URLs"""
    return jsonify({
        'monitored_urls': URLS_TO_MONITOR,
        'total_urls': len(URLS_TO_MONITOR)
    })

@app.route('/api/history')
def get_history():
    """Return recent check history"""
    return jsonify({
        'recent_checks': recent_checks[-20:],  # Last 20 checks
        'total_checks': len(recent_checks)
    })

def start_scheduler():
    """
    Start the background scheduler that runs every 2 minutes
    We moved this function here to avoid circular imports
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    import atexit
    
    def scheduled_url_check():
        """Function that runs periodically to check all URLs"""
        print("\n🔄 Running scheduled URL check...")
        successful_checks = 0
        
        for url in URLS_TO_MONITOR:
            result = check_single_url(url)
            if result['success']:
                successful_checks += 1
                print(f"   ✅ {url} - Status: {result['status_code']} - Time: {result['response_time']}s")
            else:
                print(f"   ❌ {url} - Error: {result.get('message', 'Unknown error')}")
        
        print(f"📊 Scheduled check completed: {successful_checks}/{len(URLS_TO_MONITOR)} URLs UP")
    
    scheduler = BackgroundScheduler()
    
    # Add job to run every 2 minutes
    scheduler.add_job(
        func=scheduled_url_check,
        trigger=IntervalTrigger(minutes=2),  # Check every 2 minutes
        id='url_check_job',
        name='Scheduled URL status check every 2 minutes',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    print("✅ Background scheduler started - URL checks will run every 2 minutes")
    
    # Properly shutdown the scheduler when application exits
    atexit.register(lambda: scheduler.shutdown())

def start_application():
    """Start the Flask application with scheduler"""
    # Initialize metrics
    initialize_metrics()
    
    # Start the scheduler
    start_scheduler()
    
    # Get host from environment variable or default to 0.0.0.0 for Docker
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # Start Flask app
    print("🐳 URL Status Checker Application (Dockerized)")
    print("📍 Access your dashboard at: http://localhost:5000")
    print("📊 API endpoints available at: http://localhost:5000/api")
    print("🔄 Background checks will run every 2 minutes")
    print("⏹️  Press Ctrl+C to stop the application")
    print(f"🚀 Server running on: {host}:{port}")
    
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    start_application()