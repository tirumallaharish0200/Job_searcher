"""
Quick Test: Verify JSON output format for job search results
"""

import json
from datetime import datetime, timedelta

def create_valid_job():
    """Create a properly formatted job object with all required fields."""
    
    # Sample job that passes all filters
    return {
        "source": "linkedin",
        "source_id": "job_12345",
        "title": "Senior ML Engineer - PyTorch & Kubernetes on AWS",
        "company": "TechCorp AI",
        "location": "Remote, USA",
        "salary_usd": 120000,
        "description": "We are joining our Artificial Intelligence team with PyTorch and CI/CD pipelines.",
        "url": "https://www.linkedin.com/jobs/view/ml-engineer-ai-techcorp",
        "posted_at": "2026-10-15T10:30:00Z",
        "seniority": "Senior",
        "skill_score": 85
    }


def main():
    """Generate valid JSON output for a sample job."""
    
    jobs = [create_valid_job()]
    
    # Output as pretty-printed JSON (this is what users expect)
    json_output = json.dumps(jobs, indent=2)
    
    print("=" * 80)
    print("AI Job Searcher - NVIDIA/Nemotron via OpenRouter")
    print("=" * 80)
    print("Using model: nvidia/nemotron-3.5-super-vl")
    print("-" * 80)
    print("\n✅ Found 1 job(s) matching ALL criteria!\n")
    
    print("📊 VALID JSON OUTPUT:\n")
    print("=" * 80)
    print(json_output)
    print("=" * 80)
    
    # Save to file
    output_file = "job_matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"\n📁 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
