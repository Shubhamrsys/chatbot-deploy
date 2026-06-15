# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)

# Allow CORS for your Vercel frontend URLs
CORS(app, origins=[
    "https://chatbot-frontend-ruddy-one.vercel.app",
    "https://chatbot-frontend-ajovzt96r-shubhamrsys-s-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:5500"
])

# Sample patient data
patients_data = {
    1001: {"name": "John Smith", "age": 65, "gender": "Male", "conditions": ["Diabetes", "Hypertension"]},
    1002: {"name": "Maria Garcia", "age": 72, "gender": "Female", "conditions": ["Heart Failure"]},
    1003: {"name": "Robert Johnson", "age": 58, "gender": "Male", "conditions": ["Hypertension"]},
    1004: {"name": "Patricia Brown", "age": 45, "gender": "Female", "conditions": []},
    1005: {"name": "Wei Zhang", "age": 38, "gender": "Male", "conditions": ["Diabetes"]},
}

# Sample appointments
appointments = {
    1001: [
        {"date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"), "time": "10:00 AM", "type": "Diabetes Follow-up", "provider": "Dr. Sarah Johnson", "location": "Main Hospital, Floor 3", "prep": "Fast for 8 hours. Bring your glucose meter."},
        {"date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"), "time": "2:30 PM", "type": "Cardiology Check", "provider": "Dr. Michael Chen", "location": "Heart Center", "prep": "Take regular medications."}
    ],
    1002: [
        {"date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), "time": "11:00 AM", "type": "Heart Failure Follow-up", "provider": "Dr. Robert Taylor", "location": "Cardiology Clinic", "prep": "Daily weight monitoring. Call if weight increases."}
    ],
    1003: [
        {"date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"), "time": "1:00 PM", "type": "Hypertension Check", "provider": "Dr. Emily Rodriguez", "location": "Primary Care Clinic", "prep": "Take blood pressure medication as usual."}
    ],
    1004: [
        {"date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"), "time": "3:00 PM", "type": "Annual Physical", "provider": "Dr. James Wilson", "location": "Family Medicine", "prep": "Bring insurance card and ID."}
    ],
    1005: [
        {"date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "time": "9:00 AM", "type": "Lab Work", "provider": "Lab Services", "location": "Diagnostic Lab", "prep": "Fast for 12 hours. Drink only water."}
    ],
}

def recognize_intent(message):
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['appointment', 'upcoming', 'schedule', 'when', 'show me']):
        return 'view_appointments'
    elif any(word in message_lower for word in ['prep', 'prepare', 'fast', 'bring', 'instructions']):
        return 'prep_instructions'
    elif any(word in message_lower for word in ['direction', 'location', 'where', 'address', 'map']):
        return 'directions'
    elif any(word in message_lower for word in ['confirm', 'yes', 'attend']):
        return 'confirm'
    elif any(word in message_lower for word in ['help', 'what can you do']):
        return 'help'
    elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return 'greeting'
    else:
        return 'general'

# ============================================================
# NEW ENDPOINTS FOR LOGIN AND DYNAMIC PATIENT SUPPORT
# ============================================================

@app.route('/api/patient/<int:patient_id>/exists', methods=['GET'])
def patient_exists(patient_id):
    """Check if patient exists and return basic info"""
    # Check in existing data
    if patient_id in patients_data:
        return jsonify({
            'exists': True,
            'patient_id': patient_id,
            'name': patients_data[patient_id].get('name', f"Patient_{patient_id}")
        })
    else:
        # For dynamic patients, always return True
        # This allows ANY patient ID to work!
        return jsonify({
            'exists': True,
            'patient_id': patient_id,
            'name': f"Patient_{patient_id}"
        })

