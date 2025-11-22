import socket

from flask import Flask, render_template, jsonify, request
from mailjet_rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')



@app.route('/submit-estimate', methods=['POST'])
def submit_estimate():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    project = request.form.get('project', '').strip()

    if not all([name, email, phone, project]):
        return jsonify({'status': 'error', 'message': 'All fields are required.'})

    if '@' not in email or '.' not in email:
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address.'})

    try:
        print("=== SENDING VIA MAILJET ===")

        # Initialize Mailjet client
        mailjet = Client(
            auth=(os.getenv('MAILJET_API_KEY'), os.getenv('MAILJET_SECRET_KEY')),
            version='v3.1'
        )

        # Prepare email data
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "t.bryan.dev@gmail.com",
                        "Name": "Moore Quality Builders Website"
                    },
                    "To": [
                        {
                            "Email": "t.bryan.dev@gmail.com",
                            "Name": "Moore Quality Builders"
                        }
                    ],
                    "Subject": "New Estimate Request - Moore Quality Builders",
                    "HTMLPart": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: #e67e22; color: white; padding: 20px; text-align: center;">
                            <h1 style="margin: 0;">New Estimate Request</h1>
                        </div>
                        <div style="padding: 30px; background: #f9f9f9;">
                            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                                <p style="margin: 5px 0;"><strong>Name:</strong> {name}</p>
                                <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                                <p style="margin: 5px 0;"><strong>Phone:</strong> {phone}</p>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 8px;">
                                <p style="margin: 0 0 10px 0;"><strong>Project Description:</strong></p>
                                <p style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 0;">{project}</p>
                            </div>
                        </div>
                        <div style="background: #2c3e50; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p style="margin: 0;">Moore Quality Builders | CA License #882168</p>
                        </div>
                    </div>
                    """
                }
            ]
        }

        # Send email
        result = mailjet.send.create(data=data)

        print(f"✅ Mailjet Response Status: {result.status_code}")
        print(f"Response: {result.json()}")

        if result.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Thank you! Your request has been sent.'})
        else:
            print(f"❌ Mailjet error: {result.json()}")
            return jsonify({'status': 'success', 'message': 'Thank you! We received your request.'})

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'success', 'message': 'Thank you! We received your request.'})


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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)