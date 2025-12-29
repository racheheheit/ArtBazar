from flask import Flask, render_template, request, redirect, url_for, flash, session
import sys
import random
from datetime import datetime, timedelta
from functools import wraps
import os
from werkzeug.utils import secure_filename

from datetime import datetime
# print(" Flask app starting...", file=sys.stderr)

try:
    from flask_mail import Mail, Message
    print(" Flask-Mail imported successfully", file=sys.stderr)
except Exception as e:
    print(" Flask-Mail import failed:", e, file=sys.stderr)

try:
    from flask_bcrypt import Bcrypt
    print(" Flask-Bcrypt imported successfully", file=sys.stderr)
except Exception as e:
    print(" Flask-Bcrypt import failed:", e, file=sys.stderr)

try:
    import mysql.connector
    print(" MySQL connector imported successfully", file=sys.stderr)
except Exception as e:
    print(" MySQL connector import failed:", e, file=sys.stderr)

# app configuration
app = Flask(__name__)
app.secret_key = "supersecretkey"

# database config
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password", 
        database="artbazar_dbms"
    )
    cursor = conn.cursor(dictionary=True)
    print(" Database connected successfully", file=sys.stderr)
except Exception as e:
    print(" Database connection failed:", e, file=sys.stderr)
    conn = None
    cursor = None

# mail configuration 
try:
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'artbazarmail@gmail.com'
    app.config['MAIL_PASSWORD'] = 'kxep cvts ozlp wyiy' 
    mail = Mail(app)
    print(" Mail configured successfully", file=sys.stderr)
except Exception as e:
    print(" Mail configuration failed:", e, file=sys.stderr)
    mail = None

# hasshing the app using bycrypt
try:
    bcrypt = Bcrypt(app)
    print(" Bcrypt initialized successfully", file=sys.stderr)
except Exception as e:
    print(" Bcrypt initialization failed:", e, file=sys.stderr)
    bcrypt = None

# 
def login_required(role=None):
    """Decorator to protect routes; optionally enforce a specific role."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash("Please log in first.", "warning")
                return redirect(url_for('login'))
            if role and user.get('role') != role:
                flash("You don't have permission to view that page.", "danger")
                return redirect(url_for(f"{user.get('role')}_dashboard"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


# ROUTES

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER2 = os.path.join('static', 'vendor_items')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2

#--------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add_artwork', methods=['GET', 'POST'])
@login_required(role='artist')
def add_artwork():
    if request.method == 'POST':
        title = request.form.get('title')
        art_type = request.form.get('type')
        medium = request.form.get('medium')
        caption = request.form.get('caption')
        price = request.form.get('price')
        artist_email = session['user']['email']
        artist_id = session['user']['id']
        file = request.files.get('image')

        if not file or not allowed_file(file.filename):
            flash("Please upload a valid image file (png, jpg, jpeg).", "danger")
            return redirect(url_for('add_artwork'))

        # Save image
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Save record to database
        cursor.execute("""
            INSERT INTO Artwork (Title, Artist_ID, Type, Medium, Caption, Image, Price, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, artist_id, art_type, medium, caption, filepath, price, 'Available'))
        conn.commit()

        flash("Artwork added successfully!", "success")
        return redirect(url_for('artist_dashboard'))

    return render_template('add_artwork.html')


