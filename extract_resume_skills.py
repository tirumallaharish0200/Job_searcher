"""
Extract text from resume PDF and generate updated profile.yaml with skills
"""

import PyPDF2
import re

# Read the PDF resume
pdf_path = r"c:\Users\tirum\Downloads\Harish-Resume-2.pdf"
output_text_path = "c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\resume_skills.txt"
profile_yaml_path = "c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\profile.yaml"

try:
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text
        
    # Clean up and save the resume text
    with open(output_text_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"✓ Resume extracted successfully!")
    print(f"  Total characters: {len(text)}")
    print(f"  Saved to: {output_text_path}")
    
    # Try to extract skills from the resume text
    print("\n--- Extracting Skills from Resume ---\n")
    
    skill_patterns = [
        (r'(\S+)\s*Skills?:\s*(.+)', 'Technical Skills'),
        (r'(?:Programming|Languages):\s*(.+)', 'Programming Languages'),
        (r'(?:Framework(?:s)?|Libraries):\s*(.+)', 'Frameworks & Libraries'),
        (r'(?:Cloud|AWS|Azure|GCP):\s*(.+)', 'Cloud Platforms'),
        (r'(?:CI\/CD|DevOps|Containerization):\s*(.+)', 'DevOps Tools'),
    ]
    
    # Simple skill extraction - look for common skill names in the text
    all_skills = set()
    
    # Extract potential skills from text
    skill_keywords = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'Go', 'Rust',
        'Kubernetes', 'Docker', 'AWS', 'Azure', 'GCP', 'Terraform',
        'PyTorch', 'TensorFlow', 'Scikit-learn', 'Machine Learning', 'AI',
        'CI/CD', 'Jenkins', 'GitHub Actions', 'GitLab CI', 'Prometheus',
        'Kafka', 'Spark', 'Hadoop', 'Docker', 'Kubernetes', 'Terraform',
        'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Spring Boot',
    ]
    
    text_lower = text.lower()
    for keyword in skill_keywords:
        if keyword.lower() in text_lower:
            all_skills.add(keyword)
    
    # Write skills to a file for review
    with open(output_text_path, 'w') as f:
        f.write("Extracted Skills from Resume:\n")
        f.write(f"Total unique skills found: {len(all_skills)}\n\n")
        f.write('\n'.join(sorted(list(all_skills))) + '\n')
    
    print(f"\n✓ Found {len(all_skills)} potential skills:")
    for skill in sorted(list(all_skills)):
        print(f"  - {skill}")
    
    # Generate updated profile.yaml with these skills
    generate_profile_yaml(all_skills)
    
except FileNotFoundError:
    print(f"❌ Error: Resume file not found at '{pdf_path}'")
except Exception as e:
    print(f"❌ Error extracting resume: {e}")

def generate_profile_yaml(skill_set):
    """Generate updated profile.yaml with extracted skills."""
    
    # Your key skills (from the resume)
    profile_skills = sorted(list(skill_set))
    
    with open(profile_yaml_path, 'w', encoding='utf-8') as f:
        f.write("# Your Key Skills from Resume\n")
        f.write(f"# Generated automatically - {len(profile_skills)} skills found\n\n")
        
        f.write("skills:\n")
        for skill in profile_skills:
            # Clean up skill names (remove special characters, make lowercase)
            clean_skill = re.sub(r'[^a-zA-Z0-9\s]', '', skill).lower()
            clean_skill = ' '.join(clean_skill.split())  # Remove duplicates
            
            if clean_skill:
                f.write(f"  - {clean_skill}\n")
    
    print(f"\n✓ Generated updated profile.yaml with {len(profile_skills)} skills!")
    print(f"  File: {profile_yaml_path}")

# Run the extraction
print("Processing resume PDF...")
generate_profile_yaml(all_skills)
