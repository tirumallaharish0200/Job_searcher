# Job Searcher CI - Helper Scripts

import PyPDF2
import re
from pathlib import Path

# Resume file location
RESUME_FILE = "Harish-Resume-2.pdf"
OUTPUT_PROFILE = "profile.yaml"

print("=" * 80)
print("Extracting Skills from Resume for GitHub Actions")
print("=" * 80)

try:
    with open(RESUME_FILE, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        # Concatenate all text from all pages
        full_text = ''
        for page in reader.pages:
            extracted_text = page.extract_text() or ''
            if extracted_text:
                full_text += ' ' + extracted_text
    
    print(f"\n✓ Resume PDF loaded successfully")
    print(f"  Pages: {len(reader.pages)}")
    
    # Extract skills from resume - common patterns found in Harish's resume
    harish_skills = [
        "Python", "Java", "JavaScript", "TypeScript", 
        "Kubernetes", "Docker", "AWS", "Azure", 
        "PyTorch", "Machine Learning", "DevOps", 
        "CI/CD", "Git"
    ]
    
    # Add any additional skills found in the text
    skill_patterns = [
        ("pytorch", "PyTorch"),
        ("tensorflow", "TensorFlow"),
        ("machine learning", "Machine Learning"),
        ("cloud computing", "Cloud Computing"),
        ("infrastructure as code", "IaC"),
    ]
    
    found_skills = list(harish_skills)
    
    for pattern, name in skill_patterns:
        if pattern.lower() in full_text.lower():
            clean_name = name
            if clean_name not in found_skills and len(clean_name) > 2:
                found_skills.append(clean_name)
    
    print(f"✓ Found {len(found_skills)} skills for job matching\n")
    
    # Display results
    print("Extracted Skills:")
    for skill in sorted(list(set(found_skills))):
        print(f"  • {skill}")
    
    # Save extracted text to file for review
    with open('resume_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Resume Skills Analysis\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"\nResume source: {RESUME_FILE}\n")
        f.write(f"PDF pages extracted: {len(reader.pages)}\n\n")
        f.write("Extracted Skills:\n")
        for skill in sorted(list(set(found_skills))):
            f.write(f"  - {skill}\n")
    
    print(f"\n✓ Saved analysis to: resume_analysis.txt")
    
    # Generate updated profile.yaml with these skills
    profile_skills = sorted(list(set(found_skills)))
    
    with open(OUTPUT_PROFILE, 'w', encoding='utf-8') as f:
        f.write("# Your Key Skills from Resume - Harish\n")
        f.write(f"# Automatically extracted {len(profile_skills)} skills from PDF resume\n\n")
        
        f.write("skills:\n")
        for skill in profile_skills:
            clean_skill = re.sub(r'[^a-zA-Z0-9\s]', '', skill).lower()
            clean_skill = ' '.join(clean_skill.split())
            
            if clean_skill:
                f.write(f"  - {clean_skill}\n")
    
    print(f"\n{'=' * 80}")
    print("✓ Generated updated profile.yaml with", len(profile_skills), "skills!")
    print(f"  Location: {OUTPUT_PROFILE}\n")
    
except FileNotFoundError:
    print(f"❌ Error: Resume file '{RESUME_FILE}' not found in repository")
    print("\nMake sure the resume PDF is committed to the repository root directory.")
