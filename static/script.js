function uploadImage() {
    // Create a new FormData object to store the image data
    var formData = new FormData();
    
    // Get the file input element
    var fileInput = document.getElementById('imageFile');
    
    // Get the selected file
    var file = fileInput.files[0];
    
    // Append the selected file to the FormData object
    formData.append('imageFile', file);


    // Display the selected image
    var imageContainer = document.getElementById('imageContainer');
    var img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    imageContainer.innerHTML = ''; // Clear previous image
    imageContainer.appendChild(img);

    fetch('/image_text_recognition', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Handle response data
        // Display the text beside the image
        var outputContainer = document.getElementById('outputContainer');
        var text = data.text.replace(/\n/g, '<br>'); // Replace newline characters with HTML line breaks
        outputContainer.innerHTML = '<p>' + text + '</p>';

        // Display the confidence values
        var confidenceContainer = document.getElementById('confidenceContainer');
        confidenceContainer.innerHTML = '<p>Average Block Confidence: ' + data.avg_block_confidence + '%</p>' +
                                          '<p>Average Paragraph Confidence: ' + data.avg_paragraph_confidence + '%</p>';


        // Display the rating
        var ratingContainer = document.getElementById('ratingContainer');
        //ratingContainer.innerHTML = '<li>' + data.rating + '</li>';

        var ratingHTML = '<ul>'; // Opening <ul> tag
        if (data.rating && data.rating.length > 0) {
            for (let i = 0; i < data.rating.length; i++) {
                ratingHTML += '<li>' + data.rating[i] + '</li>';
            } 
        } else {
            ratingHTML += '<li>None</li>';
        }
        ratingHTML += '</ul>';
        ratingContainer.innerHTML = ratingHTML;



        // Display the keywords
        var keywordsContainer = document.getElementById('keywordsContainer');
        var keywordsHTML = '<ul>'; // Opening <ul> tag
        if (data.keywords && data.keywords.length > 0) {
            for (let i = 0; i < data.keywords.length; i++) {
                keywordsHTML += '<li>' + data.keywords[i] + '</li>';
            } 
        } else {
            keywordsHTML += '<li>None</li>';
        }
        keywordsHTML += '</ul>';
        keywordsContainer.innerHTML = keywordsHTML;

        // Display the link
        var searchContainer = document.getElementById('searchContainer');
        searchContainer.innerHTML = '<p>Search Links: ' + data.search.join(', ') + '</p>';

    })
    .catch(error => console.error('Error:', error));
}