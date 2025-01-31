from flask import Flask, request, jsonify, render_template, redirect, url_for,Response
from flask_apscheduler import APScheduler
from src.config import Config
from src.services.linkedin_service import LinkedInImageShare, share_festival_content_on_linkedin
from src.services.calendar_service import GoogleCalendarManager
from src.services.post_generator import PostGenerator
from src.services.whatsapp import WhatsAppService
from datetime import datetime, timedelta
import json
import gridfs
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, OperationFailure


# linkedin_service = LinkedInService(Config.LINKEDIN_ACCESS_TOKEN)
calendar_service = GoogleCalendarManager()
post_generator = PostGenerator(Config.MISTRAL_API_KEY)
whatsapp_service = WhatsAppService(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
whatsapp_to_number = Config.WHATSAPP_TO_NUMBER
ACCESS_TOKEN = Config.LINKEDIN_ACCESS_TOKEN
PERSON_URN = Config.LINKEDIN_PERSON_URN
BASE_URL = "http://127.0.0.1:5000"


# MongoDB Configuration
MONGO_USERNAME = "rabitmoon02"
MONGO_PASSWORD = "lxsGwBzU2AUO9icR"  # Replace with actual password
MONGO_CLUSTER = "cluster0.vrpe1.mongodb.net"
uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)
# Select database
db = client.get_database("festival_db")
# Create a GridFS instance
fs = gridfs.GridFS(db)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def init_mongodb():
    """Initialize MongoDB connection with error handling"""
    global client, db, festival_images
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        db = client['festival_db']
        festival_images = db['festival_images']
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False


# Initialize MongoDB connection
if not init_mongodb():
    print("Warning: MongoDB connection failed. Some features may not work.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_and_save_draft():
    # Get today's date and tomorrow's date
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Format dates for comparison
    today_str = today.isoformat()
    tomorrow_str = tomorrow.isoformat()
    
    # Fetch next holiday
    events = calendar_service.fetch_indian_festival()
    if not events:
        return {"status": "No upcoming festival found"}
    
    # Parse events
    result = json.loads(events)
    result = result["events"]
    result = result[0]
    date_of_event = result["start_date"]
    print(f"today: {today_str}, tomorrow: {tomorrow_str}, date_of_event: {date_of_event}")

    # If today is Monday to Friday and tomorrow is an event
    if today.weekday() in range(0, 5) and tomorrow_str == date_of_event:
        whatsapp_service.sand_message(
            whatsapp_to_number, 
            f"Tomorrow is {result['title']}. Please create a post for the same."
        )
        post_content = post_generator.generate_post(result["title"])
        response = share_festival_content_on_linkedin(
            access_token=ACCESS_TOKEN,
            person_urn=PERSON_URN,
            festival_name=result['title'],
            share_text=post_content,
            base_url=BASE_URL
        )
        
        if response.status_code == 201:
            return {"status": "success", "message": "Draft created successfully for tomorrow's festival"}
        else:
            return {"status": "error", "message": f"Failed to create draft: {response.json()}"}
    
    # If today is Friday and the event is on Sunday or Monday
    elif today.weekday() == 4 and date_of_event in [(today + timedelta(days=2)).isoformat(), (today + timedelta(days=3)).isoformat()]:
        # whatsapp_service.sand_message(
        #     whatsapp_to_number, 
        #     f"{result['title']} is coming up on {date_of_event}. Please create a post for the same."
        # )
        
        post_content = post_generator.generate_post(result["title"])
        response = share_festival_content_on_linkedin(
            access_token=ACCESS_TOKEN,
            person_urn=PERSON_URN,
            festival_name=result['title'],
            share_text=post_content,
            base_url=BASE_URL
        )
        print(response)
        
        if response.status_code == 201:
            return {"status": "success", "message": "Draft created successfully for the weekend festival"}
        else:
            return {"status": "error", "message": f"Failed to create draft: {response.json()}"}
    
    # Default case - No action needed
    else:
        return {"status": "No action needed today"}
    

@app.route('/generate-post', methods=['GET'])
def manual_generate():
    result = generate_and_save_draft()
    return jsonify(result)

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    try:
        calendar_manager = GoogleCalendarManager()
        festivals_json = calendar_manager.fetch_indian_festival()
        festivals = json.loads(festivals_json)['events']
        
        # Filter festivals based on search query
        if search_query:
            festivals = [f for f in festivals if search_query.lower() in f['title'].lower()]
        
        if festival_images is not None:
            for festival in festivals:
                try:
                    # Retrieve the image record from GridFS
                    image_record = festival_images.find_one({'festival_name': festival['title']})
                    
                    if image_record and 'file_id' in image_record:
                        # Get the file ID from the record and retrieve the image from GridFS
                        file_id = image_record['file_id']
                        file = fs.get(file_id)
                        
                        # Assuming you're sending the image as a base64 encoded string for embedding in the HTML
                        from base64 import b64encode
                        encoded_image = b64encode(file.read()).decode('utf-8')
                        
                        # Set the image as a base64 string so it can be displayed on the webpage
                        festival['image_path'] = f"data:image/jpeg;base64,{encoded_image}"
                    else:
                        festival['image_path'] = None
                except Exception as e:
                    print(f"Error fetching image for festival {festival['title']}: {e}")
                    festival['image_path'] = None
        else:
            for festival in festivals:
                festival['image_path'] = None
        
        # Render the festivals along with their images on the page
        return render_template('index.html', festivals=festivals, search_query=search_query)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload/<festival_name>', methods=['POST'])
def upload_image(festival_name):
    if festival_images is None:
        return jsonify({'error': 'Database connection not available'}), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Get the existing image file from the database if it exists
            existing_record = festival_images.find_one({'festival_name': festival_name})
            
            # If the festival already has an image, delete it from GridFS
            if existing_record and 'file_id' in existing_record:
                fs.delete(existing_record['file_id'])
            
            # Store the new image in GridFS
            file_id = fs.put(file, filename=file.filename, festival_name=festival_name)
            
            # Save the file reference and metadata in your festival_images collection
            festival_images.update_one(
                {'festival_name': festival_name},
                {
                    '$set': {
                        'file_id': file_id,
                        'updated_at': datetime.utcnow(),
                        'filename': file.filename
                    }
                },
                upsert=True
            )
            
            return jsonify({'success': True, 'file_id': str(file_id)})
        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/image/<festival_name>', methods=['GET'])
def get_image(festival_name):
    try:
        # Get the record for the festival
        festival = festival_images.find_one({'festival_name': festival_name})
        
        if festival and 'file_id' in festival:
            file_id = festival['file_id']
            
            # Retrieve the file from GridFS
            file = fs.get(file_id)
            
            # Set the appropriate content type based on the file
            return Response(file.read(), content_type='image/jpeg')  # Adjust content type if needed
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error fetching image: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(debug=True)