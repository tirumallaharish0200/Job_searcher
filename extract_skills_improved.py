"""
Extract skills from resume with improved pattern matching
"""

import PyPDF2
import re

# Read the PDF resume
pdf_path = r"c:\Users\tirum\Downloads\Harish-Resume-2.pdf"

# More comprehensive skill patterns to search for
skill_patterns = [
    # Programming languages
    ("python", "Python"),
    ("java", "Java"),
    ("javascript", "JavaScript"),
    ("typescript", "TypeScript"),
    ("c++", "C++"),
    ("go", "Go"),
    ("rust", "Rust"),
    ("ruby", "Ruby"),
    ("php", "PHP"),
    ("scala", "Scala"),
    
    # Frameworks & Libraries
    ("pytorch", "PyTorch"),
    ("tensorflow", "TensorFlow"),
    ("scikit-learn", "Scikit-Learn"),
    ("flask", "Flask"),
    ("django", "Django"),
    ("spring-boot", "Spring Boot"),
    ("express", "Express"),
    ("react", "React"),
    ("angular", "Angular"),
    
    # Cloud platforms
    ("aws", "AWS"),
    ("azure", "Azure"),
    ("gcp", "GCP"),
    ("google cloud", "Google Cloud"),
    
    # Containerization & Orchestration
    ("kubernetes", "Kubernetes"),
    ("docker", "Docker"),
    ("containerd", "Containerd"),
    
    # CI/CD & DevOps
    ("jenkins", "Jenkins"),
    ("gitlab-ci", "GitLab CI"),
    ("github actions", "GitHub Actions"),
    ("cicd", "CI/CD"),
    ("prometheus", "Prometheus"),
    ("grafana", "Grafana"),
    
    # Database & Storage
    ("postgresql", "PostgreSQL"),
    ("mysql", "MySQL"),
    ("redis", "Redis"),
    ("mongodb", "MongoDB"),
    ("cassandra", "Cassandra"),
    
    # ML/AI
    ("machine learning", "Machine Learning"),
    ("deep learning", "Deep Learning"),
    ("nlp", "NLP"),
    ("llm", "LLM"),
    ("computer vision", "Computer Vision"),
]

try:
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        # Concatenate all text from all pages
        full_text = ''
        for page in reader.pages:
            extracted_text = page.extract_text() or ''
            if extracted_text:
                full_text += ' ' + extracted_text
        
    print("=" * 80)
    print(f"Resume Extracted Successfully!")
    print(f"Total characters: {len(full_text)}")
    
    # Find skills in the text
    found_skills = []
    matched_skills = set()
    
    for pattern, name in skill_patterns:
        if pattern.lower() in full_text.lower():
            clean_name = f"{name}"
            if clean_name not in matched_skills and len(clean_name) > 2:
                found_skills.append(clean_name)
                matched_skills.add(clean_name)
    
    # Add any other potential skills found (e.g., specific technologies mentioned)
    text_lower = full_text.lower()
    additional_patterns = [
        ('cloud computing', 'Cloud Computing'),
        ('infrastructure as code', 'IaC'),
        ('microservices', 'Microservices'),
        ('devops', 'DevOps'),
        ('mlops', 'MLOps'),
    ]
    
    for pattern, name in additional_patterns:
        if pattern.lower() in text_lower:
            clean_name = f"{name}"
            if clean_name not in matched_skills and len(clean_name) > 2:
                found_skills.append(clean_name)
                matched_skills.add(clean_name)
    
    print(f"\n✓ Found {len(found_skills)} skills:\n")
    
    # Display results
    for skill in sorted(list(matched_skills)):
        print(f"  • {skill}")
    
    # Save extracted text to file for review
    with open('c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\resume_text_full.txt', 'w', encoding='utf-8') as f:
        f.write("Full Resume Text:\n")
        f.write(f"{'=' * 80}\n")
        # Keep first 2000 characters for readability
        f.write(full_text[:2000] + "...\n")
    
    print(f"\n✓ Saved full resume text to: resume_text_full.txt")
    
    # Generate updated profile.yaml
    with open('c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\profile.yaml', 'w', encoding='utf-8') as f:
        f.write("# Your Key Skills from Resume - Harish\n")
        f.write(f"# Automatically extracted {len(matched_skills)} skills from PDF resume\n")
        f.write("# Source: c:\\Users\\tirum\\Downloads\\Harish-Resume-2.pdf\n\n")
        
        f.write("skills:\n")
        for skill in sorted(list(matched_skills)):
            clean_skill = re.sub(r'[^a-zA-Z0-9\s]', '', skill).lower()
            clean_skill = ' '.join(clean_skill.split())  # Remove duplicates
            
            if clean_skill:
                f.write(f"  - {clean_skill}\n")
    
    print(f"\n✓ Updated profile.yaml with {len(matched_skills)} skills!")
    print(f"  Location: c:\\Users\\tirum\\OneDrive\\Documents\\GenAI\\Basics\\profile.yaml")
    print("\n" + "=" * 80)
    
except FileNotFoundError:
    print(f"❌ Error: Resume file not found at '{pdf_path}'")
    print("  Make sure the file is located at: c:\\Users\\tirum\\Downloads\\Harish-Resume-2.pdf")
except Exception as e:
    import traceback
    print(f"❌ Error extracting resume: {e}")
    traceback.print_exc()

# Run extraction
print("\n--- Analyzing Resume ---\n")
