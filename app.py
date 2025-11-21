import socket

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Email configuration (using Gmail as example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Use app password, not regular password
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['TESTING'] = False

app.config['MAIL_TIMEOUT'] = 30


mail = Mail(app)


@app.before_request
def redirect_old_domain():
    """Redirect old domain to new domain with 301 status"""
    if request.host in ['moorequality.builders', 'www.moorequality.builders']:
        new_url = request.url.replace(request.host, 'moore-qualitybuilders.com')
        return redirect(new_url, code=301)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/blog/adu-construction-san-diego-guide')
def blog_adu():
    return render_template('blog-post-adu.html')


@app.route('/gallery')
def gallery():
    import os

    # Define gallery categories
    categories = {
        'kitchens': 'Kitchen Remodeling Projects',
        'bathrooms': 'Bathroom Renovation Projects',
        'decks': 'Deck Construction Projects',
        'doors': 'Doors & Windows Projects',
        'custom': 'Custom Construction Projects'
    }

    # Default descriptions for each category
    descriptions = {
        'kitchens': 'Kitchen Remodel',
        'bathrooms': 'Bathroom Renovation',
        'decks': 'Deck Construction',
        'doors': 'Door & Window Installation',
        'custom': 'Custom Construction Work'
    }

    gallery_data = {}

    # Get images from each category folder
    for category, title in categories.items():
        folder_path = os.path.join('static', 'images', 'gallery', category)
        images = []

        # Check if folder exists
        if os.path.exists(folder_path):
            # Get all jpg/jpeg/png files
            files = sorted([f for f in os.listdir(folder_path)
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

            for filename in files:
                images.append({
                    'path': f'/static/images/gallery/{category}/{filename}',
                    'alt': f'{descriptions[category]} San Diego',
                    'title': descriptions[category],
                    'description': 'Professional craftsmanship'
                })

        gallery_data[category] = {
            'title': title,
            'images': images
        }

    return render_template('gallery.html', gallery_data=gallery_data)


@app.route('/submit-estimate', methods=['POST'])
def submit_estimate():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    project = request.form.get('project', '').strip()

    if not all([name, email, phone, project]):
        return jsonify({'status': 'error', 'message': 'All fields are required.'})

    try:
        print("=== USING RAW SMTP ===")
        print(f"Connecting to smtp.gmail.com:587...")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = os.getenv('MAIL_USERNAME')
        msg['To'] = 'mooreqbuilders@gmail.com'
        msg['Subject'] = 'New Estimate Request - Moore Quality Builders'

        body = f"""
        New estimate request received:

        Name: {name}
        Email: {email}
        Phone: {phone}
        Project: {project}
        """
        msg.attach(MIMEText(body, 'plain'))

        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)

        print("Starting TLS...")
        server.starttls()

        print("Logging in...")
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))

        print("Sending message...")
        server.send_message(msg)

        print("Closing connection...")
        server.quit()

        print("Email sent successfully via raw SMTP!")
        return jsonify({'status': 'success', 'message': 'Thank you! Your request has been sent.'})

    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"SMTP AUTH ERROR: {auth_error}")
        print("This means Gmail rejected your credentials")
        return jsonify({'status': 'success', 'message': 'Thank you! We received your request.'})

    except smtplib.SMTPException as smtp_error:
        print(f"SMTP ERROR: {type(smtp_error).__name__}")
        print(f"SMTP ERROR MESSAGE: {smtp_error}")
        return jsonify({'status': 'success', 'message': 'Thank you! We received your request.'})

    except Exception as e:
        print(f"GENERAL ERROR: {type(e).__name__}")
        print(f"ERROR MESSAGE: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'success', 'message': 'Thank you! We received your request.'})

    except Exception as outer_error:
        print(f"OUTER ERROR: {type(outer_error).__name__}")
        print(f"OUTER ERROR MESSAGE: {str(outer_error)}")

        import traceback
        traceback.print_exc()

        return jsonify({'status': 'success', 'message': 'Thank you! We received your request.'})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)