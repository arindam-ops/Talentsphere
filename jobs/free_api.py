import urllib.request
import json
import time

# Simple in-memory cache to make page loads ultra-fast
_API_CACHE = {
    'data': [],
    'timestamp': 0
}
CACHE_DURATION_SECONDS = 300  # 5 minutes


def fetch_live_tech_jobs(limit=15):
    """
    Fetches real-time live tech jobs from the 100% Free ArbeitNow API.
    Does NOT require any API key, registration, or credit card.
    """
    global _API_CACHE
    now = time.time()

    # Return cached data if fresh
    if _API_CACHE['data'] and (now - _API_CACHE['timestamp']) < CACHE_DURATION_SECONDS:
        return _API_CACHE['data'][:limit]

    url = 'https://www.arbeitnow.com/api/job-board-api'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as response:
            payload = json.loads(response.read().decode('utf-8'))
            raw_jobs = payload.get('data', [])

            jobs = []
            for item in raw_jobs:
                jobs.append({
                    'title': item.get('title', 'Software Engineer'),
                    'company_name': item.get('company_name', 'Tech Innovators'),
                    'location': item.get('location', 'Remote / Global'),
                    'remote': item.get('remote', True),
                    'url': item.get('url', '#'),
                    'tags': item.get('tags', [])[:5],
                    'created_at': item.get('created_at', ''),
                    'description': item.get('description', '')[:250] + '...' if item.get('description') else ''
                })

            if jobs:
                _API_CACHE['data'] = jobs
                _API_CACHE['timestamp'] = now
                return jobs[:limit]

    except Exception as e:
        print(f"Free Job API fetch warning (fallback active): {e}")

    # Fallback simulated dataset in case user is offline
    fallback_jobs = [
        {
            'title': 'Full Stack Python & React Engineer',
            'company_name': 'Global Tech Labs',
            'location': 'Remote',
            'remote': True,
            'url': 'https://www.arbeitnow.com',
            'tags': ['Python', 'Django', 'React', 'MySQL'],
            'created_at': 'Today',
            'description': 'Building scalable web microservices and responsive dashboards.'
        },
        {
            'title': 'Junior Backend Developer',
            'company_name': 'CloudStream Media',
            'location': 'Bangalore, India (Remote)',
            'remote': True,
            'url': 'https://www.arbeitnow.com',
            'tags': ['Python', 'MySQL', 'REST API'],
            'created_at': 'Yesterday',
            'description': 'Join a fast-moving engineering team building REST APIs and data pipelines.'
        },
        {
            'title': 'Data Analyst / Junior ML Engineer',
            'company_name': 'DataMetrics AI',
            'location': 'Hyderabad, India (Hybrid)',
            'remote': False,
            'url': 'https://www.arbeitnow.com',
            'tags': ['Python', 'Pandas', 'SQL', 'Data Science'],
            'created_at': '2 days ago',
            'description': 'Analyze customer trends and automate predictive reporting pipelines.'
        }
    ]
    return fallback_jobs[:limit]

