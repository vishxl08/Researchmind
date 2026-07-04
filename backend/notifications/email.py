from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_report_email(user, report):
    subject = f"ResearchMind Completed: {report.title}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@researchmind.com')
    to = user.email
    
    if not to:
        print(f"Skipping email to user {user.username} as they have no email address.")
        return False
        
    context = {
        'user': user,
        'report': report,
        'url': f"http://localhost:5173/reports/{report.id}"
    }
    
    html_content = render_to_string('report_email.html', context)
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
