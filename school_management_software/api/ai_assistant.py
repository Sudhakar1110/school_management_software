import frappe
from frappe import _
import json

def _get_ai_settings():
    """Get AI configuration"""
    settings = frappe.get_single("AI Settings")
    if not settings.enable_ai:
        frappe.throw(_("AI features are not enabled. Enable in AI Settings."))
    return settings


def _call_ai_api(prompt, system_message=None):
    """Call the configured AI API"""
    settings = _get_ai_settings()
    
    if not settings.api_key:
        frappe.throw(_("AI API Key not configured. Set it in AI Settings."))
    
    if settings.provider == "OpenAI":
        return _call_openai(settings, prompt, system_message)
    elif settings.provider == "Anthropic Claude":
        return _call_anthropic(settings, prompt, system_message)
    else:
        frappe.throw(_("Provider '{0}' not yet supported").format(settings.provider))


def _call_openai(settings, prompt, system_message=None):
    """Call OpenAI API"""
    import requests
    
    try:
        headers = {
            "Authorization": "Bearer {0}".format(settings.api_key),
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": settings.model or "gpt-4o-mini",
            "messages": messages,
            "max_tokens": settings.max_tokens or 2000,
            "temperature": settings.temperature or 0.7
        }
        
        url = settings.api_base_url or "https://api.openai.com/v1/chat/completions"
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        frappe.log_error(title="OpenAI API Error", message=str(e))
        frappe.throw(_("AI API call failed: {0}").format(str(e)))


def _call_anthropic(settings, prompt, system_message=None):
    """Call Anthropic Claude API"""
    try:
        import requests
        
        headers = {
            "x-api-key": settings.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": settings.model or "claude-3-haiku-20240307",
            "max_tokens": settings.max_tokens or 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_message:
            data["system"] = system_message
        
        url = settings.api_base_url or "https://api.anthropic.com/v1/messages"
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]
    
    except Exception as e:
        frappe.log_error(title="Anthropic API Error", message=str(e))
        frappe.throw(_("AI API call failed: {0}").format(str(e)))


@frappe.whitelist()
def ask_assistant(question, context_doctype=None, context_docname=None):
    """Natural language Q&A about school data"""
    settings = frappe.get_single("AI Settings")
    if not settings.enable_ai or not settings.enable_chatbot:
        frappe.throw(_("AI Assistant is not enabled"))
    
    # Gather context if a specific document is referenced
    context_info = ""
    if context_doctype and context_docname:
        try:
            doc = frappe.get_doc(context_doctype, context_docname)
            context_info = "\nContext from {0} '{1}':\n{2}".format(
                context_doctype, context_docname,
                json.dumps(doc.as_dict(), default=str, indent=2)[:2000]
            )
        except Exception:
            context_info = "\n(Unable to fetch context document)"
    
    system_message = (
        "You are an AI assistant for a school management system built on ERPNext. "
        "Your role is to help school administrators find information, understand data, "
        "and perform tasks. Answer questions clearly and concisely based on the context provided. "
        "If you don't know the answer, say so. Do not make up information."
    )
    
    prompt = (
        "Question: {0}\n"
        "Context: The user is accessing an ERPNext Education system with modules for "
        "Admissions, Attendance, Fees, Exams, Hostel, Transport, Library, Events, "
        "Certificates, and HR.\n{1}\n"
        "Please answer the question based on the context provided."
    ).format(question, context_info)
    
    response = _call_ai_api(prompt, system_message)
    return {"answer": response}


@frappe.whitelist()
def grade_subjective_answer(question, student_answer, rubric=None, max_score=10):
    """AI-powered grading for subjective answers"""
    settings = frappe.get_single("AI Settings")
    if not settings.enable_ai or not settings.enable_grading:
        frappe.throw(_("AI Grading is not enabled"))
    
    system_message = (
        "You are an AI grading assistant for a school. Grade the student's answer "
        "fairly and provide constructive feedback. Be specific about what was correct "
        "and what could be improved."
    )
    
    prompt = (
        "Question: {0}\n\n"
        "Student's Answer: {1}\n\n"
        "Maximum Score: {2}\n"
    ).format(question, student_answer, max_score)
    
    if rubric:
        prompt += "Rubric/Guidelines: {0}\n".format(rubric)
    
    prompt += (
        "\nPlease provide:\n"
        "1. Score (out of {0})\n"
        "2. Feedback (strengths and areas for improvement)\n"
        "3. Suggested model answer"
    ).format(max_score)
    
    response = _call_ai_api(prompt, system_message)
    return {"result": response}


@frappe.whitelist()
def generate_quiz(topic, difficulty="Medium", num_questions=5, question_type="Multiple Choice"):
    """AI-generated quiz questions"""
    settings = frappe.get_single("AI Settings")
    if not settings.enable_ai or not settings.enable_content_generation:
        frappe.throw(_("AI Content Generation is not enabled"))
    
    system_message = (
        "You are an AI content creator for a school. Generate educational quiz questions "
        "that are age-appropriate and curriculum-aligned. Provide questions with clear "
        "correct answers and explanations."
    )
    
    prompt = (
        "Generate {0} {1} questions on the topic '{2}' at {3} difficulty level.\n\n"
        "For each question provide:\n"
        "- Question text\n"
        "- Options (for MCQ)\n"
        "- Correct answer\n"
        "- Brief explanation\n\n"
        "Format as structured JSON array."
    ).format(num_questions, question_type, topic, difficulty)
    
    response = _call_ai_api(prompt, system_message)
    return {"questions": response}


@frappe.whitelist()
def generate_report_card_remark(student_name, performance_summary):
    """AI-generated report card remarks"""
    settings = frappe.get_single("AI Settings")
    if not settings.enable_ai or not settings.enable_report_card_remarks:
        frappe.throw(_("AI Report Card Remarks are not enabled"))
    
    system_message = (
        "You are a school teacher writing report card remarks. Write encouraging, "
        "constructive, and personalized remarks for students. Be specific about subjects "
        "and areas of improvement. Keep remarks to 2-3 sentences."
    )
    
    prompt = (
        "Student: {0}\n"
        "Performance Summary: {1}\n\n"
        "Write a personalized report card remark for this student."
    ).format(student_name, performance_summary)
    
    response = _call_ai_api(prompt, system_message)
    return {"remark": response}
