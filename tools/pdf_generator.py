from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(content, filename="VoyagerAI_TravelPlan.pdf"):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Voyager AI Travel Plan</b>", styles["Title"]))

    story.append(Paragraph(content.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(story)

    return filename