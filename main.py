from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI(
    title="HireIQ - Multimodal AI Interview Intelligence Platform",
    description="Backend API for job applications, authentication, and advanced AI-powered candidate and interview evaluation.",
    version="2.0.0"
)

class EvaluationRequest(BaseModel):
    resume_text: str
    interview_transcript: str

class QuestionRequest(BaseModel):
    job_role: str
    experience_level: str

class ResumeParseRequest(BaseModel):
    resume_text: str


@app.get("/")
def read_root():
    return {
        "message": "Welcome to HireIQ API - Multimodal AI Interview Intelligence Platform",
        "status": "Active & Fully Operational"
    }


# FEATURE 1: AI Interview Questions Generator
@app.post("/generate-interview-questions/")
def generate_questions(data: QuestionRequest):
    try:
        client = genai.Client()
        prompt = f"""
        You are an expert technical recruiter for 'HireIQ'. 
        Generate 5 core interview questions with expected key answers for the following role:
        - Job Role: {data.job_role}
        - Experience Level: {data.experience_level}
        
        Provide professional, industry-standard questions covering technical skills and problem-solving.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {
            "status": "success",
            "job_role": data.job_role,
            "interview_questions": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FEATURE 2: AI Resume Skill Extraction & Parsing
@app.post("/parse-resume/")
def parse_resume(data: ResumeParseRequest):
    try:
        client = genai.Client()
        prompt = f"""
        Analyze the following candidate resume text and extract:
        1. Primary Technical Skills
        2. Years of Estimated Experience
        3. Key Projects or Achievements
        4. Overall Profile Summary
        
        Resume Text:
        {data.resume_text}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {
            "status": "success",
            "resume_analysis": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FEATURE 3: Multimodal Candidate Evaluation (Interview Intelligence)
@app.post("/evaluate-candidate/")
def evaluate_candidate(data: EvaluationRequest):
    try:
        client = genai.Client()
        
        prompt = f"""
        You are an AI Interview Intelligence expert for 'HireIQ'. 
        Analyze the following candidate resume text and interview transcript/responses.
        
        Candidate Resume:
        {data.resume_text}
        
        Interview Transcript/Answers:
        {data.interview_transcript}
        
        Provide a comprehensive professional evaluation including:
        1. Overall Fit Score (out of 100)
        2. Key Technical Strengths
        3. Areas for Improvement / Red Flags
        4. Detailed Recommendation (Hire / Hold / Reject)
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        return {
            "status": "success",
            "ai_evaluation": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
