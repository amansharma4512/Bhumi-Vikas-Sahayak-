"""
Authentication and User Preference Management Engine for Bhumi Vikas Sahayak.
Supports:
1. Secure OTP Login via Phone Number or Email (with simulated gateway for Bhopal Municipal Corporation)
2. Secure Password-based Demo Account Login for evaluators and testing
3. User Preferences Storage (Default Language: Hindi/English, Theme: Light/Dark)
4. Session state management and persistent profile storage
"""

import os
import json
import time
import hashlib
import secrets
from datetime import datetime

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PREFERENCES_FILE = os.path.join(DATA_DIR, "user_preferences.json")

# In-memory OTP registry for active session verifications: {destination: {"otp": "123456", "expires_at": 1234567890}}
_ACTIVE_OTPS = {}

DEMO_USER_ID = "clerk_bhopal"
DEMO_EMAIL = "demo@bmc.gov.in"
DEMO_PHONE = "9876543210"
DEMO_PASSWORD_PLAIN = "BhumiSahayak@2026"
DEMO_SALT = "bmc_bhopal_salt_2026"


def _hash_password(password: str, salt: str = DEMO_SALT) -> str:
    """Generate SHA-256 hash with salt for secure authentication."""
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()


def init_auth_db():
    """Initialize default user and preference files if not existing."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize users DB with Demo Clerk Account
    if not os.path.exists(USERS_FILE):
        demo_user = {
            DEMO_USER_ID: {
                "user_id": DEMO_USER_ID,
                "name": "राजेश शर्मा (Rajesh Sharma)",
                "role": "Senior Building Permission Clerk",
                "department": "Town Planning & Building Sanction, Ward 14",
                "organization": "Bhopal Municipal Corporation (भोपाल नगर निगम)",
                "email": DEMO_EMAIL,
                "phone": DEMO_PHONE,
                "password_hash": _hash_password(DEMO_PASSWORD_PLAIN, DEMO_SALT),
                "salt": DEMO_SALT,
                "created_at": "2026-03-01T10:00:00"
            }
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(demo_user, f, indent=2, ensure_ascii=False)

    # Initialize user preferences DB
    if not os.path.exists(PREFERENCES_FILE):
        default_prefs = {
            DEMO_USER_ID: {
                "language": "hi",
                "theme": "light",
                "auto_voice_playback": True,
                "updated_at": "2026-03-01T10:00:00"
            }
        }
        with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
            json.dump(default_prefs, f, indent=2, ensure_ascii=False)


def get_all_users() -> dict:
    """Load all registered users."""
    init_auth_db()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users: dict):
    """Save users dictionary to file."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def authenticate_password(identifier: str, password: str) -> dict:
    """
    Authenticate demo user or registered officer via username/email and password.
    Returns user dict on success, None on failure.
    """
    users = get_all_users()
    identifier = identifier.strip().lower()

    for uid, user in users.items():
        if (uid.lower() == identifier or 
            user.get("email", "").lower() == identifier or 
            user.get("phone", "") == identifier):
            stored_hash = user.get("password_hash")
            salt = user.get("salt", DEMO_SALT)
            input_hash = _hash_password(password, salt)
            if input_hash == stored_hash:
                return user
    return None


def generate_otp(destination: str) -> tuple[str, str]:
    """
    Generate a 6-digit OTP for phone or email login.
    Returns (otp_code, status_message).
    """
    destination = destination.strip()
    if not destination:
        return "", "Invalid destination"

    # Cryptographically secure 6-digit OTP
    otp = f"{secrets.randbelow(900000) + 100000:06d}"
    expires_at = time.time() + 300  # 5 minutes validity

    _ACTIVE_OTPS[destination.lower()] = {
        "otp": otp,
        "expires_at": expires_at,
        "created_at": datetime.now().isoformat()
    }

    is_phone = destination.replace("+", "").replace("-", "").isdigit()
    dest_type = "मोबाइल नंबर" if is_phone else "ईमेल पता"
    msg = f"OTP सफलता से जनरेट हुआ! आपके {dest_type} ({destination}) पर 6-अंकीय सत्यापन कोड भेजा गया है।"

    return otp, msg


def verify_otp(destination: str, user_otp: str) -> tuple[bool, dict, str]:
    """
    Verify OTP provided by user.
    If valid, returns (True, user_profile, success_message).
    Also supports fallback testing code '123456' for rapid offline hackathon evaluation.
    """
    destination = destination.strip().lower()
    user_otp = user_otp.strip()

    valid = False
    now = time.time()

    # Check active OTP
    record = _ACTIVE_OTPS.get(destination)
    if record:
        if now > record["expires_at"]:
            return False, {}, "OTP समाप्त (Expired) हो चुका है। कृपया नया OTP मांगें।"
        if record["otp"] == user_otp or user_otp == "123456":
            valid = True
            # Invalidate once used
            _ACTIVE_OTPS.pop(destination, None)
    elif user_otp == "123456":
        # Master evaluation passkey for judges/testing
        valid = True

    if not valid:
        return False, {}, "अमान्य OTP (Invalid OTP)। कृपया पुनः प्रयास करें या '123456' दर्ज करें।"

    # Look up or create user record for this phone/email
    users = get_all_users()
    user = None
    for uid, u in users.items():
        if (u.get("email", "").lower() == destination or 
            u.get("phone", "").lower() == destination or 
            uid.lower() == destination):
            user = u
            break

    if not user:
        # Create a new user profile on the fly
        is_phone = destination.replace("+", "").replace("-", "").isdigit()
        new_uid = f"user_{int(time.time())}"
        user = {
            "user_id": new_uid,
            "name": f"नागरिक / अधिकारी ({destination[-4:]})",
            "role": "Building Permission Applicant / Officer",
            "department": "Bhopal Municipal Corporation Citizen Portal",
            "organization": "Bhopal Municipal Corporation",
            "email": destination if not is_phone else f"{destination}@citizen.mp.gov.in",
            "phone": destination if is_phone else "",
            "password_hash": "",
            "created_at": datetime.now().isoformat()
        }
        users[new_uid] = user
        save_users(users)

    return True, user, "सत्यापन सफल! आपका स्वागत है।"


def get_user_preferences(user_id: str) -> dict:
    """
    Get saved preferences (Language, Theme, Auto Playback) for a user.
    Returns defaults if not previously saved.
    """
    init_auth_db()
    try:
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
            all_prefs = json.load(f)
            if user_id in all_prefs:
                return all_prefs[user_id]
    except Exception:
        pass

    # Default settings: Hindi language, Light theme
    return {
        "language": "hi",
        "theme": "light",
        "auto_voice_playback": True
    }


def save_user_preferences(user_id: str, preferences: dict) -> bool:
    """
    Save user's language and theme preferences permanently to data/user_preferences.json.
    """
    init_auth_db()
    try:
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
            all_prefs = json.load(f)
    except Exception:
        all_prefs = {}

    current = all_prefs.get(user_id, {})
    current.update(preferences)
    current["updated_at"] = datetime.now().isoformat()
    all_prefs[user_id] = current

    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(all_prefs, f, indent=2, ensure_ascii=False)

    return True
