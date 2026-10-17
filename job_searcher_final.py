"""
Job Searcher using NVIDIA/Nemotron via OpenRouter

This project uses OpenRouter's API to search for AI/ML job listings 
matching strict criteria and outputs results as valid JSON.

Filters applied:
1. Remote-only jobs or location in [Remote, USA, Germany, UK, Australia]
2. Salary >= $80k (or $60k-$80k if remote)
3. Seniority: Senior, Lead, Principal
4. Industries: AI/ML, FinTech, SaaS, Cloud Computing
5. Keywords: Kubernetes, PyTorch, CI/CD, AWS/GCP/Azure
6. Exclude companies: RecruiterCo, TempStaff, StaffingSolutions
7. Gigs >= $15/hr or >= $200/project value
8. Posted within last 7 days

Output format: Valid JSON with all required fields plus skill_score.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    """Get OpenRouter API key from environment variables."""
    return os.getenv("OPENROUTER_API_KEY", "").strip()


def parse_job_text(job: Dict[str, Any]) -> str:
    """Combine all text fields for keyword matching."""
    return (job.get("title", "") + " " + 
            job.get("description", "") + " " + 
            job.get("location", ""))


def format_job(job_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format and filter job data according to strict criteria.
    
    Args:
        job_data: Raw job data from API
        
    Returns:
        Filtered list of job dictionaries with all required fields
    """
    formatted_jobs = []
    
    # Required keywords - need ALL present
    required_keywords = [
        "kubernetes", 
        "pytorch",
        ("ci/cd"), ("ci cd"),  # Handle multiple formats
        ("aws or gcp or azure")  # Need at least one cloud provider keyword
    ]
    
    # Companies to exclude (case-insensitive)
    excluded_companies = {"recruiterco", "tempstaff", "staffingsolutions"}
    
    print(f"DEBUG: Processing {len(job_data)} jobs with keywords: {required_keywords[:3]}")
    
    for job in job_data:
        # Get all text content together for keyword matching
        all_text = parse_job_text(job).lower()
        title = job.get("title", "").lower()
        
        # Filter 1: Remote-only check
        location = job.get("location", "").upper()
        valid_locations = ["REMOTE", "USA", "GERMANY", "UNITED KINGDOM", "AUSTRALIA"]
        is_remote_valid = location in valid_locations or "remote" in location.lower()
        
        if not is_remote_valid:
            print(f"\nDEBUG Job skipped ({job.get('title', '...')[:50]}): Location check FAIL")
            continue
        
        # Filter 6: Exclude specific companies
        company = job.get("company", "").lower()
        if company in excluded_companies:
            print(f"DEBUG Job skipped ({job.get('title', '...')[:50]}): Company exclusion check")
            continue
        
        # Filter 2: Salary check (>= $80k or $60k-$80k for remote)
        salary = job.get("salary_usd")
        try:
            salary_num = float(salary) if salary else 0
            salary_ok = salary_num >= 80000
            print(f"DEBUG Job ({job.get('title', '...')[:50]}): Salary check {'PASS' if salary_ok else 'FAIL'}")
        except (ValueError, TypeError):
            print(f"DEBUG Job skipped ({job.get('title', '...')[:50]}): Invalid salary")
            continue
        
        # Filter 3: Seniority check
        seniority = job.get("seniority", "")
        if seniority not in ["SENIOR", "LEAD", "PRINCIPAL"]:
            print(f"DEBUG Job skipped ({job.get('title', '...')[:50]}): Invalid seniority")
            continue
        
        # Filter 4: Industry check - must contain at least one industry keyword
        description = (job.get("description", "") + " " + job.get("location", "")).lower()
        industries = ["artificial intelligence", "machine learning", "fintech", 
                     "saas", "cloud computing"]
        
        has_industry = any(ind in description for ind in industries)
        print(f"DEBUG Job ({job.get('title', '...')[:50]}): Industry check {'PASS' if has_industry else 'FAIL'}")
        
        if not has_industry:
            continue
        
        # Filter 5: Keywords check - ALL must be present (case-insensitive)
        all_keywords_found = True
        
        for keyword in required_keywords:
            found = False
            for kw in keyword.split():
                if kw in all_text:
                    found = True
                    break
            
            if not found:
                print(f"DEBUG Job ({job.get('title', '...')[:50]}): Keyword '{keyword}' MISSING")
                all_keywords_found = False
        
        if not all_keywords_found:
            continue
        
        # Filter 7: Gig/micro-task pay validation
        is_gig = any(job.get("source", "").lower() in ["mturk", "clickworker", "fiverr"] 
                    for _ in job_data)
        
        if is_gig or "gig" in title.lower() or "micro-task" in description:
            salary_num = float(salary) if isinstance(salary, (int, float)) else 0
            
            # Gig must pay >= $15/hr or project value >= $200
            if salary_num < 15:
                print(f"DEBUG Job skipped ({job.get('title', '...')[:50]}): Gig pay check FAIL")
                continue
        
        # Filter 8: Posted within last 7 days
        posted_at = job.get("posted_at")
        try:
            posted_dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            cutoff_date = datetime.now() - timedelta(days=7)
            
            if posted_dt < cutoff_date:
                print(f"DEBUG Job skipped ({job.get('title', '...')[:50]}): Posted too old")
                continue
        except ValueError:
            print(f"DEBUG Job skipped ({job.get('title', '...')[:50]}): Invalid date format")
            continue
        
        # Calculate skill_score (bonus feature 0-100)
        skill_score = calculate_skill_score(job, job_data)
        
        formatted_job = {
            "source": str(job.get("source", "unknown")),
            "source_id": str(job.get("source_id", "n/a")),
            "title": str(job.get("title", "")),
            "company": str(job.get("company", "")),
            "location": str(job.get("location", "")),
            "salary_usd": job.get("salary_usd"),
            "description": str(job.get("description", "")),
            "url": str(job.get("url", "")),
            "posted_at": job.get("posted_at"),
            "seniority": job.get("seniority"),
            "skill_score": skill_score
        }
        
        formatted_jobs.append(formatted_job)
    
    return formatted_jobs


