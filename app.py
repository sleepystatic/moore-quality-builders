import json
import logging
import os

from flask import Flask, render_template, jsonify, request, redirect, Response
from mailjet_rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

logging.basicConfig(level=logging.INFO)

# Shown to the visitor whenever we could not hand the lead off to Mailjet, so a
# failed send never looks like a successful one.
FALLBACK_MESSAGE = ("We couldn't send your request just now. "
                    "Please call us at (619) 807-1227 and we'll get right back to you.")



@app.route('/submit-estimate', methods=['POST'])
def submit_estimate():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    project = request.form.get('project', '').strip()

    # Honeypot: the matching field is hidden from people, so anything in it came
    # from a bot. Answer as though it worked rather than telling it what failed.
    if request.form.get('company', '').strip():
        app.logger.info('Discarded honeypot submission from %s', request.remote_addr)
        return jsonify({'status': 'success', 'message': 'Thank you! Your request has been sent.'})

    if not all([name, email, phone, project]):
        return jsonify({'status': 'error', 'message': 'All fields are required.'})

    if '@' not in email or '.' not in email:
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address.'})

    try:
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
                            "Email": "mooreqbuilders@gmail.com",
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

        if result.status_code == 200:
            app.logger.info('Estimate request sent for %s <%s>', name, email)
            return jsonify({'status': 'success', 'message': 'Thank you! Your request has been sent.'})

        try:
            detail = result.json()
        except Exception:
            detail = '<unparseable response body>'

        # Mailjet refused the send. Log the whole lead so it stays recoverable
        # from the server logs, then tell the visitor the truth.
        app.logger.error(
            'Mailjet rejected estimate request (HTTP %s): %s | LEAD name=%r email=%r phone=%r project=%r',
            result.status_code, detail, name, email, phone, project
        )
        return jsonify({'status': 'error', 'message': FALLBACK_MESSAGE})

    except Exception:
        app.logger.exception(
            'Estimate request failed to send | LEAD name=%r email=%r phone=%r project=%r',
            name, email, phone, project
        )
        return jsonify({'status': 'error', 'message': FALLBACK_MESSAGE})


@app.before_request
def redirect_old_domain():
    """Redirect old domain to new domain with 301 status"""
    if request.host in ['moorequality.builders', 'www.moorequality.builders']:
        new_url = request.url.replace(request.host, 'moore-qualitybuilders.com')
        return redirect(new_url, code=301)


@app.route('/')
def index():
    return render_template('index.html', reviews=REVIEWS)


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/blog/adu-construction-san-diego-guide')
def blog_adu():
    return render_template('blog-post-adu.html')


@app.route('/blog/kitchen-remodel-cost-guide')
def blog_kitchen_remodel():
    return render_template('blog-post-kitchenremodel.html')


@app.route('/blog/bathroom-remodel-cost-guide')
def blog_bathroom_remodel():
    return render_template('blog-post-bathroomremodel.html')


@app.route('/blog/home-remodeling-permit-guide')
def blog_permit_guide():
    return render_template('blog-post-permitguide.html')


