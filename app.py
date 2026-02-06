# ============================================
# ORDERFLOW - MULTI-TENANT VERSION
# ============================================
# Save as: app.py
# Run: python -m streamlit run app.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import urllib.parse
import secrets


# Page config
st.set_page_config(
    page_title="StockUp",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clear any URL query parameters to prevent logout on refresh
try:
    if st.query_params:
        st.query_params.clear()
except:
    pass

# Session state persistence - prevent logout on refresh
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""
if 'cafe_id' not in st.session_state:
    st.session_state.cafe_id = ""
if 'cafe_name' not in st.session_state:
    st.session_state.cafe_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'items_added_count' not in st.session_state:
    st.session_state.items_added_count = 0
st.markdown("""
<style>
/* Make ALL text inside the yellow cafe box readable */
section[data-testid="stSidebar"] .stMarkdown strong,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown code,
section[data-testid="stSidebar"] .stMarkdown small {
    color: #1A1A1A !important;  /* dark text for yellow background */
}
</style>
""", unsafe_allow_html=True)

# Custom CSS - Mobile Friendly
st.markdown("""
<style>
    /* Base Styles */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-size: 16px;
        font-weight: 600;
    }
    
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }
    
    .cafe-id-box {
        background: #fff3cd;
        border: 2px solid #ffc107;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        word-wrap: break-word;
    }
    
    .status-draft {
        background-color: #ffc107;
        color: black;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .status-approved {
        background-color: #28a745;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .whatsapp-message {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 15px;
        border-radius: 10px;
        font-family: monospace;
        white-space: pre-wrap;
        border: 2px solid #4caf50;
        line-height: 1.6;
        word-wrap: break-word;
        overflow-x: auto;
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        /* Reduce padding on mobile */
        .block-container {
            padding: 1rem !important;
        }
        
        /* Make welcome banner more compact */
        .welcome-banner {
            padding: 20px 15px;
            margin-bottom: 15px;
        }
        
        .welcome-banner h1 {
            font-size: 24px !important;
        }
        
        .welcome-banner h2 {
            font-size: 20px !important;
        }
        
        .welcome-banner p {
            font-size: 14px !important;
        }
        
        /* Cafe ID box mobile friendly */
        .cafe-id-box {
            padding: 12px;
            font-size: 14px;
        }
        
        .cafe-id-box h1 {
            font-size: 32px !important;
        }
        
        .cafe-id-box h3 {
            font-size: 16px !important;
        }
        
        /* Button adjustments */
        .stButton button {
            height: 48px;
            font-size: 15px;
        }
        
        /* Form inputs */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox select {
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
        
        /* Metrics - Stack on mobile */
        [data-testid="stMetricValue"] {
            font-size: 20px !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 12px !important;
        }
        
        /* WhatsApp message box */
        .whatsapp-message {
            font-size: 13px;
            padding: 12px;
        }
        
        /* Tabs - Better mobile spacing */
        .stTabs [data-baseweb="tab"] {
            padding: 10px 12px;
            font-size: 14px;
        }
        
        /* Column layout fixes */
        [data-testid="column"] {
            padding: 0 5px !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            font-size: 15px;
            padding: 12px;
        }
        
        /* Headers */
        h1 {
            font-size: 26px !important;
        }
        
        h2 {
            font-size: 22px !important;
        }
        
        h3 {
            font-size: 18px !important;
        }
        
        /* Status badges */
        .status-draft,
        .status-approved {
            font-size: 12px;
            padding: 4px 12px;
        }
        
        /* Sidebar adjustments */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }
        
        section[data-testid="stSidebar"] .stButton button {
            height: 44px;
            font-size: 14px;
        }
        
        /* Form container */
        .stForm {
            padding: 15px !important;
        }
    }
    
    /* Small phones (< 375px) */
    @media (max-width: 375px) {
        .block-container {
            padding: 0.5rem !important;
        }
        
        .welcome-banner {
            padding: 15px 10px;
        }
        
        .welcome-banner h1 {
            font-size: 20px !important;
        }
        
        .welcome-banner h2 {
            font-size: 18px !important;
        }
        
        .stButton button {
            height: 44px;
            font-size: 14px;
        }
        
        .cafe-id-box h1 {
            font-size: 28px !important;
        }
        
        h1 {
            font-size: 22px !important;
        }
        
        h2 {
            font-size: 18px !important;
        }
    }
    
    /* Tablet landscape (768px - 1024px) */
    @media (min-width: 768px) and (max-width: 1024px) {
        .block-container {
            padding: 2rem !important;
        }
        
        .welcome-banner {
            padding: 25px 20px;
        }
    }
    
    /* Touch-friendly improvements */
    @media (hover: none) and (pointer: coarse) {
        /* Larger tap targets for touch devices */
        .stButton button {
            min-height: 48px;
        }
        
        /* Better spacing for touch */
        .streamlit-expanderHeader {
            min-height: 48px;
        }
        
        /* Prevent text selection issues on mobile */
        .stButton button {
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
    }
    
    /* Landscape mode adjustments */
    @media (max-width: 768px) and (orientation: landscape) {
        .welcome-banner {
            padding: 15px 20px;
        }
        
        .stButton button {
            height: 40px;
        }
    }
    
    /* Improve scrolling on mobile */
    body {
        -webkit-overflow-scrolling: touch;
    }
    
    /* Make sure content doesn't get cut off */
    .main {
        overflow-x: hidden;
    }
    
    /* Fix for iOS Safari bottom bar */
    @supports (-webkit-touch-callout: none) {
        .main {
            padding-bottom: 80px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FIREBASE SETUP
# ============================================

@st.cache_resource
def init_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))

        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# ============================================
# CATEGORIZATION ENGINE
# ============================================

KEYWORDS_DATABASE = {
    "Dairy & Milk Products": ["milk", "butter", "cheese", "paneer", "curd", "ghee", "cream", "dahi", "malai"],
    "Meat, Poultry & Seafood": ["chicken", "mutton", "fish", "eggs", "prawns", "meat", "keema"],
    "Vegetables": ["onion", "tomato", "potato", "carrot", "beans", "cabbage", "spinach", "palak", "gobi"],
    "Fruits": ["apple", "banana", "mango", "orange", "grapes", "papaya"],
    "Rice, Grains & Pulses": ["rice", "wheat", "atta", "dal", "pasta", "noodles", "maida", "rava"],
    "Spices & Masala": ["salt", "pepper", "turmeric", "chilli", "masala", "jeera", "haldi"],
    "Cooking Oil & Ghee": ["oil", "ghee", "butter", "refined", "mustard oil"],
    "Bakery & Bread": ["bread", "bun", "cake", "biscuit", "pav", "rusk"],
    "Beverages & Drinks": ["tea", "coffee", "juice", "water", "cold drink", "chai"],
    "Cleaning & Kitchen Supplies": ["tissue", "napkin", "detergent", "soap", "foil", "cleaner"]
}

def add_new_category(category_name, keywords_list):
    """Add a new category to the database."""
    if category_name not in KEYWORDS_DATABASE:
        KEYWORDS_DATABASE[category_name] = keywords_list
        return True
    return False

def add_item_to_category(category_name, item_name):
    """Add an item keyword to existing category."""
    if category_name in KEYWORDS_DATABASE:
        item_lower = item_name.lower().strip()
        if item_lower not in KEYWORDS_DATABASE[category_name]:
            KEYWORDS_DATABASE[category_name].append(item_lower)
            return True
    return False

def categorize_item(item_name):
    if not item_name:
        return "Uncategorized"
    
    item_lower = item_name.lower().strip()
    
    for category, keywords in KEYWORDS_DATABASE.items():
        if item_lower in keywords:
            return category
    
    for category, keywords in KEYWORDS_DATABASE.items():
        for keyword in keywords:
            if keyword in item_lower:
                return category
    
    return "Uncategorized"

# ============================================
# CAFE MANAGER (MULTI-TENANT)
# ============================================

class CafeManager:
    def __init__(self):
        self.cafes_ref = db.collection('cafes')
        self.users_ref = db.collection('users')
    
    def create_cafe(self, cafe_name, owner_name, phone, password):
        """Create new cafe with phone + password."""
        cafe_id = secrets.token_hex(4).upper()
        
        existing = self.get_user_by_phone(phone)
        if existing:
            return None, "Phone number already registered"
        
        cafe_data = {
            'name': cafe_name,
            'owner_name': owner_name,
            'owner_phone': phone,
            'created_at': firestore.SERVER_TIMESTAMP,
            'subscription': 'free'
        }
        
        self.cafes_ref.document(cafe_id).set(cafe_data)
        
        self.users_ref.add({
            'name': owner_name,
            'phone': phone,
            'password': password,
            'role': 'Owner',
            'cafe_id': cafe_id,
            'cafe_name': cafe_name,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return cafe_id, "Success"
    
    def get_cafe(self, cafe_id):
        """Get cafe details."""
        doc = self.cafes_ref.document(cafe_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_user_by_phone(self, phone):
        """Find user by phone number."""
        docs = self.users_ref.where('phone', '==', phone).limit(1).stream()
        
        for doc in docs:
            user = doc.to_dict()
            user['id'] = doc.id
            return user
        return None
    
    def verify_login(self, phone, password):
        """Verify phone + password login."""
        user = self.get_user_by_phone(phone)
        
        if user and user.get('password') == password:
            return user
        return None
    
    def reset_password(self, phone, new_password):
        """Reset password for a user."""
        user = self.get_user_by_phone(phone)
        
        if not user:
            return False, "Phone number not found"
        
        # Update password
        self.users_ref.document(user['id']).update({
            'password': new_password
        })
        
        return True, f"Password reset successful for {user['name']}"
    
    def add_staff(self, cafe_id, cafe_name, name, phone, password):
        """Add staff member to cafe."""
        existing = self.get_user_by_phone(phone)
        if existing:
            return False, "Phone number already registered"
        
        self.users_ref.add({
            'name': name,
            'phone': phone,
            'password': password,
            'role': 'Staff',
            'cafe_id': cafe_id,
            'cafe_name': cafe_name,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return True, "Success"
    
    def get_all_staff(self, cafe_id):
        """Get all users in a cafe."""
        docs = self.users_ref.where('cafe_id', '==', cafe_id).stream()
        users = []
        for doc in docs:
            user = doc.to_dict()
            user['id'] = doc.id
            users.append(user)
        return users
    
    def delete_staff(self, user_id):
        """Delete a staff member."""
        self.users_ref.document(user_id).delete()
        return True

# ============================================
# VENDOR MANAGER (MULTI-TENANT)
# ============================================

class VendorManager:
    def __init__(self, cafe_id):
        self.cafe_id = cafe_id
        self.vendors_ref = db.collection('cafes').document(cafe_id).collection('vendors')
    
    def add_vendor(self, category, vendor_name, phone, vendor_type="WhatsApp"):
        vendor_data = {
            "category": category,
            "vendor_name": vendor_name,
            "phone": phone,
            "vendor_type": vendor_type,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        self.vendors_ref.add(vendor_data)
        return True
    
    def get_all_vendors(self):
        docs = self.vendors_ref.stream()
        vendors = []
        for doc in docs:
            vendor = doc.to_dict()
            vendor['id'] = doc.id
            vendors.append(vendor)
        return vendors
    
    def get_vendor_by_category(self, category):
        docs = self.vendors_ref.where('category', '==', category).limit(1).stream()
        for doc in docs:
            vendor = doc.to_dict()
            vendor['id'] = doc.id
            return vendor
        return None
    
    def delete_vendor(self, vendor_id):
        self.vendors_ref.document(vendor_id).delete()
        return True

# ============================================
# DRAFT MANAGER (MULTI-TENANT)
# ============================================

class DraftManager:
    def __init__(self, cafe_id):
        self.cafe_id = cafe_id
        self.draft_ref = db.collection('cafes').document(cafe_id).collection('drafts').document('current-draft')
        self.orders_ref = db.collection('cafes').document(cafe_id).collection('orders')
    
    def add_item(self, item_name, quantity, added_by):
        category = categorize_item(item_name)
        
        item = {
            "name": item_name.strip(),
            "quantity": quantity.strip(),
            "category": category,
            "added_by": added_by,
            "added_at": datetime.now().isoformat()
        }
        
        draft_doc = self.draft_ref.get()
        
        if draft_doc.exists:
            current_items = draft_doc.to_dict().get('items', [])
            current_items.append(item)
            self.draft_ref.update({
                'items': current_items,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        else:
            self.draft_ref.set({
                'items': [item],
                'status': 'Draft',
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        
        return category
    
    def get_draft(self):
        draft_doc = self.draft_ref.get()
        if not draft_doc.exists:
            return {'items': [], 'status': 'Draft'}
        return draft_doc.to_dict()
    
    def remove_item(self, index):
        draft_doc = self.draft_ref.get()
        if draft_doc.exists:
            items = draft_doc.to_dict().get('items', [])
            if 0 <= index < len(items):
                items.pop(index)
                self.draft_ref.update({
                    'items': items,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                return True
        return False
    
    def clear_draft(self):
        self.draft_ref.set({
            'items': [],
            'status': 'Draft',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True
    
    def approve_draft(self, approved_by):
        draft_doc = self.draft_ref.get()
        if draft_doc.exists:
            items = draft_doc.to_dict().get('items', [])
            if len(items) > 0:
                self.draft_ref.update({
                    'status': 'Approved',
                    'approved_by': approved_by,
                    'approved_at': firestore.SERVER_TIMESTAMP
                })
                return True, "✅ Draft approved!"
        return False, "Cannot approve empty draft"
    
    def send_orders(self, orders_data, sent_by):
        draft_doc = self.draft_ref.get()
        if draft_doc.exists:
            draft_data = draft_doc.to_dict()
            
            order_record = {
                'items': draft_data.get('items', []),
                'sent_by': sent_by,
                'sent_at': datetime.now().isoformat(),
                'orders_sent': orders_data
            }
            
            self.orders_ref.add(order_record)
            
            self.draft_ref.set({
                'items': [],
                'status': 'Draft',
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            return True, "✅ Orders sent and saved to history!"
        
        return False, "No draft to send"
    
    def get_order_history(self):
        docs = self.orders_ref.order_by('sent_at', direction=firestore.Query.DESCENDING).limit(20).stream()
        orders = []
        for doc in docs:
            order = doc.to_dict()
            order['id'] = doc.id
            orders.append(order)
        return orders

# ============================================
# WHATSAPP FUNCTIONS
# ============================================

def format_order_message(vendor_name, items):
    message = f"Hello {vendor_name},\n\n"
    message += "New Order:\n\n"
    
    for item in items:
        message += f"• {item['name']} - {item['quantity']}\n"
    
    message += "\nThanks!"
    return message

def create_whatsapp_url(phone, message):
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    if not clean_phone.startswith('91') and len(clean_phone) == 10:
        clean_phone = '91' + clean_phone
    
    encoded_message = urllib.parse.quote(message)
    url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    return url

# ============================================
# SESSION STATE
# ============================================

# ============================================
# LOGIN SCREEN
# ============================================

cafe_manager = CafeManager()

def login_screen():
    st.markdown("""
    <div class='welcome-banner'>
        <h1 style='color: white; margin: 0;'>🛒 OrderFlow</h1>
        <p style='color: white; margin: 0;'>Smart Inventory Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "✨ Create New Café", "🔓 Forgot Password"])
    
    # ============================================
    # TAB 1: LOGIN - PHONE + PASSWORD
    # ============================================
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            phone = st.text_input("Phone Number", placeholder="1234567890", max_chars=10)
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submitted:
            if not phone or not password:
                st.error("❌ Please fill all fields")
            elif len(phone) != 10 or not phone.isdigit():
                st.error("❌ Phone must be 10 digits")
            else:
                user = cafe_manager.verify_login(phone, password)
                
                if not user:
                    st.error("❌ Invalid phone number or password")
                else:
                    st.session_state.logged_in = True
                    st.session_state.cafe_id = user['cafe_id']
                    st.session_state.cafe_name = user['cafe_name']
                    st.session_state.user_name = user['name']
                    st.session_state.user_role = user['role']
                    st.session_state.user_phone = phone
                    
                    st.success(f"✅ Welcome back, {user['name']}!")
                    st.balloons()
                    st.rerun()
    
    # ============================================
    # TAB 2: CREATE NEW CAFÉ - PHONE + PASSWORD
    # ============================================
    with tab2:
        st.subheader("Create Your Café Account")
        
        with st.form("signup_form"):
            cafe_name = st.text_input("Café Name", placeholder="My Coffee Shop")
            owner_name = st.text_input("Owner Name", placeholder="Your Name")
            owner_phone = st.text_input("Phone Number", placeholder="1234567890", max_chars=10)
            password = st.text_input("Create Password", type="password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            
            submitted = st.form_submit_button("Create Café", use_container_width=True, type="primary")
        
        if submitted:
            if not cafe_name or not owner_name or not owner_phone or not password:
                st.error("❌ Please fill all fields")
            elif len(owner_phone) != 10 or not owner_phone.isdigit():
                st.error("❌ Phone must be 10 digits")
            elif password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(password) < 4:
                st.error("❌ Password must be at least 4 characters")
            else:
                cafe_id, message = cafe_manager.create_cafe(cafe_name, owner_name, owner_phone, password)
                
                if cafe_id:
                    st.success("🎉 Café created successfully!")
                    st.info(f"✅ You can now login with phone: **{owner_phone}** and your password")
                    
                    st.session_state.logged_in = True
                    st.session_state.cafe_id = cafe_id
                    st.session_state.cafe_name = cafe_name
                    st.session_state.user_name = owner_name
                    st.session_state.user_role = "Owner"
                    st.session_state.user_phone = owner_phone
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        st.markdown("---")
        st.info("💡 **Tip:** After creating your café, you can add staff members from the Staff menu.")
    
    # ============================================
    # TAB 3: FORGOT PASSWORD
    # ============================================
    with tab3:
        st.subheader("Reset Your Password")
        st.caption("Enter your phone number to reset your password")
        
        with st.form("forgot_password_form"):
            reset_phone = st.text_input("Phone Number", placeholder="1234567890", max_chars=10, key="reset_phone")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password", key="new_pass")
            confirm_new_password = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password", key="confirm_new_pass")
            
            submitted = st.form_submit_button("Reset Password", use_container_width=True, type="primary")
        
        if submitted:
            if not reset_phone or not new_password or not confirm_new_password:
                st.error("❌ Please fill all fields")
            elif len(reset_phone) != 10 or not reset_phone.isdigit():
                st.error("❌ Phone must be 10 digits")
            elif new_password != confirm_new_password:
                st.error("❌ Passwords don't match")
            elif len(new_password) < 4:
                st.error("❌ Password must be at least 4 characters")
            else:
                success, message = cafe_manager.reset_password(reset_phone, new_password)
                
                if success:
                    st.success("✅ " + message)
                    st.info("🔑 You can now login with your new password!")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")
        
        st.markdown("---")
        st.info("💡 **Note:** You can reset your password anytime using your registered phone number.")

# ============================================
# HOME SCREEN
# ============================================

def home_screen():
    draft = draft_manager.get_draft()
    status = draft.get('status', 'Draft')
    
    st.markdown(f"""
    <div class='welcome-banner'>
        <h2 style='color: white; margin: 0;'>Welcome back, {st.session_state.user_name}!</h2>
        <p style='color: white; margin: 0;'>☕ {st.session_state.cafe_name} • Role: {st.session_state.user_role}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Current Draft Status")
    with col2:
        if status == "Draft":
            st.markdown('<span class="status-draft">📝 Draft</span>', unsafe_allow_html=True)
        elif status == "Approved":
            st.markdown('<span class="status-approved">✅ Approved</span>', unsafe_allow_html=True)
    
    items = draft.get('items', [])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📦 Total Items", len(items))
    
    with col2:
        categories = len(set(item['category'] for item in items if item['category'] != 'Uncategorized'))
        st.metric("📂 Categories", categories)
    
    with col3:
        vendors = len(vendor_manager.get_all_vendors())
        st.metric("👥 Vendors", vendors)
    
    st.markdown("---")
    
    st.subheader("Quick Actions")
    
    if st.session_state.user_role == "Staff":
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Items", use_container_width=True, type="primary"):
                st.session_state.current_page = "add_items"
                st.rerun()
        
        with col2:
            if st.button("📋 View Draft", use_container_width=True):
                st.session_state.current_page = "view_draft"
                st.rerun()
    
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Items", use_container_width=True):
                st.session_state.current_page = "add_items"
                st.rerun()
        
        with col2:
            if st.button("📋 View Draft", use_container_width=True):
                st.session_state.current_page = "view_draft"
                st.rerun()
        
        with col3:
            if len(items) > 0 and status == "Draft":
                if st.button("✅ Review", use_container_width=True, type="primary"):
                    st.session_state.current_page = "review"
                    st.rerun()
            elif status == "Approved":
                if st.button("📤 Send Orders", use_container_width=True, type="primary"):
                    st.session_state.current_page = "send_orders"
                    st.rerun()
        
        with col4:
            if st.button("👥 Vendors", use_container_width=True):
                st.session_state.current_page = "vendors"
                st.rerun()
    
    st.markdown("---")
    
    if len(items) > 0:
        st.subheader("Current Draft Preview")
        recent = items[-5:]
        recent.reverse()
        
        for item in recent:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{item['name']}**")
            with col2:
                st.write(f"{item['quantity']}")
            with col3:
                st.caption(item['category'][:12])
        
        if len(items) > 5:
            st.caption(f"...and {len(items) - 5} more items")
    else:
        st.info("📋 No items in draft. Click 'Add Items' to get started!")

# ============================================
# ADD ITEMS SCREEN
# ============================================

def add_items_screen():
    st.title("➕ Add New Item")
    
    draft = draft_manager.get_draft()
    status = draft.get('status', 'Draft')
    
    if status != "Draft":
        st.warning(f"⚠️ Draft is currently **{status}**. Cannot add items.")
        if st.button("← Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    # Show success message if items were just added
    if 'items_added_count' in st.session_state and st.session_state.items_added_count > 0:
        st.success(f"✅ Successfully added {st.session_state.items_added_count} items to draft!")
        st.balloons()
        st.session_state.items_added_count = 0  # Reset
    
    # BULK ADD MODE
    st.subheader("📝 Bulk Add Items")
    st.caption("Enter items one per line in format: Item Name, Quantity")
    st.caption("Example: Milk, 10L")
    
    bulk_items = st.text_area(
        "Items List",
        placeholder="Milk, 10L\nChicken, 5kg\nOnion, 3kg\nButter, 2kg",
        height=200
    )
    
    added_by = st.text_input("Added By", value=st.session_state.user_name)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Add All Items", type="primary", use_container_width=True):
            if not bulk_items or not bulk_items.strip():
                st.error("❌ Please enter at least one item")
            else:
                lines = bulk_items.strip().split('\n')
                added_count = 0
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if ',' in line:
                        parts = line.split(',', 1)
                        item_name = parts[0].strip()
                        quantity = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        item_name = line.strip()
                        quantity = ""
                    
                    if item_name:
                        draft_manager.add_item(item_name, quantity, added_by)
                        added_count += 1
                
                if added_count > 0:
                    st.session_state.items_added_count = added_count
                    st.rerun()
                else:
                    st.error("❌ No valid items found")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

# ============================================
# VIEW DRAFT SCREEN
# ============================================

def view_draft_screen():
    st.title("📋 Current Draft")
    
    draft = draft_manager.get_draft()
    items = draft.get('items', [])
    status = draft.get('status', 'Draft')
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Status: {status}")
    with col2:
        if status == "Draft":
            st.markdown('<span class="status-draft">📝 Draft</span>', unsafe_allow_html=True)
        elif status == "Approved":
            st.markdown('<span class="status-approved">✅ Approved</span>', unsafe_allow_html=True)
    
    if len(items) == 0:
        st.info("📋 Draft is empty.")
        if st.button("➕ Add Items", type="primary"):
            st.session_state.current_page = "add_items"
            st.rerun()
        return
    
    # Quick add items in view draft
    if status == "Draft":
        st.subheader("➕ Quick Add Items")
        with st.form("quick_add_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                quick_item = st.text_input("Item Name", placeholder="e.g., Milk")
            with col2:
                quick_qty = st.text_input("Quantity", placeholder="10L")
            
            if st.form_submit_button("Add Item", use_container_width=True):
                if quick_item and quick_item.strip():
                    draft_manager.add_item(quick_item, quick_qty if quick_qty else "", st.session_state.user_name)
                    st.success(f"✅ Added {quick_item}")
                    st.rerun()
        
        st.markdown("---")
    
    by_category = {}
    uncategorized_items = []
    
    for item in items:
        cat = item['category']
        if cat == "Uncategorized":
            uncategorized_items.append(item)
        else:
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)
    
    # Show uncategorized items first with category assignment
    if len(uncategorized_items) > 0:
        with st.expander(f"⚠️ Uncategorized ({len(uncategorized_items)} items)", expanded=True):
            st.warning("These items need to be categorized")
            
            for item in uncategorized_items:
                idx = items.index(item)
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{item['name']}**")
                    st.caption(f"Added by {item['added_by']}")
                
                with col2:
                    st.write(f"{item['quantity']}")
                
                with col3:
                    if status == "Draft":
                        # Category selection
                        categories_list = list(KEYWORDS_DATABASE.keys()) + ["➕ Create New Category"]
                        selected_cat = st.selectbox(
                            "Assign Category",
                            categories_list,
                            key=f"cat_{idx}",
                            label_visibility="collapsed"
                        )
                        
                        if selected_cat == "➕ Create New Category":
                            new_cat = st.text_input("New Category Name", key=f"newcat_{idx}", placeholder="Enter category name")
                            if new_cat and st.button("Create & Assign", key=f"create_{idx}"):
                                if new_cat not in KEYWORDS_DATABASE:
                                    KEYWORDS_DATABASE[new_cat] = [item['name'].lower()]
                                    items[idx]['category'] = new_cat
                                    draft_manager.draft_ref.update({'items': items})
                                    st.success(f"✅ Created '{new_cat}' and assigned")
                                    st.rerun()
                        else:
                            if st.button("Assign", key=f"assign_{idx}"):
                                # Add to category keywords
                                item_lower = item['name'].lower()
                                if item_lower not in KEYWORDS_DATABASE[selected_cat]:
                                    KEYWORDS_DATABASE[selected_cat].append(item_lower)
                                items[idx]['category'] = selected_cat
                                draft_manager.draft_ref.update({'items': items})
                                st.success(f"✅ Assigned to {selected_cat}")
                                st.rerun()
                
                with col4:
                    if status == "Draft":
                        if st.button("🗑️", key=f"del_uncat_{idx}"):
                            draft_manager.remove_item(idx)
                            st.rerun()
                
                st.markdown("---")
    
    # Show categorized items
    for category, cat_items in by_category.items():
        with st.expander(f"✅ {category} ({len(cat_items)} items)", expanded=True):
            for item in cat_items:
                idx = items.index(item)
                
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.markdown(f"**{item['name']}**")
                    st.caption(f"Added by {item['added_by']}")
                
                with col2:
                    st.write(f"{item['quantity']}")
                
                with col3:
                    if status == "Draft":
                        if st.button("🗑️", key=f"del_{idx}"):
                            draft_manager.remove_item(idx)
                            st.rerun()
                
                st.markdown("---")
    
    st.markdown("---")
    
    if status == "Draft":
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add More Items", use_container_width=True):
                st.session_state.current_page = "add_items"
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
                draft_manager.clear_draft()
                st.success("Draft cleared!")
                st.rerun()

# ============================================
# REVIEW SCREEN
# ============================================

def review_screen():
    st.title("✅ Review & Approve Draft")
    
    if st.session_state.user_role != "Owner":
        st.error("❌ Only owners can approve drafts")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    draft = draft_manager.get_draft()
    items = draft.get('items', [])
    status = draft.get('status', 'Draft')
    
    if len(items) == 0:
        st.warning("⚠️ Cannot approve empty draft")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    if status != "Draft":
        st.info(f"ℹ️ This draft is already **{status}**")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    st.subheader("Draft Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(items))
    with col2:
        categories = len(set(item['category'] for item in items))
        st.metric("Categories", categories)
    with col3:
        uncategorized = sum(1 for item in items if item['category'] == 'Uncategorized')
        st.metric("Uncategorized", uncategorized)
    
    st.markdown("---")
    
    by_category = {}
    for item in items:
        cat = item['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    st.subheader("Items by Category")
    
    for category, cat_items in by_category.items():
        icon = "⚠️" if category == "Uncategorized" else "✅"
        
        with st.expander(f"{icon} {category} ({len(cat_items)} items)", expanded=True):
            for item in cat_items:
                idx = items.index(item)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item['name']}** - {item['quantity']}")
                with col2:
                    st.caption(f"by {item['added_by']}")
                with col3:
                    # Allow owner to delete items during review
                    if st.button("🗑️", key=f"review_del_{idx}"):
                        draft_manager.remove_item(idx)
                        st.rerun()
    
    st.markdown("---")
    
    # Quick add during review
    st.subheader("➕ Add Items During Review")
    with st.form("review_add_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            review_item = st.text_input("Item Name", placeholder="e.g., Sugar")
        with col2:
            review_qty = st.text_input("Quantity", placeholder="5kg")
        
        if st.form_submit_button("Add Item"):
            if review_item and review_item.strip():
                draft_manager.add_item(review_item, review_qty if review_qty else "", st.session_state.user_name)
                st.success(f"✅ Added {review_item}")
                st.rerun()
    
    st.markdown("---")
    
    if uncategorized > 0:
        st.warning(f"⚠️ {uncategorized} items are uncategorized.")
    
    st.subheader("Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve Draft", type="primary", use_container_width=True):
            success, message = draft_manager.approve_draft(st.session_state.user_name)
            if success:
                st.success(message)
                st.balloons()
                st.session_state.current_page = "home"
                st.rerun()
    
    with col2:
        if st.button("📝 Edit in Draft View", use_container_width=True):
            st.session_state.current_page = "view_draft"
            st.rerun()
    
    with col3:
        if st.button("← Cancel", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

# ============================================
# VENDORS SCREEN
# ============================================

def vendors_screen():
    st.title("👥 Vendor Management")
    
    if st.session_state.user_role != "Owner":
        st.error("❌ Only owners can manage vendors")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    st.subheader("➕ Add New Vendor")
    
    with st.form("add_vendor"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox("Category", list(KEYWORDS_DATABASE.keys()))
            vendor_name = st.text_input("Vendor Name")
        
        with col2:
            phone = st.text_input("Phone Number (10 digits)", max_chars=10)
            vendor_type = st.selectbox("Type", ["WhatsApp", "Call"])
        
        if st.form_submit_button("Add Vendor", use_container_width=True):
            if not vendor_name or not phone:
                st.error("❌ Please fill all fields")
            elif len(phone) != 10 or not phone.isdigit():
                st.error("❌ Phone must be 10 digits")
            else:
                vendor_manager.add_vendor(category, vendor_name, phone, vendor_type)
                st.success(f"✅ Added {vendor_name} for {category}")
                st.rerun()
    
    st.markdown("---")
    
    st.subheader("📋 All Vendors")
    
    vendors = vendor_manager.get_all_vendors()
    
    if len(vendors) == 0:
        st.info("No vendors added yet.")
    else:
        by_category = {}
        for vendor in vendors:
            cat = vendor['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(vendor)
        
        for category, cat_vendors in by_category.items():
            with st.expander(f"📁 {category} ({len(cat_vendors)} vendors)", expanded=False):
                for vendor in cat_vendors:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**{vendor['vendor_name']}**")
                        st.caption(f"📞 {vendor['phone']}")
                    
                    with col2:
                        st.write(f"Type: {vendor['vendor_type']}")
                    
                    with col3:
                        if st.button("🗑️", key=f"del_vendor_{vendor['id']}"):
                            vendor_manager.delete_vendor(vendor['id'])
                            st.rerun()
                    
                    st.markdown("---")

# ============================================
# SEND ORDERS SCREEN
# ============================================

def send_orders_screen():
    st.title("📤 Send Orders to Vendors")
    
    if st.session_state.user_role != "Owner":
        st.error("❌ Only owners can send orders")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    draft = draft_manager.get_draft()
    items = draft.get('items', [])
    status = draft.get('status', 'Draft')
    
    if status != "Approved":
        st.warning(f"⚠️ Draft must be approved first. Current status: {status}")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    st.subheader("Orders by Category")
    
    by_category = {}
    for item in items:
        cat = item['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    messages_to_send = []
    
    for category, cat_items in by_category.items():
        with st.expander(f"📦 {category} ({len(cat_items)} items)", expanded=True):
            vendor = vendor_manager.get_vendor_by_category(category)
            
            if not vendor:
                st.warning(f"⚠️ No vendor assigned for {category}")
                
                # Quick add vendor form
                st.subheader(f"➕ Add Vendor for {category}")
                with st.form(f"quick_vendor_{category}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        vendor_name = st.text_input("Vendor Name", key=f"vname_{category}")
                    with col2:
                        vendor_phone = st.text_input("Phone (10 digits)", max_chars=10, key=f"vphone_{category}")
                    
                    vendor_type = st.selectbox("Type", ["WhatsApp", "Call"], key=f"vtype_{category}")
                    
                    if st.form_submit_button("Add Vendor"):
                        if not vendor_name or not vendor_phone:
                            st.error("❌ Please fill all fields")
                        elif len(vendor_phone) != 10 or not vendor_phone.isdigit():
                            st.error("❌ Phone must be 10 digits")
                        else:
                            vendor_manager.add_vendor(category, vendor_name, vendor_phone, vendor_type)
                            st.success(f"✅ Added {vendor_name} for {category}")
                            st.rerun()
            else:
                st.success(f"✅ Vendor: {vendor['vendor_name']} - {vendor['phone']}")
                
                message = format_order_message(vendor['vendor_name'], cat_items)
                
                st.markdown('<div class="whatsapp-message">', unsafe_allow_html=True)
                st.text(message)
                st.markdown('</div>', unsafe_allow_html=True)
                
                whatsapp_url = create_whatsapp_url(vendor['phone'], message)
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.link_button(
                        "📱 Send via WhatsApp",
                        whatsapp_url,
                        use_container_width=True
                    )
                
                messages_to_send.append({
                    'category': category,
                    'vendor': vendor['vendor_name'],
                    'phone': vendor['phone'],
                    'message': message
                })
            
            st.markdown("---")
    
    st.markdown("---")
    
    if len(messages_to_send) > 0:
        if st.button("✅ Mark All as Sent", type="primary", use_container_width=True):
            success, message = draft_manager.send_orders(messages_to_send, st.session_state.user_name)
            if success:
                st.success(message)
                st.balloons()
                st.session_state.current_page = "home"
                st.rerun()
    
    if st.button("← Back to Home", use_container_width=True):
        st.session_state.current_page = "home"
        st.rerun()

# ============================================
# HISTORY SCREEN
# ============================================

def history_screen():
    st.title("📜 Order History")
    
    if st.session_state.user_role != "Owner":
        st.error("❌ Only owners can view history")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    orders = draft_manager.get_order_history()
    
    if len(orders) == 0:
        st.info("No orders sent yet.")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    st.subheader(f"Total Orders: {len(orders)}")
    
    for order in orders:
        order_date = order.get('sent_at', 'Unknown')
        if isinstance(order_date, str):
            try:
                order_date = datetime.fromisoformat(order_date).strftime('%b %d, %Y %I:%M %p')
            except:
                pass
        
        with st.expander(f"📦 Order sent on {order_date}", expanded=False):
            st.caption(f"Sent by: {order.get('sent_by', 'Unknown')}")
            
            items = order.get('items', [])
            by_category = {}
            
            for item in items:
                cat = item.get('category', 'Uncategorized')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)
            
            for category, cat_items in by_category.items():
                st.write(f"**{category}:**")
                for item in cat_items:
                    st.write(f"  • {item['name']} - {item['quantity']}")

# ============================================
# STAFF MANAGEMENT SCREEN
# ============================================

def staff_screen():
    st.title("👥 Staff Management")
    
    if st.session_state.user_role != "Owner":
        st.error("❌ Only owners can manage staff")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    st.subheader("➕ Add New Staff Member")
    
    with st.form("add_staff"):
        col1, col2 = st.columns(2)
        
        with col1:
            staff_name = st.text_input("Staff Name")
        
        with col2:
            staff_phone = st.text_input("Staff Phone (10 digits)", max_chars=10)
        
        staff_password = st.text_input("Staff Password", type="password", placeholder="Create password for staff")
        
        if st.form_submit_button("Add Staff", use_container_width=True):
            if not staff_name or not staff_phone or not staff_password:
                st.error("❌ Please fill all fields")
            elif len(staff_phone) != 10 or not staff_phone.isdigit():
                st.error("❌ Phone must be 10 digits")
            elif len(staff_password) < 4:
                st.error("❌ Password must be at least 4 characters")
            else:
                success, message = cafe_manager.add_staff(
                    st.session_state.cafe_id,
                    st.session_state.cafe_name,
                    staff_name,
                    staff_phone,
                    staff_password
                )
                if success:
                    st.success(f"✅ Added {staff_name} as staff member")
                    st.info(f"📱 They can login with phone **{staff_phone}** and the password you set")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    st.markdown("---")
    
    st.subheader("📋 All Users")
    
    # Get all users
    users = cafe_manager.get_all_staff(st.session_state.cafe_id)
    
    if len(users) == 0:
        st.info("No users found.")
    else:
        for user in users:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                icon = "👑" if user['role'] == 'Owner' else "👤"
                st.write(f"{icon} **{user['name']}**")
                st.caption(f"📞 {user['phone']}")
            
            with col2:
                st.write(f"Role: {user['role']}")
            
            with col3:
                if user['role'] != 'Owner':
                    if st.button("🗑️", key=f"del_user_{user['id']}"):
                        cafe_manager.delete_staff(user['id'])
                        st.success(f"Removed {user['name']}")
                        st.rerun()
            
            st.markdown("---")

# ============================================
# CATEGORY MANAGEMENT SCREEN
# ============================================

def categories_screen():
    st.title("📂 Category Management")
    
    if st.session_state.user_role != "Owner":
        st.error("❌ Only owners can manage categories")
        if st.button("← Back"):
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    st.subheader("All Categories & Items")
    
    for category, keywords in KEYWORDS_DATABASE.items():
        with st.expander(f"📁 {category} ({len(keywords)} items)", expanded=False):
            
            st.caption("Items in this category:")
            
            if len(keywords) == 0:
                st.info("No items in this category yet")
            else:
                cols_per_row = 3
                rows = [keywords[i:i + cols_per_row] for i in range(0, len(keywords), cols_per_row)]
                
                for row in rows:
                    cols = st.columns(cols_per_row)
                    for idx, item in enumerate(row):
                        with cols[idx]:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"• {item}")
                            with col2:
                                if st.button("🗑️", key=f"del_{category}_{item}"):
                                    KEYWORDS_DATABASE[category].remove(item)
                                    st.success(f"✅ Deleted '{item}'")
                                    st.rerun()
            
            st.markdown("---")
            
            with st.form(f"add_to_{category}"):
                new_item = st.text_input("Add new item keyword", placeholder="e.g., paneer, yogurt")
                
                if st.form_submit_button("➕ Add to Category"):
                    if new_item and new_item.strip():
                        item_lower = new_item.lower().strip()
                        if item_lower not in keywords:
                            KEYWORDS_DATABASE[category].append(item_lower)
                            st.success(f"✅ Added '{new_item}' to {category}")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ '{new_item}' already exists in this category")
                    else:
                        st.error("❌ Please enter an item name")
    
    st.markdown("---")
    
    st.subheader("➕ Create New Category")
    
    with st.form("create_new_category"):
        new_cat_name = st.text_input("Category Name", placeholder="e.g., Frozen Foods")
        first_item = st.text_input("First Item (optional)", placeholder="e.g., ice cream")
        
        if st.form_submit_button("Create Category"):
            if new_cat_name and new_cat_name.strip():
                if new_cat_name.strip() not in KEYWORDS_DATABASE:
                    keywords_list = [first_item.lower().strip()] if first_item else []
                    KEYWORDS_DATABASE[new_cat_name.strip()] = keywords_list
                    st.success(f"✅ Created category '{new_cat_name}'")
                    st.rerun()
                else:
                    st.error(f"❌ Category '{new_cat_name}' already exists")
            else:
                st.error("❌ Please enter category name")

# ============================================
# MAIN APP
# ============================================

def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    # Check if logged in
    if not st.session_state.logged_in:
        login_screen()
        return
    
    # Create managers for this cafe
    global draft_manager, vendor_manager
    draft_manager = DraftManager(st.session_state.cafe_id)
    vendor_manager = VendorManager(st.session_state.cafe_id)
    
    # Sidebar
    with st.sidebar:
        st.title("🛒 StockUp")
        
        # Show café info
        st.markdown(f"""
        <div class="cafe-id-box">
            <strong>☕ {st.session_state.cafe_name}</strong><br>
            <small>Café ID: {st.session_state.cafe_id}</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("➕ Add Items", use_container_width=True):
            st.session_state.current_page = "add_items"
            st.rerun()
        
        if st.button("📋 View Draft", use_container_width=True):
            st.session_state.current_page = "view_draft"
            st.rerun()
        
        # Owner-only buttons
        if st.session_state.user_role == "Owner":
            st.markdown("---")
            st.caption("Owner Menu")
            
            draft = draft_manager.get_draft()
            status = draft.get('status', 'Draft')
            items = draft.get('items', [])
            
            if len(items) > 0 and status == "Draft":
                if st.button("✅ Review", use_container_width=True):
                    st.session_state.current_page = "review"
                    st.rerun()
            
            if status == "Approved":
                if st.button("📤 Send Orders", use_container_width=True, type="primary"):
                    st.session_state.current_page = "send_orders"
                    st.rerun()
            
            if st.button("👥 Vendors", use_container_width=True):
                st.session_state.current_page = "vendors"
                st.rerun()
            
            if st.button("👤 Staff", use_container_width=True):
                st.session_state.current_page = "staff"
                st.rerun()
            
            if st.button("📜 History", use_container_width=True):
                st.session_state.current_page = "history"
                st.rerun()
            
            if st.button("📂 Categories", use_container_width=True):
                st.session_state.current_page = "categories"
                st.rerun()
        
        st.markdown("---")
        
        st.caption(f"**{st.session_state.user_name}**")
        st.caption(f"Role: {st.session_state.user_role}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_page = "home"
            st.rerun()
    
    # Route to screens
    if st.session_state.current_page == "home":
        home_screen()
    elif st.session_state.current_page == "add_items":
        add_items_screen()
    elif st.session_state.current_page == "view_draft":
        view_draft_screen()
    elif st.session_state.current_page == "review":
        review_screen()
    elif st.session_state.current_page == "vendors":
        vendors_screen()
    elif st.session_state.current_page == "send_orders":
        send_orders_screen()
    elif st.session_state.current_page == "history":
        history_screen()
    elif st.session_state.current_page == "staff":
        staff_screen()
    elif st.session_state.current_page == "categories":
        categories_screen()

if __name__ == "__main__":
    main()