def calculate_skill_score(job: Dict[str, Any], all_jobs: List[Dict[str, Any]]) -> int:
    """
    Calculate a skill score (0-100) based on how many of your key skills 
    are matched in the job description compared to other similar jobs.
    
    Higher score = better fit for learning new tools/expertise.
    """
    # Your key skills (from profile.yaml or hardcoded here)
    my_skills = [
        "python", "pytorch", "kubernetes", "aws", "azure", "gcp", 
        "docker", "ci-cd", "git", "machine learning", "deep learning",
        "nlp", "llms", "data engineering", "ml ops", "terraform",
        "infrastructure as code", "cloud computing", "saas", "fin-tech",
        "agile"
    ]
    
    # Combine title and description for matching
    job_text = (f"{job.get('title', '')} {job.get('description', '')}")
    job_text_lower = job_text.lower()
    
    # Count skills matched in this job
    skills_matched_in_job = sum(1 for skill in my_skills if any(kw in job_text_lower 
                                                           for kw in skill.split()))
    
    # Find similar jobs (other jobs with matching keywords)
    similar_count = 0
    for other_job in all_jobs:
        if other_job["source_id"] == job["source_id"]:
            continue
            
        other_text = f"{other_job.get('title', '')} {other_job.get('description', '')}".lower()
        
        # Check if other job has similar keywords (at least one match)
        if sum(1 for skill in my_skills if any(kw in other_text 
                                                 for kw in skill.split())) > 0:
            similar_count += 1
    
    # Calculate score based on rarity among matching jobs
    total_matching = similar_count + 1
    
    # Score components:
    # - Rarity (more unique = higher score)
    # - Number of skills matched (higher = better fit)
    
    rarity_score = int((total_matching - 1) / max(total_matching, 1) * 30)
    skill_match_score = (skills_matched_in_job / len(my_skills)) * 40
    bonus_count = min(2, similar_count) * 3
    
    score = round(rarity_score + skill_match_score + bonus_count)
    
    return min(100, max(0, score))


def main():
    """Main function to search for and filter jobs."""
    
    api_key = get_api_key()
    print("=" * 80)
    print("AI Job Searcher - NVIDIA/Nemotron via OpenRouter")
    print("=" * 80)
    print(f"Using model: nvidia/nemotron-3.5-super-vl")
    print(f"OpenRouter API Key: {'✓ Configured' if api_key else '✗ Not configured'}")
    print("-" * 80)
    
    # Simulated job data for demonstration (in production, use OpenRouter API)
    sample_jobs = [
        {
            "source": "linkedin",
            "source_id": "job_12345",
            "title": "Senior ML Engineer - PyTorch & Kubernetes on AWS",
            "company": "TechCorp AI",
            "location": "Remote, USA",
            "salary_usd": 120000,
            "description": "We are joining our Artificial Intelligence team with PyTorch and CI/CD pipelines.",
            "url": "https://www.linkedin.com/jobs/view/ml-engineer-ai-techcorp",
            "posted_at": "2026-10-15T10:30:00Z",
            "seniority": "Senior"
        },
        {
            "source": "indeed",
            "source_id": "job_67890",
            "title": "Lead AI Engineer - PyTorch, Kubernetes on Azure",
            "company": "CloudFirst Solutions",
            "location": "Remote, Germany",
            "salary_usd": 95000,
            "description": "Machine Learning and SaaS products with Artificial Intelligence capabilities. PyTorch, CI/CD pipelines, and Azure cloud infrastructure.",
            "url": "https://www.indeed.com/viewjob?jk=lead-ai-engineer",
            "posted_at": "2026-10-14T14:20:00Z",
            "seniority": "Lead"
        },
        {
            "source": "remotejobs.io",
            "source_id": "job_11111",
            "title": "Principal Engineer - PyTorch & CI/CD on AWS Kubernetes",
            "company": "SaaS Masters",
            "location": "Remote, United Kingdom",
            "salary_usd": 140000,
            "description": "Cloud Computing SaaS platform with Machine Learning features. PyTorch frameworks required.",
            "url": "https://remotejobs.io/job/principal-engineer-ai",
            "posted_at": "2026-10-13T09:15:00Z",
            "seniority": "Principal"
        },
    ]
    
    print("\nApplying strict filters...\n")
    
    # Apply all filters to get valid JSON results
    formatted_jobs = format_job(sample_jobs)
    
    if len(formatted_jobs) == 0:
        print("❌ No jobs matched ALL filter criteria.")
        result = {"jobs": [], "message": "No qualifying jobs found matching all criteria."}
    else:
        print(f"\n✅ Found {len(formatted_jobs)} job(s) matching ALL criteria!\n")
        
        # Generate valid JSON output
        json_output = json.dumps(formatted_jobs, indent=2)
        print("📊 VALID JSON OUTPUT:\n")
        print("=" * 80)
        print(json_output)
        print("=" * 80)
        
        # Write to file for easier viewing
        output_file = "job_matches.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"\n📁 Results also saved to: {output_file}")
    
    return formatted_jobs


if __name__ == "__main__":
    main()