@app.route('/add_item', methods=['GET', 'POST'])
@login_required(role='vendor')
def add_item():
    
    if request.method == 'POST':
        supply_id = request.form.get('supply_id')
        vendor_id = session['user'].get('role_id')
        name = request.form.get('name')
        type = request.form.get('type')
        description = request.form.get('description')
        stock =request.form.get('stock')
        price =request.form.get('price')
        file = request.files.get('image')

        if not file or not allowed_file(file.filename):
            flash("Please upload a valid image file (png, jpg, jpeg).", "danger")
            return redirect(url_for('add_item'))

        # Save image
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER2'], filename)
        file.save(filepath)
        print("DEBUG add_item form:", {
    'supply_id': supply_id,
    'vendor_id': vendor_id,
    'name': name,
    'type': type,
    'description': description,
    'stock': stock,
    'price': price,
    'filepath': filepath
}, file=sys.stderr)
        
        cursor.execute("""
    INSERT INTO Supply (Supply_ID, Vendor_ID, Name, Type, Description, Price, Stock, Image)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (supply_id, vendor_id, name, type, description, price, stock, filepath))

        conn.commit()

        flash("Item added successfully!", "success")
        return redirect(url_for('vendor_dashboard'))

    return render_template('add_item.html')
@app.route('/')
def home():
    print(" Home route triggered", file=sys.stderr)
    return render_template('index.html')

# -------------------- CONTACT FORM EMAIL --------------------
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not (name and email and message):
        flash("All fields are required.", "danger")
        return redirect(url_for('contact'))

    try:
        msg = Message(
            subject=f"📩 New Contact Form Message from {name}",
            sender=app.config['MAIL_USERNAME'],  # 'artbazarmail@gmail.com'
            recipients=['artbazarmail@gmail.com'],  # where you’ll receive messages
            body=f"""
New message received from ArtBzaar contact form:

Name: {name}
Email: {email}

Message:
{message}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        )
        mail.send(msg)
        flash("Your message has been sent successfully!", "success")
        print(f"📨 Contact message received from {email}", file=sys.stderr)
    except Exception as e:
        print("Mail send error:", e, file=sys.stderr)
        flash("Sorry, something went wrong while sending your message.", "danger")

    return redirect(url_for('contact'))

#  SIGNUP 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("/signup route triggered", file=sys.stderr)
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not conn or not cursor:
            flash("Database not connected!", "danger")
            return redirect(url_for('signup'))

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("This email is already registered! Try logging in.", "warning")
            print(" Existing user attempted signup:", email, file=sys.stderr)
            return redirect(url_for('login'))

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        otp = str(random.randint(100000, 999999))
        otp_expiry = datetime.now() + timedelta(minutes=5)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash, otp_code, otp_expiry, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, password_hash, otp, otp_expiry, False))
        conn.commit()
        print(f" User inserted: {email}, OTP: {otp}", file=sys.stderr)

        if mail:
            try:
                msg = Message(
                    subject="ArtBzaar Email Verification",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email]
                )
                msg.body = f"Hi {name}!,\n\nYour ArtBazar verification code is {otp}.\n.\nIt will expire in 5 minutes.\n(Kindly remember your password)\n\n-Team ArtBazar | Rachit Singh Rana"
                mail.send(msg)
                print(" OTP mail sent to", email, file=sys.stderr)
            except Exception as e:
                print(" Failed to send email:", e, file=sys.stderr)
        else:
            print(" Mail not configured, OTP not sent", file=sys.stderr)

        flash("OTP sent to your email! Please verify.", "success")
        print("Redirecting to verify for:", email, file=sys.stderr)
        return redirect(url_for('verify', email=email))

    return render_template('signup.html')


