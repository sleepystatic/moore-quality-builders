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
    try:
        print("=== FORM SUBMISSION DEBUG ===")
        print(f"Email user: {os.getenv('MAIL_USERNAME')}")
        print(f"Has password: {bool(os.getenv('MAIL_PASSWORD'))}")
        print(f"Password length: {len(os.getenv('MAIL_PASSWORD', ''))}")
        print(f"Mail server: {app.config['MAIL_SERVER']}")
        print(f"Mail port: {app.config['MAIL_PORT']}")
        print(f"Use TLS: {app.config['MAIL_USE_TLS']}")
        print(f"Use SSL: {app.config['MAIL_USE_SSL']}")

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        project = request.form.get('project', '').strip()

        print(f"Form data received: {name}, {email}, {phone}")

        if not all([name, email, phone, project]):
            return jsonify({'status': 'error', 'message': 'All fields are required.'})

        if '@' not in email or '.' not in email:
            return jsonify({'status': 'error', 'message': 'Please enter a valid email address.'})

        print("Creating message...")
        msg = Message('New Estimate Request - Moore Quality Builders',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['mooreqbuilders@gmail.com'])

        msg.body = f"""
        New estimate request received:

        Name: {name}
        Email: {email}
        Phone: {phone}
        Project: {project}
        """

        print("Message created. Attempting to send email...")

        # Try to send with explicit error catching
        try:
            with app.app_context():
                mail.send(msg)
            print("Email sent successfully!")
            return jsonify({'status': 'success', 'message': 'Thank you! Your request has been sent.'})
        except Exception as send_error:
            print(f"SEND ERROR TYPE: {type(send_error).__name__}")
            print(f"SEND ERROR MESSAGE: {str(send_error)}")

            # Try to get more details
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"Exception type: {exc_type}")
            print(f"Exception value: {exc_value}")

            import traceback
            print("Full traceback:")
            traceback.print_exc()

            # Still return success to user
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