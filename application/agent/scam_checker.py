import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def load_scam_data():
    """Load scam database from CSV file"""
    try:
        if os.path.exists("data/scam_contacts.csv"):
            scam_df = pd.read_csv("data/scam_contacts.csv")
        else:
            # Create directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            # Create empty CSV with headers
            scam_df = pd.DataFrame(columns=['email', 'phone'])
            scam_df.to_csv("data/scam_contacts.csv", index=False)
        
        # Ensure columns exist
        if 'email' not in scam_df.columns:
            scam_df['email'] = ''
        if 'phone' not in scam_df.columns:
            scam_df['phone'] = ''
            
        return scam_df
    except Exception as e:
        logger.error(f"Error loading scam data: {str(e)}")
        return pd.DataFrame(columns=['email', 'phone'])

# Initialize the scam data once when the script is run
scam_df = load_scam_data()

def check_scam_database(email: str, phone: str) -> dict:
    """Check if email or phone exists in scam database"""
    result = {
        "email_flagged": False,
        "phone_flagged": False,
        "flagged_email": None,
        "flagged_phone": None,
    }

    try:
        global scam_df
        
        # Check email
        if email and not scam_df.empty:
            email_matches = scam_df['email'].str.lower() == email.lower()
            if email_matches.any():
                result["email_flagged"] = True
                result["flagged_email"] = email

        # Check phone
        if phone and not scam_df.empty:
            # Clean phone number for comparison
            clean_phone = ''.join(filter(str.isdigit, phone))
            phone_matches = scam_df['phone'].apply(
                lambda x: ''.join(filter(str.isdigit, str(x))) == clean_phone if pd.notna(x) else False
            )
            if phone_matches.any():
                result["phone_flagged"] = True
                result["flagged_phone"] = phone

    except Exception as e:
        logger.error(f"Scam database check error: {str(e)}")

    return result

def add_scam_to_database(email: str, phone: str):
    """Add email and phone number to scam database"""
    try:
        global scam_df
        
        # Reload data to get latest
        scam_df = load_scam_data()
        
        # Check if already exists
        existing_email = scam_df['email'].str.lower().eq(email.lower()).any() if email else False
        existing_phone = False
        if phone:
            clean_phone = ''.join(filter(str.isdigit, phone))
            existing_phone = scam_df['phone'].apply(
                lambda x: ''.join(filter(str.isdigit, str(x))) == clean_phone if pd.notna(x) else False
            ).any()
        
        # Only add if not already exists
        if not existing_email and not existing_phone:
            # Append new scam data
            new_data = pd.DataFrame([[email or '', phone or '']], columns=['email', 'phone'])
            scam_df = pd.concat([scam_df, new_data], ignore_index=True)
            
            # Save back to CSV
            scam_df.to_csv("data/scam_contacts.csv", index=False)
            logger.info(f"Added scam data: Email - {email}, Phone - {phone}")
        else:
            logger.info(f"Scam data already exists: Email - {email}, Phone - {phone}")
            
    except Exception as e:
        logger.error(f"Error adding scam to database: {str(e)}")