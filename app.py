from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bcrypt import hashpw, gensalt, checkpw
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Add context processor for datetime
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')  # Update to your AWS region

# DynamoDB Tables
users_table = dynamodb.Table('BeautySalon_Users')
beauticians_table = dynamodb.Table('BeautySalon_Beauticians')
appointments_table = dynamodb.Table('BeautySalon_Appointments')
client_records_table = dynamodb.Table('BeautySalon_ClientRecords')
contact_messages_table = dynamodb.Table('BeautySalon_ContactMessages')

# Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gtharunasri19@gmail.com"  # Update with your email
SENDER_PASSWORD = "umpb bimb pahp axmc"  # Update with your app password

# Sample Beautician Data
beautician_data = [
    {
        'beautician_id': '1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p',
        'name': 'Emma Johnson',
        'email': 'emma.johnson@glowbeauty.com',
        'specialty': 'Hair Styling & Coloring',
        'qualification': 'Certified Color Specialist, Advanced Hair Cutting',
        'experience': '8 years',
        'bio': 'Emma specializes in creating personalized hair color and styles that enhance your natural beauty. With an eye for detail and a passion for keeping up with the latest trends, she ensures every client leaves feeling confident and beautiful.',
        'phone': '555-123-4567',
        'available': True,
        'working_hours': '9:00 AM - 5:00 PM',
        'working_days': ['Monday', 'Tuesday', 'Wednesday', 'Friday', 'Saturday'],
        'languages': ['English', 'Spanish'],
        'photo_url': '/static/images/beauticians/emma_johnson.jpg',
        'rating': 4.9,
        'created_at': '2023-05-15 09:00:00'
    },
    {
        'beautician_id': '2b3c4d5e-6f7g-8h9i-0j1k-2l3m4n5o6p7q',
        'name': 'Sophia Martinez',
        'email': 'sophia.martinez@glowbeauty.com',
        'specialty': 'Skincare & Facials',
        'qualification': 'Licensed Esthetician, Certified in Advanced Facial Techniques',
        'experience': '6 years',
        'bio': 'Sophia is passionate about helping clients achieve their best skin. She specializes in personalized facial treatments and has extensive knowledge of skincare products and routines for all skin types and concerns.',
        'phone': '555-234-5678',
        'available': True,
        'working_hours': '10:00 AM - 6:00 PM',
        'working_days': ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Sunday'],
        'languages': ['English', 'Spanish', 'Portuguese'],
        'photo_url': '/static/images/beauticians/sophia_martinez.jpg',
        'rating': 4.8,
        'created_at': '2023-06-20 10:00:00'
    },
    {
        'beautician_id': '3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r',
        'name': 'James Wilson',
        'email': 'james.wilson@glowbeauty.com',
        'specialty': 'Men\'s Grooming & Beard Care',
        'qualification': 'Master Barber, Certified in Advanced Beard Styling',
        'experience': '10 years',
        'bio': 'James brings a decade of experience in men\'s grooming and styling. He specializes in precision haircuts, beard styling, and traditional hot towel shaves. His attention to detail ensures every client receives a personalized experience.',
        'phone': '555-345-6789',
        'available': True,
        'working_hours': '11:00 AM - 7:00 PM',
        'working_days': ['Monday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'languages': ['English'],
        'photo_url': '/static/images/beauticians/james_wilson.jpg',
        'rating': 4.9,
        'created_at': '2022-12-10 11:00:00'
    },
    {
        'beautician_id': '4d5e6f7g-8h9i-0j1k-2l3m-4n5o6p7q8r9s',
        'name': 'Olivia Chen',
        'email': 'olivia.chen@glowbeauty.com',
        'specialty': 'Nail Art & Manicures',
        'qualification': 'Certified Nail Technician, Specialized in Nail Art',
        'experience': '5 years',
        'bio': 'Olivia is known for her creative nail designs and meticulous attention to detail. Whether you want a classic manicure or elaborate nail art, she brings creativity and precision to every appointment.',
        'phone': '555-456-7890',
        'available': True,
        'working_hours': '9:00 AM - 5:00 PM',
        'working_days': ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'languages': ['English', 'Mandarin'],
        'photo_url': '/static/images/beauticians/olivia_chen.jpg',
        'rating': 4.7,
        'created_at': '2024-01-05 09:00:00'
    },
    {
        'beautician_id': '5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t',
        'name': 'Aisha Patel',
        'email': 'aisha.patel@glowbeauty.com',
        'specialty': 'Makeup & Bridal Services',
        'qualification': 'Professional Makeup Artist, Bridal Specialist',
        'experience': '7 years',
        'bio': 'Aisha specializes in creating flawless makeup looks for all occasions, with particular expertise in bridal makeup. She believes in enhancing natural beauty and creating looks that make her clients feel confident and radiant.',
        'phone': '555-567-8901',
        'available': True,
        'working_hours': '10:00 AM - 6:00 PM',
        'working_days': ['Monday', 'Tuesday', 'Friday', 'Saturday', 'Sunday'],
        'languages': ['English', 'Hindi', 'Gujarati'],
        'photo_url': '/static/images/beauticians/aisha_patel.jpg',
        'rating': 5.0,
        'created_at': '2023-08-20 10:00:00'
    },
    {
        'beautician_id': '6f7g8h9i-0j1k-2l3m-4n5o-6p7q8r9s0t1u',
        'name': 'Michael Brown',
        'email': 'michael.brown@glowbeauty.com',
        'specialty': 'Massage Therapy',
        'qualification': 'Licensed Massage Therapist, Specialized in Deep Tissue and Hot Stone Massage',
        'experience': '9 years',
        'bio': 'Michael provides therapeutic massage treatments tailored to each client's needs. Whether you need stress relief or help with muscle tension, his skilled techniques will leave you feeling relaxed and rejuvenated.',
        'phone': '555-678-9012',
        'available': True,
        'working_hours': '12:00 PM - 8:00 PM',
        'working_days': ['Tuesday', 'Wednesday', 'Thursday', 'Saturday', 'Sunday'],
        'languages': ['English', 'French'],
        'photo_url': '/static/images/beauticians/michael_brown.jpg',
        'rating': 4.9,
        'created_at': '2023-03-15 12:00:00'
    }
]

# Function to initialize beautician data in DynamoDB
def initialize_beautician_data():
    try:
        # Check if beauticians exist
        response = beauticians_table.scan(Limit=1)
        if 'Items' in response and len(response['Items']) > 0:
            print("Beautician data already exists, skipping initialization")
            return
        
        # Add sample beauticians to DynamoDB
        for beautician in beautician_data:
            beauticians_table.put_item(Item=beautician)
            
            # Create user accounts for beauticians with a default password
            hashed_password = hashpw("BeautyPro2025!".encode('utf-8'), gensalt()).decode('utf-8')
            users_table.put_item(
                Item={
                    'email': beautician['email'],
                    'name': beautician['name'],
                    'password': hashed_password,
                    'phone': beautician['phone'],
                    'user_type': 'beautician',
                    'registration_date': beautician['created_at']
                }
            )
        
        print("Sample beautician data initialized successfully")
    except Exception as e:
        print(f"Error initializing beautician data: {e}")


# Beauty tips data
beauty_tips = [
    {
        "title": "Stay Hydrated for Glowing Skin",
        "content": "Drink at least 8 glasses of water daily to keep your skin hydrated and maintain a natural glow.",
        "category": "Skincare"
    },
    {
        "title": "Natural Hair Mask",
        "content": "Mix honey, olive oil, and avocado for a nourishing hair mask that adds shine and repairs damage.",
        "category": "Hair Care"
    },
    {
        "title": "Proper Nail Care",
        "content": "Apply cuticle oil daily to maintain healthy nails and prevent brittleness.",
        "category": "Nail Care"
    },
    {
        "title": "DIY Face Scrub",
        "content": "Mix 1 tablespoon of brown sugar with honey for a gentle exfoliating scrub that removes dead skin cells.",
        "category": "DIY Beauty"
    },
    {
        "title": "Healthy Sleep Habits",
        "content": "Get 7-9 hours of quality sleep to reduce dark circles and promote skin cell regeneration.",
        "category": "Wellness"
    },
    {
        "title": "Sun Protection",
        "content": "Always wear SPF 30+ sunscreen, even on cloudy days, to prevent premature aging and protect your skin.",
        "category": "Skincare"
    }
]

# Common beauty concerns and advice
beauty_concerns = {
    "dry_skin": {
        "symptoms": "Flaky, tight, rough skin texture",
        "remedy": "Use hydrating serums with hyaluronic acid, apply moisturizer while skin is damp, and use facial oils at night",
        "when_to_see_professional": "If skin becomes irritated, red, or painful despite regular moisturizing"
    },
    "acne": {
        "symptoms": "Pimples, blackheads, oily skin",
        "remedy": "Cleanse twice daily, use products with salicylic acid or benzoyl peroxide, avoid touching face",
        "when_to_see_professional": "For persistent acne, deep cystic acne, or if over-the-counter treatments aren't working"
    },
    "hair_loss": {
        "symptoms": "Excessive shedding, thinning hair, receding hairline",
        "remedy": "Gentle hair care, balanced diet rich in protein and iron, reduce heat styling",
        "when_to_see_professional": "If hair loss is sudden or accompanied by scalp irritation"
    },
    "brittle_nails": {
        "symptoms": "Nails that crack, split, or break easily",
        "remedy": "Keep nails moisturized, use strengthening treatments, wear gloves when doing housework",
        "when_to_see_professional": "If nails show discoloration, thickening, or persistent splitting"
    }
}

# Function to send email
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Helper function to check if user is logged in
def is_logged_in():
    return 'user_email' in session

# Home route
@app.route('/')
def home():
    # Get random beauty tips to display on homepage
    random_tips = random.sample(beauty_tips, min(3, len(beauty_tips)))
    return render_template('index.html', tips=random_tips, is_logged_in=is_logged_in())

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        
        # Basic Validation
        if not name or not email or not password or not confirm_password or not phone:
            flash("All fields are mandatory! Please fill out the entire form.", "danger")
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash("Passwords do not match! Please try again.", "danger")
            return redirect(url_for('register'))

        # Check if user already exists
        response = users_table.get_item(Key={'email': email})
        if 'Item' in response:
            flash("User already exists! Please log in.", "info")
            return redirect(url_for('login'))

        # Hash the password
        hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

        # Store user in DynamoDB
        users_table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': hashed_password,
                'phone': phone,
                'user_type': 'client',  # Default role is client
                'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

        # Create an empty client record
        client_records_table.put_item(
            Item={
                'client_id': email,
                'name': name,
                'email': email,
                'phone': phone,
                'skin_type': '',
                'hair_type': '',
                'allergies': [],
                'preferences': [],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

        # Send welcome email
        welcome_message = f"Welcome to Glow Beauty Salon, {name}!\n\nThank you for registering with us. We're dedicated to providing you with the best beauty treatments and services."
        send_email(email, "Welcome to Glow Beauty Salon", welcome_message)
        
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html', is_logged_in=is_logged_in())

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Basic Validation
        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return redirect(url_for('login'))

        # Fetch user data from DynamoDB
        response = users_table.get_item(Key={'email': email})
        user = response.get('Item')

        if not user or not checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            flash("Incorrect email or password! Please try again.", "danger")
            return redirect(url_for('login'))

        # Store user info in session
        session['user_email'] = email
        session['user_name'] = user['name']
        session['user_type'] = user['user_type']
        
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for('home'))
        
    return render_template('login.html', is_logged_in=is_logged_in())

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

# About Page
@app.route('/about')
def about():
    return render_template('about.html', is_logged_in=is_logged_in())

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        # Store message in DynamoDB
        contact_messages_table.put_item(
            Item={
                'message_id': str(uuid.uuid4()),
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'submitted_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'new'
            }
        )
        
        # Send confirmation email
        confirmation_message = f"Dear {name},\n\nThank you for contacting Glow Beauty Salon. We have received your message and will get back to you soon.\n\nBest regards,\nGlow Beauty Salon Team"
        send_email(email, "Thank you for contacting Glow Beauty Salon", confirmation_message)
        
        # Send notification to salon staff
        admin_message = f"New contact message from {name} ({email})\nSubject: {subject}\n\nMessage:\n{message}"
        send_email(SENDER_EMAIL, f"New Contact Form Submission: {subject}", admin_message)
        
        flash("Your message has been sent! We'll get back to you soon.", "success")
        return redirect(url_for('contact'))
        
    return render_template('contact.html', is_logged_in=is_logged_in())

# Beauticians List Page
@app.route('/beauticians')
def beauticians_list():
    # Get all beauticians from DynamoDB
    response = beauticians_table.scan()
    beauticians = response.get('Items', [])
    
    # Sort beauticians by specialty for better organization
    beauticians.sort(key=lambda x: x.get('specialty', ''))
    
    return render_template('beauticians.html', beauticians=beauticians, is_logged_in=is_logged_in())

# Beautician Details Page
@app.route('/beautician/<beautician_id>')
def beautician_details(beautician_id):
    # Get beautician details from DynamoDB
    response = beauticians_table.get_item(Key={'beautician_id': beautician_id})
    beautician = response.get('Item')
    
    if not beautician:
        flash("Beautician not found!", "danger")
        return redirect(url_for('beauticians_list'))
        
    return render_template('beautician_details.html', beautician=beautician, is_logged_in=is_logged_in())

# Appointments Page
@app.route('/appointments')
def appointments():
    if not is_logged_in():
        flash("Please log in to view and book appointments.", "info")
        return redirect(url_for('login'))
    
    # Get user's appointments
    response = appointments_table.scan(
        FilterExpression=Attr('client_email').eq(session['user_email'])
    )
    user_appointments = response.get('Items', [])
    
    # Sort appointments by date/time
    user_appointments.sort(key=lambda x: x.get('appointment_datetime', ''))
    
    # Get all beauticians for appointment booking
    response = beauticians_table.scan()
    beauticians = response.get('Items', [])
    
    # Define available services
    services = [
        {'id': 'haircut', 'name': 'Haircut & Styling', 'duration': '60', 'price': '45'},
        {'id': 'coloring', 'name': 'Hair Coloring', 'duration': '120', 'price': '80'},
        {'id': 'facial', 'name': 'Facial Treatment', 'duration': '60', 'price': '55'},
        {'id': 'manicure', 'name': 'Manicure', 'duration': '45', 'price': '35'},
        {'id': 'pedicure', 'name': 'Pedicure', 'duration': '45', 'price': '40'},
        {'id': 'massage', 'name': 'Relaxing Massage', 'duration': '60', 'price': '65'},
        {'id': 'makeup', 'name': 'Professional Makeup', 'duration': '60', 'price': '60'},
        {'id': 'waxing', 'name': 'Waxing Service', 'duration': '30', 'price': '30'}
    ]
    
    return render_template('appointments.html', 
                          appointments=user_appointments, 
                          beauticians=beauticians,
                          services=services,
                          is_logged_in=is_logged_in())

# Book Appointment Route
@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    if not is_logged_in():
        flash("Please log in to book appointments.", "danger")
        return redirect(url_for('login'))
        
    beautician_id = request.form['beautician_id']
    service_id = request.form['service_id']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    special_requests = request.form.get('special_requests', '')
    
    # Basic validation
    if not beautician_id or not service_id or not appointment_date or not appointment_time:
        flash("All fields are required to book an appointment.", "danger")
        return redirect(url_for('appointments'))
    
    # Get beautician details
    response = beauticians_table.get_item(Key={'beautician_id': beautician_id})
    beautician = response.get('Item')
    
    if not beautician:
        flash("Selected beautician not found.", "danger")
        return redirect(url_for('appointments'))
    
    # Define services dictionary to look up service details
    services = {
        'haircut': {'name': 'Haircut & Styling', 'duration': '60', 'price': '45'},
        'coloring': {'name': 'Hair Coloring', 'duration': '120', 'price': '80'},
        'facial': {'name': 'Facial Treatment', 'duration': '60', 'price': '55'},
        'manicure': {'name': 'Manicure', 'duration': '45', 'price': '35'},
        'pedicure': {'name': 'Pedicure', 'duration': '45', 'price': '40'},
        'massage': {'name': 'Relaxing Massage', 'duration': '60', 'price': '65'},
        'makeup': {'name': 'Professional Makeup', 'duration': '60', 'price': '60'},
        'waxing': {'name': 'Waxing Service', 'duration': '30', 'price': '30'}
    }
    
    service = services.get(service_id)
    if not service:
        flash("Selected service not found.", "danger")
        return redirect(url_for('appointments'))
    
    # Create appointment datetime string for sorting
    appointment_datetime = f"{appointment_date} {appointment_time}"
    
    # Generate a unique appointment ID
    appointment_id = str(uuid.uuid4())
    
    # Store appointment in DynamoDB
    appointments_table.put_item(
        Item={
            'appointment_id': appointment_id,
            'client_email': session['user_email'],
            'client_name': session['user_name'],
            'beautician_id': beautician_id,
            'beautician_name': beautician['name'],
            'beautician_specialty': beautician['specialty'],
            'service_id': service_id,
            'service_name': service['name'],
            'service_duration': service['duration'],
            'service_price': service['price'],
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'appointment_datetime': appointment_datetime,
            'special_requests': special_requests,
            'status': 'scheduled',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    
    # Send confirmation email to client
    appointment_confirmation = f"Dear {session['user_name']},\n\nYour appointment for {service['name']} with {beautician['name']} has been scheduled for {appointment_date} at {appointment_time}.\n\nDuration: {service['duration']} minutes\nPrice: ${service['price']}\n\nSpecial Requests: {special_requests if special_requests else 'None'}\n\nPlease arrive 10 minutes before your scheduled time.\n\nBest regards,\nGlow Beauty Salon"
    send_email(session['user_email'], "Beauty Appointment Confirmation", appointment_confirmation)
    
    flash("Appointment booked successfully!", "success")
    return redirect(url_for('my_appointments'))

# My Appointments Page
@app.route('/my-appointments')
def my_appointments():
    if not is_logged_in():
        flash("Please log in to view your appointments.", "info")
        return redirect(url_for('login'))
    
    # Get user's appointments
    response = appointments_table.scan(
        FilterExpression=Attr('client_email').eq(session['user_email'])
    )
    user_appointments = response.get('Items', [])
    
    # Sort appointments by date/time
    user_appointments.sort(key=lambda x: x.get('appointment_datetime', ''))
    
    # Separate upcoming and past appointments
    upcoming_appointments = []
    past_appointments = []
    now = datetime.now()
    
    for appointment in user_appointments:
        appointment_dt = datetime.strptime(appointment['appointment_datetime'], "%Y-%m-%d %H:%M")
        if appointment_dt > now:
            upcoming_appointments.append(appointment)
        else:
            past_appointments.append(appointment)
    
    return render_template('my_appointments.html', 
                          upcoming_appointments=upcoming_appointments,
                          past_appointments=past_appointments,
                          is_logged_in=is_logged_in())

# Reschedule Appointment Page
@app.route('/reschedule-appointment/<appointment_id>', methods=['GET', 'POST'])
def reschedule_appointment(appointment_id):
    if not is_logged_in():
        flash("Please log in to reschedule appointments.", "danger")
        return redirect(url_for('login'))
    
    # Get appointment details
    response = appointments_table.get_item(Key={'appointment_id': appointment_id})
    appointment = response.get('Item')
    
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for('my_appointments'))
    
    # Verify the appointment belongs to the logged-in user
    if appointment['client_email'] != session['user_email']:
        flash("You don't have permission to reschedule this appointment.", "danger")
        return redirect(url_for('my_appointments'))
    
    if request.method == 'POST':
        new_date = request.form['new_date']
        new_time = request.form['new_time']
        
        if not new_date or not new_time:
            flash("Please select both date and time.", "danger")
            return redirect(url_for('reschedule_appointment', appointment_id=appointment_id))
        
        # Create new appointment datetime string for sorting
        new_appointment_datetime = f"{new_date} {new_time}"
        
        # Update appointment
        appointments_table.update_item(
            Key={'appointment_id': appointment_id},
            UpdateExpression="SET appointment_date = :date, appointment_time = :time, appointment_datetime = :datetime, rescheduled_at = :now, original_datetime = :original",
            ExpressionAttributeValues={
                ':date': new_date,
                ':time': new_time,
                ':datetime': new_appointment_datetime,
                ':now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ':original': appointment.get('appointment_datetime')
            }
        )
        
        # Send rescheduling confirmation email
        reschedule_message = f"Dear {session['user_name']},\n\nYour appointment for {appointment['service_name']} with {appointment['beautician_name']} has been rescheduled.\n\nNew Date: {new_date}\nNew Time: {new_time}\n\nIf you need to make any further changes, please visit our website.\n\nBest regards,\nGlow Beauty Salon"
        send_email(session['user_email'], "Appointment Rescheduling Confirmation", reschedule_message)
        
        flash("Appointment rescheduled successfully.", "success")
        return redirect(url_for('my_appointments'))
    
    return render_template('reschedule_appointment.html', 
                          appointment=appointment,
                          is_logged_in=is_logged_in())

# Cancel Appointment Route
@app.route('/cancel-appointment/<appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if not is_logged_in():
        flash("Please log in to cancel appointments.", "danger")
        return redirect(url_for('login'))
    
    # Get appointment details
    response = appointments_table.get_item(Key={'appointment_id': appointment_id})
    appointment = response.get('Item')
    
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for('my_appointments'))
    
    # Verify the appointment belongs to the logged-in user
    if appointment['client_email'] != session['user_email']:
        flash("You don't have permission to cancel this appointment.", "danger")
        return redirect(url_for('my_appointments'))
    
    # Update appointment status
    appointments_table.update_item(
        Key={'appointment_id': appointment_id},
        UpdateExpression="SET #status = :status, cancelled_at = :cancelled_at",
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'cancelled',
            ':cancelled_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    
    # Send cancellation email
    cancellation_message = f"Dear {session['user_name']},\n\nYour appointment for {appointment['service_name']} with {appointment['beautician_name']} scheduled for {appointment['appointment_date']} at {appointment['appointment_time']} has been cancelled.\n\nIf you wish to reschedule, please book a new appointment on our website.\n\nBest regards,\nGlow Beauty Salon"
    send_email(session['user_email'], "Appointment Cancellation Confirmation", cancellation_message)
    
    flash("Appointment cancelled successfully.", "success")
    return redirect(url_for('my_appointments'))

# Beauty Tips Page
@app.route('/beauty-tips')
def beauty_tips_page():
    return render_template('beauty_tips.html', 
                          tips=beauty_tips, 
                          concerns=beauty_concerns,
                          is_logged_in=is_logged_in())

# Client Profile Page
@app.route('/profile')
def client_profile():
    if not is_logged_in():
        flash("Please log in to view your profile.", "info")
        return redirect(url_for('login'))
    
    # Get client record
    response = client_records_table.get_item(Key={'client_id': session['user_email']})
    client_record = response.get('Item', {})
    
    # Get user account details
    response = users_table.get_item(Key={'email': session['user_email']})
    user_details = response.get('Item', {})
    
    # Get client's recent appointments
    response = appointments_table.scan(
        FilterExpression=Attr('client_email').eq(session['user_email'])
    )
    appointments = response.get('Items', [])
    
    # Sort appointments by date (newest first)
    appointments.sort(key=lambda x: x.get('appointment_datetime', ''), reverse=True)
    
    return render_template('profile.html', 
                          client=client_record, 
                          user=user_details,
                          appointments=appointments[:5],  # Show only the 5 most recent appointments
                          is_logged_in=is_logged_in())

# Update Client Profile
@app.route('/update-profile', methods=['POST'])
def update_profile():
    if not is_logged_in():
        flash("Please log in to update your profile.", "danger")
        return redirect(url_for('login'))
    
    # Get form data
    name = request.form['name']
    phone = request.form['phone']
    skin_type = request.form['skin_type']
    hair_type = request.form['hair_type']
    allergies = request.form.get('allergies', '').split(',')
    preferences = request.form.get('preferences', '').split(',')
    
    # Clean up lists (remove empty items and strip whitespace)
    allergies = [item.strip() for item in allergies if item.strip()]
    preferences = [item.strip() for item in preferences if item.strip()]
    
    # Update user information
    users_table.update_item(
        Key={'email': session['user_email']},
        UpdateExpression="SET #name = :name, phone = :phone",
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={
            ':name': name,
            ':phone': phone
        }
    )
    
    # Update client record
    client_records_table.update_item(
        Key={'client_id': session['user_email']},
        UpdateExpression="SET #name = :name, phone = :phone, skin_type = :skin_type, hair_type = :hair_type, allergies = :allergies, preferences = :preferences, last_updated = :last_updated",
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={
            ':name': name,
            ':phone': phone,
            ':skin_type': skin_type,
            ':hair_type': hair_type,
            ':allergies': allergies,
            ':preferences': preferences,
            ':last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    
    # Update session
    session['user_name'] = name
    
    flash("Profile updated successfully!", "success")
    return redirect(url_for('client_profile'))

# Admin Dashboard (for salon staff)
@app.route('/admin')
def admin_dashboard():
    if not is_logged_in():
        flash("Please log in to access the admin dashboard.", "danger")
        return redirect(url_for('login'))
    
    # Only allow staff/admin access
    if session['user_type'] not in ['admin', 'staff', 'beautician']:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))
    
    # Get all appointments
    response = appointments_table.scan()
    all_appointments = response.get('Items', [])
    
    # Get all clients
    response = client_records_table.scan()
    all_clients = response.get('Items', [])
    
    # Get all beauticians
    response = beauticians_table.scan()
    all_beauticians = response.get('Items', [])
    
    # Get all contact messages
    response = contact_messages_table.scan()
    all_messages = response.get('Items', [])
    
    # Sort data
    all_appointments.sort(key=lambda x: x.get('appointment_datetime', ''), reverse=True)
    all_clients.sort(key=lambda x: x.get('name', ''))
    all_beauticians.sort(key=lambda x: x.get('name', ''))
    all_messages.sort(key=lambda x: x.get('submitted_date', ''), reverse=True)
    
    return render_template('admin_dashboard.html', 
                          appointments=all_appointments, 
                          clients=all_clients,
                          beauticians=all_beauticians,
                          messages=all_messages,
                          is_logged_in=is_logged_in())

# Add Beautician (Admin function)
@app.route('/add-beautician', methods=['GET', 'POST'])
def add_beautician():
    if not is_logged_in() or session['user_type'] != 'admin':
        flash("You don't have permission to add beauticians.", "danger")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Generate a unique beautician ID
        beautician_id = str(uuid.uuid4())
        
        # Get form data
        name = request.form['name']
        email = request.form['email']
        specialty = request.form['specialty']
        qualification = request.form['qualification']
        experience = request.form['experience']
        bio = request.form['bio']
        phone = request.form['phone']
        
        # Store beautician in DynamoDB
        beauticians_table.put_item(
            Item={
                'beautician_id': beautician_id,
                'name': name,
                'email': email,
                'specialty': specialty,
                'qualification': qualification,
                'experience': experience,
                'bio': bio,
                'phone': phone,
                'available': True,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        
        # Also create user account for beautician
        hashed_password = hashpw("temppassword123".encode('utf-8'), gensalt()).decode('utf-8')
        users_table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': hashed_password,
                'phone': phone,
                'user_type': 'beautician',
                'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        
        # Send welcome email with login details
        # Send welcome email with login details
        welcome_message = f"Dear {name},\n\nYou have been added to the Glow Beauty Salon portal. You can now login with the following details:\n\nEmail: {email}\nTemporary Password: temppassword123\n\nPlease change your password after first login.\n\nBest regards,\nGlow Beauty Salon Management"
        send_email(email, "Welcome to Glow Beauty Salon Portal", welcome_message)
        
        flash(f"Beautician {name} added successfully!", "success")
        return redirect(url_for('beauticians_list'))
        
    return render_template('add_beautician.html', is_logged_in=is_logged_in())

# Services Page
@app.route('/services')
def services():
    # Define available services
    beauty_services = [
        {
            'id': 'haircut',
            'name': 'Haircut & Styling', 
            'duration': '60', 
            'price': '45',
            'description': 'Professional haircut and styling tailored to your face shape and preferences.',
            'category': 'Hair'
        },
        {
            'id': 'coloring',
            'name': 'Hair Coloring', 
            'duration': '120', 
            'price': '80',
            'description': 'Full hair coloring service using premium products for vibrant, long-lasting color.',
            'category': 'Hair'
        },
        {
            'id': 'facial',
            'name': 'Facial Treatment', 
            'duration': '60', 
            'price': '55',
            'description': 'Deep cleansing facial that includes exfoliation, extraction, and hydration.',
            'category': 'Face'
        },
        {
            'id': 'manicure',
            'name': 'Manicure', 
            'duration': '45', 
            'price': '35',
            'description': 'Nail shaping, cuticle care, hand massage, and polish application.',
            'category': 'Nails'
        },
        {
            'id': 'pedicure',
            'name': 'Pedicure', 
            'duration': '45', 
            'price': '40',
            'description': 'Foot soak, exfoliation, nail care, and polish application for beautiful feet.',
            'category': 'Nails'
        },
        {
            'id': 'massage',
            'name': 'Relaxing Massage', 
            'duration': '60', 
            'price': '65',
            'description': 'Full-body massage using essential oils to relieve stress and tension.',
            'category': 'Body'
        },
        {
            'id': 'makeup',
            'name': 'Professional Makeup', 
            'duration': '60', 
            'price': '60',
            'description': 'Full-face makeup application for special occasions or events.',
            'category': 'Face'
        },
        {
            'id': 'waxing',
            'name': 'Waxing Service', 
            'duration': '30', 
            'price': '30',
            'description': 'Hair removal using high-quality wax for smooth, long-lasting results.',
            'category': 'Body'
        }
    ]
    
    # Group services by category
    categorized_services = {}
    for service in beauty_services:
        category = service['category']
        if category not in categorized_services:
            categorized_services[category] = []
        categorized_services[category].append(service)
    
    return render_template('services.html', 
                          categorized_services=categorized_services,
                          is_logged_in=is_logged_in())

# Change Password
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not is_logged_in():
        flash("Please log in to change your password.", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for('change_password'))
        
        # Get user data
        response = users_table.get_item(Key={'email': session['user_email']})
        user = response.get('Item')
        
        if not user or not checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('change_password'))
        
        # Hash the new password
        hashed_password = hashpw(new_password.encode('utf-8'), gensalt()).decode('utf-8')
        
        # Update password in DynamoDB
        users_table.update_item(
            Key={'email': session['user_email']},
            UpdateExpression="SET password = :password, password_updated_at = :updated_at",
            ExpressionAttributeValues={
                ':password': hashed_password,
                ':updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        
        flash("Password changed successfully!", "success")
        return redirect(url_for('client_profile'))
    
    return render_template('change_password.html', is_logged_in=is_logged_in())

# Beauty Packages
@app.route('/packages')
def beauty_packages():
    packages = [
        {
            'id': 'basic',
            'name': 'Basic Beauty Package',
            'price': '99',
            'description': 'Perfect for a quick refresh. Includes a basic facial, express manicure, and blowout styling.',
            'services': ['Express Facial', 'Express Manicure', 'Blowout Styling'],
            'duration': '2 hours'
        },
        {
            'id': 'premium',
            'name': 'Premium Pamper Package',
            'price': '179',
            'description': 'Complete relaxation experience with premium treatments for face, hair, and nails.',
            'services': ['Premium Facial', 'Hair Treatment', 'Gel Manicure', 'Classic Pedicure'],
            'duration': '3.5 hours'
        },
        {
            'id': 'bridal',
            'name': 'Bridal Beauty Package',
            'price': '249',
            'description': 'Special package for the bride-to-be. Look your absolute best on your special day.',
            'services': ['Bridal Makeup', 'Hair Styling', 'Manicure & Pedicure', 'Facial Treatment'],
            'duration': '4 hours'
        },
        {
            'id': 'mens',
            'name': 'Men\'s Grooming Package',
            'price': '89',
            'description': 'Tailored grooming services for men including haircut, facial, and hand treatment.',
            'services': ['Men\'s Haircut', 'Men\'s Facial', 'Hand Grooming'],
            'duration': '1.5 hours'
        }
    ]
    
    return render_template('packages.html', packages=packages, is_logged_in=is_logged_in())

# Book Package Route
@app.route('/book-package/<package_id>', methods=['GET', 'POST'])
def book_package(package_id):
    if not is_logged_in():
        flash("Please log in to book packages.", "danger")
        return redirect(url_for('login'))
    
    packages = {
        'basic': {
            'name': 'Basic Beauty Package',
            'price': '99',
            'description': 'Perfect for a quick refresh. Includes a basic facial, express manicure, and blowout styling.',
            'services': ['Express Facial', 'Express Manicure', 'Blowout Styling'],
            'duration': '2 hours'
        },
        'premium': {
            'name': 'Premium Pamper Package',
            'price': '179',
            'description': 'Complete relaxation experience with premium treatments for face, hair, and nails.',
            'services': ['Premium Facial', 'Hair Treatment', 'Gel Manicure', 'Classic Pedicure'],
            'duration': '3.5 hours'
        },
        'bridal': {
            'name': 'Bridal Beauty Package',
            'price': '249',
            'description': 'Special package for the bride-to-be. Look your absolute best on your special day.',
            'services': ['Bridal Makeup', 'Hair Styling', 'Manicure & Pedicure', 'Facial Treatment'],
            'duration': '4 hours'
        },
        'mens': {
            'name': 'Men\'s Grooming Package',
            'price': '89',
            'description': 'Tailored grooming services for men including haircut, facial, and hand treatment.',
            'services': ['Men\'s Haircut', 'Men\'s Facial', 'Hand Grooming'],
            'duration': '1.5 hours'
        }
    }
    
    if package_id not in packages:
        flash("Selected package not found.", "danger")
        return redirect(url_for('beauty_packages'))
    
    package = packages[package_id]
    
    if request.method == 'POST':
        beautician_id = request.form['beautician_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        special_requests = request.form.get('special_requests', '')
        
        # Basic validation
        if not beautician_id or not appointment_date or not appointment_time:
            flash("All fields are required to book a package.", "danger")
            return redirect(url_for('book_package', package_id=package_id))
        
        # Get beautician details
        response = beauticians_table.get_item(Key={'beautician_id': beautician_id})
        beautician = response.get('Item')
        
        if not beautician:
            flash("Selected beautician not found.", "danger")
            return redirect(url_for('book_package', package_id=package_id))
        
        # Create appointment datetime string for sorting
        appointment_datetime = f"{appointment_date} {appointment_time}"
        
        # Generate a unique appointment ID
        appointment_id = str(uuid.uuid4())
        
        # Store appointment in DynamoDB
        appointments_table.put_item(
            Item={
                'appointment_id': appointment_id,
                'client_email': session['user_email'],
                'client_name': session['user_name'],
                'beautician_id': beautician_id,
                'beautician_name': beautician['name'],
                'beautician_specialty': beautician['specialty'],
                'service_id': f"package_{package_id}",
                'service_name': package['name'],
                'service_duration': package['duration'],
                'service_price': package['price'],
                'is_package': True,
                'package_services': package['services'],
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_datetime': appointment_datetime,
                'special_requests': special_requests,
                'status': 'scheduled',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        
        # Send confirmation email to client
        services_list = "\n".join([f"- {service}" for service in package['services']])
        appointment_confirmation = f"Dear {session['user_name']},\n\nYour appointment for the {package['name']} with {beautician['name']} has been scheduled for {appointment_date} at {appointment_time}.\n\nServices included:\n{services_list}\n\nDuration: {package['duration']}\nPrice: ${package['price']}\n\nSpecial Requests: {special_requests if special_requests else 'None'}\n\nPlease arrive 15 minutes before your scheduled time.\n\nBest regards,\nGlow Beauty Salon"
        send_email(session['user_email'], "Beauty Package Appointment Confirmation", appointment_confirmation)
        
        flash("Package appointment booked successfully!", "success")
        return redirect(url_for('my_appointments'))
    
    # Get all beauticians for appointment booking
    response = beauticians_table.scan()
    beauticians = response.get('Items', [])
    
    return render_template('book_package.html', 
                          package=package,
                          package_id=package_id,
                          beauticians=beauticians,
                          is_logged_in=is_logged_in())

# Testimonials Page
@app.route('/testimonials')
def testimonials():
    # Sample testimonials
    client_testimonials = [
        {
            'name': 'Sarah Johnson',
            'service': 'Hair Coloring',
            'rating': 5,
            'comment': 'Absolutely loved my experience! The colorist understood exactly what I wanted and the results were better than I expected.',
            'date': '2025-03-15'
        },
        {
            'name': 'Michael Chen',
            'service': 'Men\'s Grooming Package',
            'rating': 5,
            'comment': 'First time getting a professional facial and I\'m now a convert. My skin looks amazing and the whole experience was relaxing.',
            'date': '2025-03-22'
        },
        {
            'name': 'Emily Rodriguez',
            'service': 'Premium Pamper Package',
            'rating': 4,
            'comment': 'Treated myself for my birthday and it was worth every penny. My technician was skilled and attentive.',
            'date': '2025-04-05'
        },
        {
            'name': 'David Lee',
            'service': 'Haircut & Styling',
            'rating': 5,
            'comment': 'Best haircut I\'ve had in years! The stylist really listened to what I wanted and gave great suggestions.',
            'date': '2025-04-10'
        }
    ]
    
    return render_template('testimonials.html', 
                          testimonials=client_testimonials,
                          is_logged_in=is_logged_in())

# Submit Testimonial Route
@app.route('/submit-testimonial', methods=['POST'])
def submit_testimonial():
    if not is_logged_in():
        flash("Please log in to submit a testimonial.", "danger")
        return redirect(url_for('login'))
    
    # This would typically save to a testimonials table in DynamoDB
    # For now, we'll just flash a success message
    flash("Thank you for your feedback! Your testimonial has been submitted for review.", "success")
    return redirect(url_for('testimonials'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', is_logged_in=is_logged_in()), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', is_logged_in=is_logged_in()), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