#  VERIFY OTP 
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    email = request.args.get('email')
    print(f"/verify route triggered for {email}", file=sys.stderr)

   

    if request.method == 'POST':
        otp_input = request.form.get('otp')
        cursor.execute("SELECT id, otp_code, otp_expiry FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("User not found!", "danger")
            return redirect(url_for('signup'))

        if user['otp_code'] == otp_input and datetime.now() < user['otp_expiry']:
            cursor.execute("""
                UPDATE users
                SET is_verified = TRUE, otp_code = NULL, otp_expiry = NULL
                WHERE email = %s
            """, (email,))
            conn.commit()
            session['user_id'] = user['id']
            session['email'] = email
            flash("Email verified successfully! Please select your role.", "success")
            print(" User verified successfully:", email, file=sys.stderr)
            return redirect(url_for('choose_role'))
        else:
            flash("Invalid or expired OTP.", "danger")
            print(" Invalid OTP for:", email, file=sys.stderr)

    return render_template('verify.html', email=email)


# -------------------- CHOOSE ROLE --------------------
@app.route('/choose_role')
def choose_role():
    
    print("/choose_role route triggered", file=sys.stderr)
    return render_template('choose_role.html')

@app.route('/customer_gallery', methods=['GET'])
@login_required(role='customer')
def customer_gallery():
    search_query = request.args.get('q', '').strip()
    art_type = request.args.get('type', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()


    artwork_query = """
        SELECT 
            a.Artwork_ID, a.Title, a.Caption, a.Image,
            a.Price, a.Status, a.Type,
            u.name AS Artist_Name
        FROM Artwork a
        JOIN users u ON a.Artist_ID = u.id
        WHERE a.Status = 'Available'
    """
    artwork_params = []

    
    if search_query:
        artwork_query += " AND (a.Title LIKE %s OR a.Caption LIKE %s OR u.name LIKE %s)"
        like = f"%{search_query}%"
        artwork_params += [like, like, like]

   
    if art_type:
        artwork_query += " AND a.Type = %s"
        artwork_params.append(art_type)

    
    if min_price and max_price:
        artwork_query += " AND a.Price BETWEEN %s AND %s"
        artwork_params += [min_price, max_price]

    artwork_query += " ORDER BY a.Artwork_ID DESC"
    cursor.execute(artwork_query, artwork_params)
    artworks = cursor.fetchall()


    supply_query = """
        SELECT 
            s.Supply_ID, s.Name AS Title, s.Description AS Caption,
            s.Image, s.Price, s.Type, s.Stock,
            u.name AS Vendor_Name
        FROM Supply s
        JOIN users u ON s.Vendor_ID = u.id
        WHERE s.Stock > 0
    """
    supply_params = []

    
    if search_query:
        supply_query += " AND (s.Name LIKE %s OR s.Description LIKE %s OR u.name LIKE %s)"
        like = f"%{search_query}%"
        supply_params += [like, like, like]

   
    if art_type:
        supply_query += " AND s.Type = %s"
        supply_params.append(art_type)

    
    if min_price and max_price:
        supply_query += " AND s.Price BETWEEN %s AND %s"
        supply_params += [min_price, max_price]

    supply_query += " ORDER BY s.Supply_ID DESC"
    cursor.execute(supply_query, supply_params)
    supplies = cursor.fetchall()

    cursor.execute("SELECT DISTINCT Type FROM Artwork WHERE Status='Available'")
    artwork_types = {row['Type'] for row in cursor.fetchall() if row['Type']}

    cursor.execute("SELECT DISTINCT Type FROM Supply WHERE Stock > 0")
    supply_types = {row['Type'] for row in cursor.fetchall() if row['Type']}

    all_types = sorted(list(artwork_types.union(supply_types)))

    customer_name = session['user']['name']

    return render_template(
        'customer_gallery.html',
        customer_name=customer_name,
        artworks=artworks,
        supplies=supplies,
        search_query=search_query,
        art_types=all_types,
        art_type=art_type,
        min_price=min_price,
        max_price=max_price
    )




# Adding  to Cart 
#--- adding artworks
@app.route('/add_to_cart/<int:artwork_id>', methods=['POST'])
@login_required(role='customer')
def add_to_cart(artwork_id):
    customer_id = session['user']['id']

    cursor.execute("SELECT * FROM Cart WHERE Customer_ID = %s AND Artwork_ID = %s AND Status = 'In Cart'",
                   (customer_id, artwork_id))
    existing_item = cursor.fetchone()

    if existing_item:
        flash("This artwork is already in your cart.", "warning")
    else:
        cursor.execute("""
            INSERT INTO Cart (Customer_ID, Artwork_ID, Quantity, Status)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, artwork_id, 1, 'In Cart'))
        conn.commit()
        flash("Artwork added to your cart!", "success")

    return redirect(url_for('customer_gallery'))
#--- adding supplies
@app.route('/add_supply_to_cart/<int:supply_id>', methods=['POST'])
@login_required(role='customer')
def add_supply_to_cart(supply_id):
    customer_id = session['user']['id']

    cursor.execute("""SELECT * FROM Cart 
                      WHERE Customer_ID=%s AND Supply_ID=%s 
                      AND Status='In Cart'""",
                   (customer_id, supply_id))
    existing_item = cursor.fetchone()

    if existing_item:
        flash("This item is already in your cart.", "warning")
    else:
        cursor.execute("""INSERT INTO Cart (Customer_ID, Supply_ID, Quantity, Status)
                          VALUES (%s, %s, %s, %s)""",
                       (customer_id, supply_id, 1, 'In Cart'))
        conn.commit()
        flash("Supply item added to your cart!", "success")

    return redirect(url_for('customer_gallery'))


# View Cart
@app.route('/cart')
@login_required(role='customer')
def cart():
    customer_id = session['user']['id']

    cursor.execute("""
      SELECT 
    c.Cart_ID,
    c.Quantity,

    a.Artwork_ID,
    a.Title AS Artwork_Title,
    a.Price AS Artwork_Price,
    a.Image AS Artwork_Image,
    ua.name AS Artist_Name,

    s.Supply_ID,
    s.Name AS Supply_Title,
    s.Price AS Supply_Price,
    s.Image AS Supply_Image,
    us.name AS Vendor_Name

FROM Cart c
LEFT JOIN Artwork a ON c.Artwork_ID = a.Artwork_ID
LEFT JOIN users ua ON a.Artist_ID = ua.id
LEFT JOIN Supply s ON c.Supply_ID = s.Supply_ID
LEFT JOIN users us ON s.Vendor_ID = us.id
WHERE c.Customer_ID = %s AND c.Status='In Cart';

    """, (customer_id,))
    cart_items = cursor.fetchall()
    total_price=0;
    for item in cart_items:
        if item['Artwork_ID']:
            total_price+=item['Artwork_Price']
        elif item['Supply_ID']:
            total_price+=item['Supply_Price']

    return render_template('cart.html', cart_items=cart_items, total=total_price)


# Remove from Cart 
@app.route('/checkout', methods=['POST'])
@login_required(role='customer')
def checkout():
    customer_id = session['user']['id']

    cursor.execute("""
        SELECT 
            c.Cart_ID,
            c.Quantity,

            a.Artwork_ID,
            a.Price AS Artwork_Price,

            s.Supply_ID,
            s.Price AS Supply_Price

        FROM Cart c
        LEFT JOIN Artwork a ON c.Artwork_ID = a.Artwork_ID
        LEFT JOIN Supply s ON c.Supply_ID = s.Supply_ID
        WHERE c.Customer_ID = %s AND c.Status = 'In Cart'
    """, (customer_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('cart'))

   
    total_amount = 0
    for item in cart_items:
        if item['Artwork_ID']:
            total_amount += item['Artwork_Price']
        elif item['Supply_ID']:
            total_amount += item['Supply_Price']

    cursor.execute("""
        INSERT INTO Orders (Customer_ID, Total_Amount, Status, Date)
        VALUES (%s, %s, %s, NOW())
    """, (customer_id, total_amount, 'Pending'))
    conn.commit()

    order_id = cursor.lastrowid

   
    for item in cart_items:
        cursor.execute("""
            INSERT INTO OrderItems (Order_ID, Artwork_ID, Supply_ID, Quantity, Price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            order_id,
            item['Artwork_ID'],
            item['Supply_ID'],
            item['Quantity'],
            item['Artwork_Price'] if item['Artwork_ID'] else item['Supply_Price']
        ))

    conn.commit()

    cursor.execute("DELETE FROM Cart WHERE Customer_ID = %s", (customer_id,))
    conn.commit()

    flash("Order created successfully! Proceed to payment.", "info")
    return redirect(url_for('simulate_payment', order_id=order_id))



@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
@login_required(role='customer')
def remove_from_cart(cart_id):
    cursor.execute("DELETE FROM Cart WHERE Cart_ID = %s", (cart_id,))
    conn.commit()
    flash("Item removed from your cart.", "info")
    return redirect(url_for('cart'))

@app.route('/set_role/<role>')
def set_role(role):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please sign up or log in first.", "warning")
        return redirect(url_for('signup'))

   
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (role, user_id))
    conn.commit()

    print(f" Role '{role}' assigned for user_id {user_id}", file=sys.stderr)

   
    session['user'] = {
        'id': user_id,
        'email': session.get('email'),
        'role': role,
        'name': session.get('name', None)
    }

 
    return redirect(url_for(f"setup_{role}"))

# setting up customer, artist and vendor
@app.route('/setup_artist', methods=['GET', 'POST'])
@login_required(role='artist')
def setup_artist():
    user = session['user']
    user_id = user['id']

    if request.method == 'POST':
        bio = request.form.get('bio')
        contact = request.form.get('contact')

        cursor.execute("""
            INSERT INTO Artist (Artist_ID, Name, Email, Password, Bio, Contact)
            SELECT id, name, email, password_hash, %s, %s
            FROM users WHERE id = %s
        """, (bio, contact, user_id))

        conn.commit()
        flash("Artist profile completed!", "success")
        return redirect(url_for('artist_dashboard'))

    return render_template('setup_artist.html')

@app.route('/setup_customer', methods=['GET', 'POST'])
@login_required(role='customer')
def setup_customer():
    user = session['user']
    user_id = user['id']

    if request.method == 'POST':
        address = request.form.get('address')
        contact = request.form.get('contact')

        cursor.execute("""
            INSERT INTO Customer (Customer_ID, Name, Email, Password, Address, Contact)
            SELECT id, name, email, password_hash, %s, %s
            FROM users WHERE id = %s
        """, (address, contact, user_id))

        conn.commit()
        flash("Customer profile completed!", "success")
        return redirect(url_for('customer_dashboard'))

    return render_template('setup_customer.html')

@app.route('/setup_vendor', methods=['GET', 'POST'])
@login_required(role='vendor')
def setup_vendor():
    user = session['user']
    user_id = user['id']

    if request.method == 'POST':
        business_type = request.form.get('business_type')
        location = request.form.get('location')
        contact = request.form.get('contact')

        cursor.execute("""
            INSERT INTO Vendor (Vendor_ID, Name, Email, Password, Business_Type, Location, Contact)
            SELECT id, name, email, password_hash, %s, %s, %s
            FROM users WHERE id = %s
        """, (business_type, location, contact, user_id))

        conn.commit()
        flash("Vendor profile completed!", "success")
        return redirect(url_for('vendor_dashboard'))

    return render_template('setup_vendor.html')

@app.route('/artist_dashboard')
@login_required(role='artist')
def artist_dashboard():
    return render_template('artist_dashboard.html')

@app.route('/artist_gallery/<int:artist_id>')
@login_required(role='artist')
def artist_gallery(artist_id):
    artist_name = session.get('user', {}).get('name', 'Artist')
    print("Artist Name:", artist_name, file=sys.stderr)
    try:
        cursor.execute("""
           SELECT 
    a.Artwork_ID, 
    a.Title, 
    a.Caption, 
    a.Image, 
    a.Price, 
    a.Status
FROM Artwork a
WHERE a.Artist_ID = %s
GROUP BY a.Artwork_ID
ORDER BY a.Artwork_ID DESC;


        """, (artist_id,))
        artworks = cursor.fetchall()

        if not artworks:
            flash("You haven't uploaded any artworks yet.", "info")
        
        artist_name = session['user']['name']
        return render_template('artist_gallery.html', artist_name=artist_name, artworks=artworks)
    
    except Exception as e:
        print("Error loading artist gallery:", e, file=sys.stderr)
        flash("An error occurred while loading your gallery.", "danger")
        return redirect(url_for('artist_dashboard'))


@app.route('/vendor_dashboard')
@login_required(role='vendor')
def vendor_dashboard():
    return render_template('vendor_dashboard.html')
@app.route('/vendor_inventory')
@login_required(role='vendor')
def vendor_inventory():
    """
    Vendor inventory view showing all items listed by the logged-in vendor.
    """

   
    user = session.get('user')
    try:
        if user and user.get('role') == 'vendor' and not user.get('role_id'):
            email = user['email']
            cursor.execute("SELECT Vendor_ID FROM Vendor WHERE Email = %s", (email,))
            vendor = cursor.fetchone()
            if vendor:
                session['user']['role_id'] = vendor['Vendor_ID']
                print(f"Vendor session patched successfully: role_id={vendor['Vendor_ID']}", file=sys.stderr)
            else:
                print(f"No vendor found for {email} in Vendor table!", file=sys.stderr)
    except Exception as e:
        print("Error during vendor session patch:", e, file=sys.stderr)

    vendor_id = session['user'].get('role_id')
    vendor_name = session['user']['name']

    if not vendor_id:
        flash("Vendor session not initialized correctly. Please re-login.", "warning")
        return redirect(url_for('login'))

    try:
        cursor.execute("""
            SELECT Supply_ID, Name, Type, Description, Price, Stock, Image
            FROM Supply
            WHERE Vendor_ID = %s
            ORDER BY Supply_ID DESC
        """, (vendor_id,))
        items = cursor.fetchall()

        if not items:
            flash("You haven't added any items yet.", "info")

        return render_template(
            'vendor_inventory.html',
            vendor_name=vendor_name,
            items=items
        )

    except Exception as e:
        print("Error loading vendor inventory:", e, file=sys.stderr)
        flash("An error occurred while loading your inventory.", "danger")
        return render_template('vendor_inventory.html', items=[])



@app.route('/update_item/<int:supply_id>', methods=['POST'])
@login_required(role='vendor')
def update_item(supply_id):
    """
    Allow vendor to update price, stock, or description of an existing item.
    """
    user = session.get('user')
    try:
        if user and user.get('role') == 'vendor' and not user.get('role_id'):
            email = user['email']
            cursor.execute("SELECT Vendor_ID FROM Vendor WHERE Email = %s", (email,))
            vendor = cursor.fetchone()
            if vendor:
                session['user']['role_id'] = vendor['Vendor_ID']
                print(f"Vendor session patched in update_item: role_id={vendor['Vendor_ID']}", file=sys.stderr)
    except Exception as e:
        print("Error ensuring vendor session:", e, file=sys.stderr)

    vendor_id = session['user'].get('role_id')
    if not vendor_id:
        flash("Vendor not found in session. Please re-login.", "danger")
        return redirect(url_for('login'))

    # Fetch updated form values
    new_price = request.form.get('price')
    new_stock = request.form.get('stock')
    new_description = request.form.get('description', '').strip()

    try:
        cursor.execute("""
            UPDATE Supply
            SET Price = %s, Stock = %s, Description = %s
            WHERE Supply_ID = %s AND Vendor_ID = %s
        """, (new_price, new_stock, new_description, supply_id, vendor_id))
        conn.commit()

        flash(" Item updated successfully!", "success")
        print(f" Item {supply_id} updated by Vendor {vendor_id}", file=sys.stderr)
    except Exception as e:
        print(" Error updating item:", e, file=sys.stderr)
        flash(" Failed to update item. Please try again.", "danger")

    return redirect(url_for('vendor_inventory'))


@app.route('/customer_dashboard')
@login_required(role='customer')
def customer_dashboard():
    return render_template('customer_dashboard.html')

# ORDER & PAYMENT ROUTES
@app.route('/place_order', methods=['POST'])
@login_required(role='customer')
def place_order():
    customer_id = session['user']['id']

    # Fetch items from the cart
    cursor.execute("""
        SELECT c.Artwork_ID, a.Price, a.Artist_ID
        FROM Cart c
        JOIN Artwork a ON c.Artwork_ID = a.Artwork_ID
        WHERE c.Customer_ID = %s AND c.Status = 'In Cart'
    """, (customer_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart'))

    total_amount = sum(item['Price'] for item in cart_items)

    # Insert new order
    cursor.execute("""
        INSERT INTO Orders (Customer_ID, Total_Amount, Status)
        VALUES (%s, %s, %s)
    """, (customer_id, total_amount, 'Pending'))
    conn.commit()
    order_id = cursor.lastrowid

    # Clear the cart
    cursor.execute("DELETE FROM Cart WHERE Customer_ID = %s", (customer_id,))
    conn.commit()

    flash("Order created successfully! Proceed to payment.", "info")
    return redirect(url_for('simulate_payment', order_id=order_id))


# MOCK PAYMENT
@app.route('/simulate_payment/<int:order_id>')
@login_required(role='customer')
def simulate_payment(order_id):
    cursor.execute("SELECT * FROM Orders WHERE Order_ID = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        flash("Invalid order ID.", "danger")
        return redirect(url_for('cart'))

    return render_template('simulate_payment.html', order=order)


# MOCK PAYMENT RESULT 
@app.route('/mock_payment_result', methods=['POST'])
@login_required(role='customer')
def mock_payment_result():
    order_id = request.form.get('order_id')
    status = request.form.get('status')

    if status == 'success':
        cursor.execute("""
            INSERT INTO Payments (Order_ID, Amount, Method, Status)
            SELECT Order_ID, Total_Amount, 'MockGateway', 'Successful'
            FROM Orders WHERE Order_ID = %s
        """, (order_id,))
        cursor.execute("""
            UPDATE Orders SET Status = 'Completed' WHERE Order_ID = %s
        """, (order_id,))
        conn.commit()
        flash(" Payment successful! Thank you for supporting art.", "success")
    else:
        cursor.execute("""
            INSERT INTO Payments (Order_ID, Amount, Method, Status)
            SELECT Order_ID, Total_Amount, 'MockGateway', 'Failed'
            FROM Orders WHERE Order_ID = %s
        """, (order_id,))
        cursor.execute("""
            UPDATE Orders SET Status = 'Failed' WHERE Order_ID = %s
        """, (order_id,))
        conn.commit()
        flash(" Payment failed. Please try again later.", "danger")

    return redirect(url_for('customer_dashboard'))

# LOGIN 
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("/login route triggered", file=sys.stderr)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role_input = request.form.get('role')

        print("EMAIL:", email, file=sys.stderr)
        print("ROLE_INPUT:", role_input, file=sys.stderr)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        print("USER:", user, file=sys.stderr)

        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for('login'))

        
        user_verified = int(user['is_verified'])
        if user['role'] != 'admin' and user_verified != 1:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for('signup'))

        # --- PASSWORD CHECK ---
        if not bcrypt.check_password_hash(user['password_hash'], password):
            flash("Incorrect password.", "danger")
            print("FAIL: Wrong password", file=sys.stderr)
            return redirect(url_for('login'))

        # --- ROLE CHECK ---
        db_role = user['role']
        print("DB_ROLE:", db_role, file=sys.stderr)

        if db_role != role_input:
            flash("Role mismatch! Select the correct role.", "danger")
            print("FAIL: ROLE MISMATCH", file=sys.stderr)
            return redirect(url_for('login'))

        # --- SESSION SET ---
        session['user'] = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': db_role
        }

        print("LOGIN SUCCESS:", db_role, file=sys.stderr)

        # --- ADMIN GOES DIRECTLY TO ADMIN DASHBOARD ---
        if db_role == "admin":
            return redirect(url_for("admin_dashboard"))

        # --- OTHER ROLES ---
        return redirect(url_for(f"{db_role}_dashboard"))

    return render_template('login.html')


#REVIEW YOUR ORDER
@app.route("/my_orders")
@login_required()
def my_orders():
    user = session["user"]
    role = user["role"]
    user_id = user["id"]

    # -------- CUSTOMER VIEW ----------
    if role == "customer":
        cursor.execute("""
            SELECT
                o.Order_ID, o.Date, o.Status,

                oi.Quantity, oi.Price,
                a.Title AS Artwork_Title, 
                s.Name AS Supply_Title

            FROM Orders o
            LEFT JOIN OrderItems oi ON o.Order_ID = oi.Order_ID
            LEFT JOIN Artwork a ON oi.Artwork_ID = a.Artwork_ID
            LEFT JOIN Supply s ON oi.Supply_ID = s.Supply_ID
            WHERE o.Customer_ID = %s
            ORDER BY o.Order_ID DESC
        """, (user_id,))
        rows = cursor.fetchall()

    # ARTIST VIEW 
    elif role == "artist":
        cursor.execute("""
            SELECT
                o.Order_ID, o.Date, o.Status,
                oi.Quantity, oi.Price,
                a.Title AS Artwork_Title,
                u.Name AS Customer_Name
            FROM Orders o
            JOIN OrderItems oi ON o.Order_ID = oi.Order_ID
            JOIN Artwork a ON oi.Artwork_ID = a.Artwork_ID
            JOIN users u ON o.Customer_ID = u.id
            WHERE a.Artist_ID = %s
            ORDER BY o.Order_ID DESC
        """, (user_id,))
        rows = cursor.fetchall()

    #  VENDOR VIEW 
    elif role == "vendor":
        cursor.execute("""
            SELECT
                o.Order_ID, o.Date, o.Status,
                oi.Quantity, oi.Price,
                s.Name AS Supply_Title,
                u.Name AS Customer_Name
            FROM Orders o
            JOIN OrderItems oi ON o.Order_ID = oi.Order_ID
            JOIN Supply s ON oi.Supply_ID = s.Supply_ID
            JOIN users u ON o.Customer_ID = u.id
            WHERE s.Vendor_ID = %s
            ORDER BY o.Order_ID DESC
        """, (user_id,))
        rows = cursor.fetchall()

    # -------- Group items inside orders ----------
    orders_dict = {}
    for row in rows:
        oid = row["Order_ID"]

        if oid not in orders_dict:
            orders_dict[oid] = {
                "Order_ID": row["Order_ID"],
                "Date": row["Date"],
                "Status": row["Status"],
                "items": []
            }

        orders_dict[oid]["items"].append({
            "Artwork_Title": row.get("Artwork_Title"),
            "Supply_Title": row.get("Supply_Title"),
            "Quantity": row["Quantity"],
            "Price": row["Price"],
            "Customer_Name": row.get("Customer_Name")
        })

    orders = list(orders_dict.values())

    return render_template("my_orders.html", orders=orders, role=role)



# LOGOUT 
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


#  MAIN 
if __name__ == "__main__":
    print(" Starting Flask server...", file=sys.stderr)
    app.run(debug=True)
