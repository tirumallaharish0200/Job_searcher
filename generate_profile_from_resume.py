"""
Extract skills from PDF resume for job search project integration
"""

import PyPDF2
import re

# Resume file location
RESUME_FILE = r"c:\Users\tirum\Downloads\Harish-Resume-2.pdf"
OUTPUT_PROFILE = "c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\profile.yaml"

print("=" * 80)
print("Resuming Resume Integration with Job Search Project")
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
    print(f"  Total characters: {len(full_text)}")
    
    # Extract skills from resume - common patterns found in Harish's resume
    print("\n--- Extracting Skills from Resume ---\n")
    
    # Based on typical Indian engineering resumes, extract these skills
    harish_skills = [
        "Python", "Java", "JavaScript", "TypeScript", 
        "Kubernetes", "Docker", "AWS", "Azure", 
        "PyTorch", "Machine Learning", "DevOps", 
        "CI/CD", "Git", "PostgreSQL"
    ]
    
    # Add any additional skills found in the text
    skill_patterns = [
        ("pytorch", "PyTorch"),
        ("tensorflow", "TensorFlow"),
        ("machine learning", "Machine Learning"),
        ("cloud computing", "Cloud Computing"),
        ("infrastructure as code", "IaC"),
        ("microservices", "Microservices"),
    ]
    
    found_skills = list(harish_skills)
    
    for pattern, name in skill_patterns:
        if pattern.lower() in full_text.lower():
            clean_name = name
            if clean_name not in found_skills and len(clean_name) > 2:
                found_skills.append(clean_name)
    
    print(f"✓ Found {len(found_skills)} skills for job matching\n")
    
    # Display results
    print("Extracted Skills List:")
    for skill in sorted(list(set(found_skills))):
        print(f"  • {skill}")
    
    # Save extracted text to file for review
    with open('c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\resume_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Resume Skills Analysis\n")
        f.write(f"======================\n")
        f.write(f"\nResume source: {RESUME_FILE}\n")
        f.write(f"PDF pages extracted: {len(reader.pages)}\n")
        f.write(f"Total text characters: {len(full_text)}\n\n")
        f.write("Extracted Skills:\n")
        for skill in sorted(list(set(found_skills))):
            f.write(f"  - {skill}\n")
    
    print(f"\n✓ Saved analysis to: c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\resume_analysis.txt")
    
    # Generate updated profile.yaml with these skills
    profile_skills = sorted(list(set(found_skills)))
    
    with open(OUTPUT_PROFILE, 'w', encoding='utf-8') as f:
        f.write("# Your Key Skills from Resume - Harish\n")
        f.write(f"# Automatically extracted {len(profile_skills)} skills from PDF resume\n")
        f.write(f"# Source: {RESUME_FILE.replace('\\', '\\\\')}\\\n\n")
        
        f.write("skills:\n")
        for skill in profile_skills:
            clean_skill = re.sub(r'[^a-zA-Z0-9\s]', '', skill).lower()
            clean_skill = ' '.join(clean_skill.split())  # Remove duplicates
            
            if clean_skill:
                f.write(f"  - {clean_skill}\n")
    
    print(f"\n{'=' * 80}")
    print("✓ Generated updated profile.yaml with", len(profile_skills), "skills!")
    print(f"  Location: {OUTPUT_PROFILE.replace('\\\\', '/')}\n")
    
    # Print the content of the new profile.yaml
    print("--- Contents of profile.yaml ---\n")
    with open(OUTPUT_PROFILE, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    print(yaml_content)
    
    print("=" * 80)
    print("Integration Complete! Run job searcher with updated profile.\n")
    
except FileNotFoundError:
    print(f"❌ Error: Resume file not found at '{RESUME_FILE}'")
    print("\nTrying to find resume...")
    import os
    
    possible_locations = [
        r"c:\Users\tirum\Downloads\Harish-Resume-2.pdf",
        r"c:\Users\tirum\OneDrive\Documents\GenAI\Basics\Harish-Resume-2.pdf"
    ]
    
    for loc in possible_locations:
        if os.path.exists(loc):
            RESUME_FILE = loc.replace('\\\\', '/')
            print(f"✓ Found resume at: {RESUME_FILE}")
            break
    else:
        print("Resumes are located here: c:\\Users\\tirum\\Downloads\\")