# Customer reviews. These were ~100 lines of duplicated markup in index.html.
# Text is verbatim -- including the two typos in the first one -- because these
# are real customers' words.
#
# rating: number of stars shown on the card, confirmed by the client as the
# reviewers' actual ratings.
REVIEWS = [
    {
        "name": "Pam F.",
        "location": "San Diego, CA",
        "rating": 5,
        "quote": (
            "Moore Quality Builders did a complete remodel of our home and garage in Point Loma, San "
            "Diego. The house was in serious need of structural and cosmetic upgrades from foundation to "
            "roof line. Mike Moore is a serious full-Ame builder. He is very professional and knowledgeable in "
            "construction design and implementation and solving problems including deferred maintenance, "
            "bringing a structure up to code, updating and modernizing infrastructure and systems including "
            "plumbing, electrical, roofing, framing, windows, floors, interiors and exteriors. We especially "
            "appreciate his keen design sense and suggestions while he also listened and delivered what we "
            "asked for when we made suggestions and decisions. Mike and his crew are very peculiar about "
            "quality details. Corners are perfect, floors are level, measurements are exact and nothing is left "
            "unfinished. Mike Moore is very proactive and easy to work with. He brings solutions and "
            "suggestions to the table and worked with us to make each decision fit our vision and his "
            "exact standards. Mike Moore and crew show up every day. They work hard all day and clean "
            "up the job site at the end of each day. They are respectful of neighbors and became well known "
            "and well liked in our neighborhood. It was a pleasure to work with Mike Moore and his crews. "
            "We highly recommend Moor Quality Builders for residential building, remodeling, repairs and "
            "maintenance. "
        ),
    },
    {
        "name": "Allan Farwe",
        "location": "San Diego, CA",
        "rating": 5,
        "quote": (
            "I engaged Michael and his team to do some wall related repair work at my SD home. "
            "From the first call he was responsive and timely. It is rare these days that contractors respond to texts or emails quickly. "
            "Michael did, and was on time for every meeting. "
            "The work started and finished on time and on budget. He even did a few things out of scope while he had the equipment available. "
            " "
            "Best building/contractor experience I have had. "
            "He's a real pro and the finished product was better than I had hoped. "
            " "
            "Great guy-- solid company. "
        ),
    },
    {
        "name": "Anna Marie",
        "location": "Sand and Sea Realty - San Diego, CA",
        "rating": 5,
        "quote": (
            "I hired Michael to remodel my bathroom after one meeting.  I was so impressed with is eye for detail and his desire to do a great job.  He is a perfectionist and he always has the clients needs at the top of his mind.  He made sure I put the exhaust fan in a spot not too noticeable yet highly functional and lighting in the right place so that there wouldn't be shadows on my face while getting ready in the mirror.  I don't know any other contractors so conscientious and I know a lot of them. "
            " "
            "He is was always on time (usually early but waiting out side until the exact time), he was clean, fast, great workmanship, easy to work with, creative with ideas to make the project better and his prices are very reasonable. "
            " "
            "He is one you will be happy to refer to your friends and family and I have referred him several times.  Could write more but happy to talk to anyone. "
        ),
    },
    {
        "name": "Jen L.",
        "location": "San Diego, CA",
        "rating": 5,
        "quote": (
            "Michael is so easy to work with: he is reliable, reasonable, and comes up with both the most efficient yet design forward ideas.  He has done multiple project on my house including renovating my bathroom.  He thoroughly explains process and leaves workspace clean. "
        ),
    },
    {
        "name": "Isabella L.",
        "location": "San Diego, CA",
        "rating": 5,
        "quote": (
            "My family and I needed a simple fence put in, and Moore Quality Builders were on the job. Michael is a friendly face with a good work ethic and meticulous craft. He takes his work seriously and charges very fairly. My family all loved him and his beautiful fence installment. I recommend him for any task, big and small, and I commend him on his attention to detail while also working quickly. Efficient and professional craft. "
        ),
    },
    {
        "name": "Sarah B.",
        "location": "San Francisco, CA",
        "rating": 5,
        "quote": (
            "Super professional, and skilled!  Cleaned up at job end.  Kind and patient with senior citizen home owner. "
        ),
    },
]


GALLERY_CATEGORIES = {
    'kitchens': ('Kitchen Remodeling Projects', 'Kitchen Remodel'),
    'bathrooms': ('Bathroom Renovation Projects', 'Bathroom Renovation'),
    'decks': ('Deck Construction Projects', 'Deck Construction'),
    'doors': ('Doors & Windows Projects', 'Door & Window Installation'),
    'custom': ('Custom Construction Projects', 'Custom Construction Work'),
}

THUMB_MANIFEST_PATH = os.path.join('static', 'images', 'gallery-thumbs', 'manifest.json')

