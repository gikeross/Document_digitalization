import os
import io
import tempfile
from flask import Flask, request, jsonify, render_template
from rake_nltk import Rake
import pandas as pd
from googlesearch import search

# Import Vision API-related modules
from google.cloud import vision
from google.cloud.vision_v1 import types

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')  # Specify the static URL path

# Set up Google Vision API credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/giacomorossini/Desktop/IRONHACK/FINAL_project/google/VisionApi/carbide-program-416711-10b09839cb5d.json'

# Initialize Google Vision client
client = vision.ImageAnnotatorClient()

# Define route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Define endpoint for image text recognition
@app.route('/image_text_recognition', methods=['POST'])
def image_text_recognition():
    # Check if the 'imageFile' key is in the request.files object
    if 'imageFile' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Get file from request
    uploaded_file = request.files['imageFile']
    
    # Save the file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        uploaded_file.save(temp_file.name)
        file_path = temp_file.name

    # Perform text recognition
    doc_text, avg_block_confidence, avg_paragraph_confidence = recognize_text(file_path)

    if not doc_text:
        return jsonify({"error": "No text detected"}), 400
    
    # Classify keywords_list
    rating_list, keywords_list = keyword_classifier(doc_text)

    # getting the link from keywords
    all_results = search_results(keywords_list)
    
    # Perform additional processing
    matching_result = matching_index(file_path)
    
    # Return the extracted text and additional results
    return jsonify({
        "text": doc_text,
        "matching_result": matching_result,
        "avg_block_confidence": round(avg_block_confidence * 100,2),
        "avg_paragraph_confidence": round(avg_paragraph_confidence * 100,2),
        "rating": rating_list,
        "keywords":keywords_list,
        "search":all_results
    })

# Function to perform image text recognition
def recognize_text(file_path):
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()
    
    image = types.Image(content=content)
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    request = vision.AnnotateImageRequest(image=image, features=[feature])
    response = client.annotate_image(request=request)
    
    if response.error.message:
        return None, None, None
    else:
        total_block_confidence = 0
        total_paragraph_confidence = 0
        num_blocks = 0
        num_paragraphs = 0
    
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            total_block_confidence += block.confidence
            num_blocks += 1
            for paragraph in block.paragraphs:
                total_paragraph_confidence += paragraph.confidence
                num_paragraphs += 1

    avg_block_confidence = total_block_confidence / num_blocks if num_blocks > 0 else 0
    avg_paragraph_confidence = total_paragraph_confidence / num_paragraphs if num_paragraphs > 0 else 0

        # Extract recognized text
    doc_text = response.text_annotations[0].description if response.text_annotations else ""

    return doc_text, avg_block_confidence, avg_paragraph_confidence

def matching_index(file_path):
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    request = vision.AnnotateImageRequest(image=image, features=[feature])
    response = client.annotate_image(request=request)

    # Print out the response for debugging
    print(response)

    # Update the code to access the correct attributes based on the response structure
    for page in response.full_text_annotation.pages:
        print("Page:")
        print(page)

    return None, None


def keyword_classifier(doc_text):
    r = Rake()
    r.extract_keywords_from_text(doc_text)
    keywords_list = []
    rating_list = []
    for rating, keywords in r.get_ranked_phrases_with_scores():
        if rating > 1:
            keywords_list.append(keywords)
            rating_list.append(round(rating,0))
    return rating_list, keywords_list

def search_results(keywords_list, num_results=1):
    all_results = []  # Initialize an empty list to store all search results
    for keyword in keywords_list:
        count = 0
        keyword_results = []  # Initialize an empty list to store results for each keyword
        for result in search(keyword, num_results=num_results):
            keyword_results.append(result)
            count += 1
            if count == num_results:
                break
        all_results.append(keyword_results)  # Append results for each keyword to the list of all results
    return all_results

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
