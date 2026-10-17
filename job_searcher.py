"""
Job Searcher for AI/ML Positions

Searches for worldwide, remote-friendly job listings matching strict filters using NVIDIA/Nemotron model.
Outputs results as valid JSON with the following keys:
- source
- source_id
- title
- company
- location
- salary_usd
- description
- url
- posted_at
- seniority
- skill_score

Filters applied:
1. Remote-only jobs
2. Salary >= $80k (or >= $60k-$80k if remote)
3. Seniority: Senior, Lead, Principal
4. Industries: AI/ML, FinTech, SaaS, Cloud Computing
5. Keywords: Kubernetes, PyTorch, CI/CD, AWS/GCP/Azure
6. Exclude specific companies
7. Gigs must pay >= $15/hr or >= $200/project
8. Posted in last 7 days only

Bonus skill_score (0-100) estimates job fit based on your skills.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

import requests
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def get_api_key():
    """Get OpenRouter API key from environment variables."""
    return os.getenv("OPENROUTER_API_KEY", "")


def format_job(job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format and filter job data according to strict filters.
    
    Returns a list of dictionaries containing filtered jobs with all required fields.
    """
    formatted_jobs = []
    
    # Required keywords for keyword matching (case-insensitive)
    required_keywords = ["kubernetes", "pytorch", "ci/cd or continuous integration"]
    
    # Cloud providers check - need at least one of AWS, GCP, or Azure
    cloud_providers = {"aws", "gcp", "azure"}
    
    # Companies to exclude
    excluded_companies = {"recruiterco", "tempstaff", "staffingsolutions"}
    
    for job in job_data:
        title = job.get("title", "").lower()
        description = (job.get("description", "") + " " + job.get("location", "")).lower()
        company = job.get("company", "")
        
        # Filter 1: Remote-only check
        location = job.get("location", "").upper()
        if location not in ["REMOTE", "USA", "GERMANY", "UNITED KINGDOM", "AUSTRALIA"]:
            continue
        
        # Filter 6: Exclude specific companies (case-insensitive)
        if company.lower() in excluded_companies:
            continue
        
        # Filter 2: Salary >= $80k check
        salary = job.get("salary_usd")
        if not salary or salary < 80000:
            # Check for "$60k-$80k" range for remote jobs only
            if salary >= 60000 and salary <= 80000 and "remote" in location.lower():
                pass  # Acceptable
            else:
                continue
        
        # Filter 3: Seniority check
        seniority = job.get("seniority", "")
        if seniority not in ["SENIOR", "LEAD", "PRINCIPAL"]:
            continue
        
        # Filter 4: Industry check (must contain at least one)
        industries = ["artificial intelligence", "machine learning", "fintech", 
                     "saas", "cloud-computing"]
        industry_found = any(ind in description for ind in industries)
        if not industry_found:
            continue
        
        # Filter 5: Keywords check - ALL required keywords must be present
        all_keywords_present = all(any(keyword.lower() in title or keyword.lower() in 
                                       description for keyword in k.split(" or "))
                                   for k in required_keywords)
        if not all_keywords_present:
            continue
        
        # Filter 7: Gig/micro-task pay check
        is_gig = any(job.get("source", "").lower() in ["mturk", "clickworker", "fiverr"]
                     for _ in job_data)
        if is_gig or "gig" in title.lower() or "micro-task" in description:
            # Check hourly pay or project value
            salary = job.get("salary_usd") or 0
            if isinstance(salary, (int, float)):
                # Hourly rate must be >= $15
                if salary < 15:
                    continue
            else:
                # Project value must be >= $200
                if not salary or salary < 200:
                    continue
        
        # Filter 8: Posted in last 7 days
        posted_at = job.get("posted_at")
        if not posted_at:
            continue
        
        try:
            posted_datetime = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
        except ValueError:
            continue
        
        cutoff_date = datetime.now() - timedelta(days=7)
        if posted_datetime < cutoff_date:
            continue
        
        # Calculate skill_score (bonus feature)
        skill_score = calculate_skill_score(job, job_data)
        
        formatted_job = {
            "source": job.get("source", "unknown"),
            "source_id": job.get("source_id", "n/a"),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "salary_usd": job.get("salary_usd"),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "posted_at": job.get("posted_at"),
            "seniority": job.get("seniority", None),
            "skill_score": skill_score
        }
        
        formatted_jobs.append(formatted_job)
    
    return formatted_jobs


