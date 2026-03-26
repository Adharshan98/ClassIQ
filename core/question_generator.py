"""
core/question_generator.py
--------------------------
AI-powered question generator for ClassIQ.
Generates a theory-based question dynamically using Google's Gemini AI.
Falls back to a generic conceptual question if the API fails or is not configured.
"""

import os
import google.generativeai as genai

# Try to configure Gemini API if the key exists
_api_key = os.environ.get("GEMINI_API_KEY")
if _api_key:
    genai.configure(api_key=_api_key)

def generate_question(topic: str, difficulty: str = "Medium") -> str:
    """
    Generate a theory-based question that a teacher can ask a student.
    
    If Gemini API is configured and accessible, it uses Gemini to generate the question.
    Otherwise, it falls back to a locally generated basic question.
    """
    
    prompt = f"""
Instead of selecting a topic from a predefined dropdown list, the teacher will type any topic manually. The teacher will also specify a difficulty level.

Your task is to generate a theory-based question that the teacher can ask the student.

Input:
* Topic: {topic}
* Difficulty Level: {difficulty}

Instructions:
* Act as a teacher asking a student a question.
* The question must be purely theory-oriented (no coding or implementation).
* Focus on conceptual understanding, explanations, definitions, comparisons, or real-world applications.
* Adjust the depth based on difficulty:
  * Easy: Simple definitions or basic explanation
  * Medium: Conceptual understanding with reasoning or comparison
  * Hard: Deep analysis, critical thinking, or multi-part questions
* Generate only ONE main question.
* For Medium/Hard, you may include sub-parts like (a), (b), (c).
* The tone should be formal and academic, like in an exam or viva.

Output Format:

Teacher’s Question:
<clear, well-structured theory question>

Expected Answer Key Points:
* Point 1
* Point 2
* Point 3
"""
    
    if _api_key:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception:
            # Fall through to offline handling
            pass
            
    # Generic offline fallback if API fails or is not configured
    if difficulty.lower() == "easy":
        diff_str = "simple definitions or basic explanations"
    elif difficulty.lower() == "medium":
        diff_str = "conceptual understanding with reasoning or comparison"
    else:
        diff_str = "deep analysis, critical thinking, or multi-part questions"
        
    fallback_text = (
        f"**Teacher’s Question:**\n"
        f"Explain the core concepts of {topic} focusing on {diff_str}.\n\n"
        f"**Expected Answer Key Points:**\n"
        f"* Key definition or conceptual overview\n"
        f"* Real-world application or comparison\n"
        f"* Critical detail based on {difficulty} difficulty"
    )
    return fallback_text