_gallery_cache = None


def _load_thumb_manifest():
    """Thumbnail dimensions written by tools/make_thumbs.py, keyed 'category/filename'."""
    try:
        with open(THUMB_MANIFEST_PATH) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        app.logger.warning('No gallery thumbnail manifest at %s; serving originals.',
                           THUMB_MANIFEST_PATH)
        return {}


def _build_gallery_data():
    """Scan the gallery folders once and pair each original with its thumbnail.

    A photo dropped into static/images/gallery/ still shows up without running
    tools/make_thumbs.py -- it just falls back to serving the original until the
    thumbnails are regenerated.
    """
    manifest = _load_thumb_manifest()
    gallery_data = {}

    for category, (title, description) in GALLERY_CATEGORIES.items():
        folder_path = os.path.join('static', 'images', 'gallery', category)
        thumb_dir = os.path.join('static', 'images', 'gallery-thumbs', category)
        images = []

        if os.path.isdir(folder_path):
            files = sorted(f for f in os.listdir(folder_path)
                           if f.lower().endswith(('.jpg', '.jpeg', '.png')))

            for filename in files:
                full = f'/static/images/gallery/{category}/{filename}'
                stem = os.path.splitext(filename)[0]
                size = manifest.get(f'{category}/{filename}')

                has_thumbs = (os.path.exists(os.path.join(thumb_dir, stem + '.webp'))
                              and os.path.exists(os.path.join(thumb_dir, stem + '.jpg')))
                if has_thumbs:
                    thumb_webp = f'/static/images/gallery-thumbs/{category}/{stem}.webp'
                    thumb_jpg = f'/static/images/gallery-thumbs/{category}/{stem}.jpg'
                else:
                    thumb_webp = thumb_jpg = full
                    size = None

                images.append({
                    'path': full,
                    'thumb_webp': thumb_webp,
                    'thumb_jpg': thumb_jpg,
                    'width': size[0] if size else None,
                    'height': size[1] if size else None,
                    'alt': f'{description} San Diego',
                    'title': description,
                    'description': 'Professional craftsmanship',
                })

        gallery_data[category] = {'title': title, 'images': images}

    return gallery_data


@app.route('/gallery')
def gallery():
    global _gallery_cache
    # The folders only change on deploy, so scan once. Debug reloads every time
    # so new photos appear while working locally.
    if _gallery_cache is None or app.debug:
        _gallery_cache = _build_gallery_data()
    return render_template('gallery.html', gallery_data=_gallery_cache)


SITE_ORIGIN = 'https://moore-qualitybuilders.com'

# Pages that should never appear in the sitemap.
SITEMAP_EXCLUDE = {'static', 'submit_estimate', 'sitemap', 'robots', 'not_found_error'}


@app.route('/sitemap.xml')
def sitemap():
    """Built from the URL map, so adding a route adds it to the sitemap.

    index.html has linked to /sitemap.xml all along, but no route served it.
    """
    urls = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint in SITEMAP_EXCLUDE:
            continue
        if 'GET' not in (rule.methods or set()):
            continue
        if rule.arguments:  # nothing dynamic to enumerate
            continue
        priority = '1.0' if rule.rule == '/' else '0.8'
        urls.append((SITE_ORIGIN + rule.rule, priority))

    urls.sort()
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority in urls:
        body.append('  <url><loc>%s</loc><changefreq>monthly</changefreq>'
                    '<priority>%s</priority></url>' % (loc, priority))
    body.append('</urlset>')

    return Response('\n'.join(body), mimetype='application/xml')


@app.route('/robots.txt')
def robots():
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /submit-estimate',
        '',
        'Sitemap: %s/sitemap.xml' % SITE_ORIGIN,
    ]
    return Response('\n'.join(lines), mimetype='text/plain')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    # Render supplies PORT; locally it falls back to 5000.
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=True, host='0.0.0.0', port=port)