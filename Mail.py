import os
from google import genai
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import pandas as pd

file_path = "Files/ai.csv"

# Fetching credentials securely from environment variables
sender_email = os.environ.get("SENDER_EMAIL", "sowjanyamanthena@gmail.com")
sender_password = os.environ.get("SENDER_PASSWORD") 
gemini_api_key = os.environ.get("GEMINI_API_KEY")

def generate_custom_wish(name, age):
    # Pass the API key securely using the variable
    client = genai.Client(api_key=gemini_api_key)
    prompt = f"""
    You are a warm and friendly assistant. Generate a highly personalized, single-paragraph birthday message.
    
    Recipient Details:
    - Name: {name}
    - Age: {age}
    
    Tone guidelines based on age:
    - Under 13 (Kids): Fun, simple language, exciting emojis, themes of playing and growing up.
    - 13-19 (Teens): Cool, casual, encouraging, not cringey or overly mushy.
    - 20-29 (Young Adults): Energetic, motivating, lighthearted joke about "adulting."
    - 30-59 (Adults): Sincere, warm, celebratory, recognizing achievements/milestones.
    - 60+ (Seniors): Heartwarming, respectful, focusing on wisdom, joy, and good health.
    
    Output requirement: Return ONLY the raw birthday message text. Do not include subject lines, markdown formatting, or introductory text.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash", # Updated to correct production model identifier
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"LLM Error, falling back to default message: {e}")
        return f"Happy Birthday, {name}! Wishing you a wonderful year ahead!"

def check_bday():
    df = pd.read_csv(file_path)
    today = datetime.now()
    current_month = today.month
    current_day = today.day

    for index, row in df.iterrows():
        dob_str = str(row.iloc[1])
        dob = datetime.strptime(dob_str, "%d-%m-%Y")

        if dob.month == current_month and dob.day == current_day:
            recipient_name = row.iloc[0]  
            recipient_email = row.iloc[2]  

            age = today.year - dob.year
            if (today.month, today.day) < (dob.month, dob.day):
                age -= 1

            print(f"Found birthday: {recipient_name} is turning {age} today!")
            custom_message = generate_custom_wish(recipient_name, age)

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, sender_password)
                
                msg = MIMEText(custom_message)
                msg["Subject"] = f"Happy Birthday, {recipient_name}! 🎉"
                msg["From"] = sender_email
                msg["To"] = recipient_email

                server.sendmail(sender_email, recipient_email, msg.as_string())
                print(f"Birthday mail successfully sent to: {recipient_email}")
                server.quit()
            except Exception as e:
                print(f"SMTP Error sending email to {recipient_email}: {e}")

check_bday()
print("complete")