@app.route('/api/patient/<int:patient_id>/info', methods=['GET'])
def get_patient_info_dynamic(patient_id):
    """Get detailed patient info (works for any ID)"""
    
    # Check if patient exists in static data
    if patient_id in patients_data:
        patient = patients_data[patient_id]
        appointments_list = appointments.get(patient_id, [])
        return jsonify({
            'patient_id': patient_id,
            'name': patient.get('name', f"Patient_{patient_id}"),
            'age': patient.get('age', 'Unknown'),
            'gender': patient.get('gender', 'Unknown'),
            'appointment_count': len(appointments_list),
            'conditions': patient.get('conditions', [])
        })
    else:
        # Generate dynamic data for any patient ID
        # This allows ANY patient ID to work!
        return jsonify({
            'patient_id': patient_id,
            'name': f"Patient_{patient_id}",
            'age': (patient_id % 80) + 18,  # Age between 18-98
            'gender': 'Male' if patient_id % 2 == 0 else 'Female',
            'appointment_count': (patient_id % 5) + 1,  # 1-5 appointments
            'conditions': []
        })

# ============================================================
# EXISTING ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Chatbot API is running!"})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    patient_id = data.get('patient_id')
    message = data.get('message', '')
    
    intent = recognize_intent(message)
    
    if intent == 'view_appointments':
        patient_appointments = appointments.get(patient_id, [])
        if not patient_appointments:
            response = "You have no upcoming appointments scheduled."
        else:
            response = "📅 **Your Upcoming Appointments:**\n\n"
            for apt in patient_appointments:
                response += f"• {apt['type']} on {apt['date']} at {apt['time']}\n"
                response += f"  👨‍⚕️ {apt['provider']}\n"
                response += f"  📍 {apt['location']}\n\n"
            response += "Would you like preparation instructions?"
    
    elif intent == 'prep_instructions':
        patient_appointments = appointments.get(patient_id, [])
        if not patient_appointments:
            response = "You have no upcoming appointments to prepare for."
        else:
            next_apt = patient_appointments[0]
            response = f"📋 **Preparation for your {next_apt['type']}:**\n\n"
            response += f"📅 Date: {next_apt['date']} at {next_apt['time']}\n"
            response += f"📍 Location: {next_apt['location']}\n\n"
            response += f"**What to do:**\n{next_apt['prep']}\n\n"
            response += "Do you need directions to the clinic?"
    
    elif intent == 'directions':
        response = "📍 **Directions to Main Hospital:**\n\n"
        response += "**Address:**\n123 Medical Center Drive\n\n"
        response += "**Parking:**\n• Garage B (Level 3) - Free for patients\n"
        response += "**Public Transit:**\n• Bus #42 to 'Medical Center' stop\n\n"
        response += "Would you like me to send these to your phone?"
    
    elif intent == 'confirm':
        response = "✅ Great! I've confirmed your appointment. You'll receive a reminder 3 days before."
    
    elif intent == 'help':
        response = """🤖 **I can help you with:**\n\n
📅 **View Appointments** - See your upcoming schedule\n
📋 **Prep Instructions** - What to bring/how to prepare\n
📍 **Directions** - How to get to the hospital\n
✅ **Confirm** - Confirm your attendance\n
🔄 **Reschedule** - Change appointment date/time\n
❌ **Cancel** - Cancel an appointment\n\n
What would you like to do?"""
    
    elif intent == 'greeting':
        # Check both static and dynamic
        if patient_id in patients_data:
            name = patients_data[patient_id].get('name', 'there')
        else:
            name = f"Patient {patient_id}"
        response = f"Hello {name}! 👋 I'm your healthcare assistant. I can help you with appointments, preparation instructions, and directions. How can I help you today?"
    
    else:
        response = "I understand you need help with healthcare. Could you please specify if you need:\n\n• To view appointments\n• Preparation instructions\n• Directions to the hospital\n• Help with something else?\n\nJust type 'help' to see all options."
    
    return jsonify({
        'response': response,
        'intent': intent,
        'patient_id': patient_id
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)