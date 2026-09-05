import requests
import json
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:1.5b"

def get_ai_response(prompt, system_prompt="You are an expert career counselor for Indian engineering students."):
    """Send a prompt to local Ollama instance and return the response."""
    try:
        payload = {
            "model": DEFAULT_MODEL,
            "prompt": f"{system_prompt}\n\nUser Question: {prompt}",
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "No response from AI.")
    except Exception as e:
        print(f"Ollama Error: {e}")
        return None

def get_personalized_recommendations(student_data, probability):
    """Generate dynamic career advice based on the student's profile."""
    prompt = f"""
    Analyze the following student profile and provide 3-4 highly specific, actionable career recommendations.
    
    Profile:
    - CGPA: {student_data.get('cgpa')}
    - Internships: {student_data.get('internships')}
    - Projects: {student_data.get('projects')}
    - Aptitude Score: {student_data.get('aptitude_score')}/100
    - Soft Skills: {student_data.get('soft_skills')}/5
    - Backlogs: {student_data.get('backlogs')}
    - Placement Training: {student_data.get('placement_training')}
    - Current Placement Probability: {probability}%
    
    The student is looking for a placement in the IT/Engineering sector in India.
    Provide the response in a structured format with Title, Category, and Action Items.
    """
    
    response = get_ai_response(prompt)
    if not response:
        return None
        
    return response

def get_report_summary(student_data, result_data):
    """Generate a high-level executive summary for the placement report."""
    prompt = f"""
    Write a concise (2-3 sentences) executive summary for a student placement report.
    
    Student: {student_data.get('student_name', 'Student')}
    Placement Status: {result_data.get('prediction')} ({result_data.get('probability')}% probability)
    Key Strengths: {', '.join(result_data.get('top_positive', []))}
    Areas for Concern: {', '.join(result_data.get('top_negative', []))}
    Risk Score: {result_data.get('risk_score')}/100
    
    Synthesize these data points into a professional encouraging summary.
    """
    
    return get_ai_response(prompt)