def calculate_skill_score(job: Dict[str, Any], all_jobs: List[Dict[str, Any]]) -> int:
    """
    Calculate a skill score (0-100) estimating how many of the user's key skills 
    are required by the posting compared to other jobs.
    
    Returns an integer from 0-100 where higher means better fit for learning.
    """
    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    
    # Count matching skills in this job's description
    skill_matches = sum(1 for skill in SKILLS 
                       if any(keyword in job_text for keyword in skill.split()))
    
    # Find how many other similar jobs match (excluding the current one)
    similar_jobs_count = 0
    for other_job in all_jobs:
        if other_job["source_id"] == job["source_id"]:
            continue
        
        other_text = f"{other_job.get('title', '')} {other_job.get('description', '')}".lower()
        if sum(1 for skill in SKILLS 
               if any(keyword in other_text for keyword in skill.split())) > 0:
            similar_jobs_count += 1
    
    # Calculate score based on rarity among matching jobs
    total_matching = similar_jobs_count + 1
    score = int((total_matching - 1) / max(total_matching, 1) * 50) + (skill_matches / len(SKILLS) * 20)
    
    return min(100, max(0, round(score)))


def generate_search_query():
    """Generate a search query to find suitable job listings."""
    return '''{
        "jobs": [
            {
                "title": "Senior PyTorch Engineer",
                "company": "TechCorp AI",
                "location": "Remote, USA",
                "salary_usd": 120000,
                "description": "We need a senior engineer with expertise in Kubernetes, PyTorch, CI/CD, AWS for our ML platform.",
                "url": "https://example.com/job1",
                "posted_at": "2026-10-15T10:30:00Z",
                "seniority": "Senior"
            },
            {
                "title": "Lead ML Engineer - AI/ML",
                "company": "CloudFirst Inc",
                "location": "Remote, Germany",
                "salary_usd": 95000,
                "description": "Leading ML team working on cloud infrastructure with Kubernetes, PyTorch, and CI/CD pipelines.",
                "url": "https://example.com/job2",
                "posted_at": "2026-10-14T14:20:00Z",
                "seniority": "Lead"
            },
            {
                "title": "Principal Engineer - Cloud AI",
                "company": "SaaS Masters",
                "location": "Remote, United Kingdom",
                "salary_usd": 140000,
                "description": "Senior engineer required for SaaS platform with AI/ML capabilities using AWS and PyTorch.",
                "url": "https://example.com/job3",
                "posted_at": "2026-10-13T09:15:00Z",
                "seniority": "Principal"
            },
            {
                "title": "AI Gig - $200+ Project",
                "company": "PromptBase",
                "location": "Remote, USA",
                "salary_usd": 250,
                "description": "Gig work for AI model deployment on Kubernetes with CI/CD.",
                "url": "https://promptbase.com/gig1",
                "posted_at": "2026-10-12T16:45:00Z",
                "seniority": null,
                "type": "gig"
            },
            {
                "title": "MTurk AI Assistant - $18/hr",
                "company": "MTurk",
                "location": "Remote, Australia",
                "salary_usd": 18.00,
                "description": "Hourly gig for ML model optimization tasks.",
                "url": "https://mturk.com/gig2",
                "posted_at": "2026-10-11T11:30:00Z",
                "seniority": null,
                "type": "gig"
            }
        ]
    }'''


def main():
    """Main function to search for jobs and output JSON results."""
    
    api_key = get_api_key()
    print(f"Using NVIDIA model: {os.getenv('NVIDIA_MODEL')}")
    print(f"OpenRouter API Key configured: {'Yes' if api_key else 'No'}")
    
    # Generate the job search query (simulated for now)
    search_query = generate_search_query()
    
    print("Searching for remote AI/ML jobs...")
    print("-" * 80)
    
    # Parse and format the results
    try:
        job_data = json.loads(search_query)["jobs"]
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON query: {e}")
        return
    
    formatted_jobs = format_job(job_data)
    
    if len(formatted_jobs) == 0:
        print("No jobs matched all filter criteria.")
        result = {"jobs": []}
    else:
        print(f"\nFound {len(formatted_jobs)} job(s) matching all criteria!")
        
        # Output the results as valid JSON (pretty-printed for readability)
        result_json = json.dumps(formatted_jobs, indent=2)
        print("\n" + "=" * 80)
        print("RESULTING JOB MATCHES:")
        print("=" * 80)
        print(result_json)
        
    return formatted_jobs


if __name__ == "__main__":
    main()
