from google import genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path




# =========================================================
# EXECUTIVE REPORT GENERATOR (CHAT CLIENT STYLE)
# =========================================================
class ExecutiveReportGenerator:
    def __init__(self, api_key: str, model_name="gemini-2.5-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.chat = self.client.chats.create(model=model_name)

    # =========================================================
    # PROMPT BUILDER
    # =========================================================
    def build_prompt(self, raw_report: str) -> str:
        return f"""
You are a senior business analyst.

Based on the following insights report, generate a concise EXECUTIVE REPORT.

Requirements:
- Maximum length: 1 page
- Clear, structured, and professional tone
- Be concise and prioritize high-impact insights

Structure:
1. Executive Summary (top 3-5 critical findings)
2. Insights by Category (summarized)
3. Actionable Recommendations (linked to findings)

Formatting rules:
- Use clear section headers
- Use bullet points when appropriate
- Avoid redundancy

INPUT REPORT:
{raw_report}
"""

    # =========================================================
    # LLM CALL (CHAT STYLE)
    # =========================================================
    def generate_text(self, raw_report: str) -> str:
        prompt = self.build_prompt(raw_report)
        response = self.chat.send_message(prompt)
        return response.text.strip()

    # =========================================================
    # PDF GENERATION
    # =========================================================
    def save_pdf(self, text: str, output_path: str):
        #Ensure directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(output_path))
        styles = getSampleStyleSheet()

        elements = []

        for line in text.split("\n"):
            line = line.strip()

            if not line:
                elements.append(Spacer(1, 10))
                continue

            elements.append(Paragraph(line, styles["Normal"]))
            elements.append(Spacer(1, 8))

        doc.build(elements)

    # =========================================================
    # MAIN EXECUTION
    # =========================================================
    def run_from_text(self, raw_report: str, output_pdf_path: str):
        print("[INFO] Generating executive report with LLM...")
        
        exec_text = self.generate_text(raw_report)

        print("[INFO] Saving PDF...")
        self.save_pdf(exec_text, output_pdf_path)

        print(f"[SUCCESS] Executive report saved to: {output_pdf_path}")