document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
  
      reader.onload = function(e) {
        const img = new Image();
        img.src = e.target.result;
  
        img.onload = function() {
          EXIF.getData(img, function() {
            const allMetaData = EXIF.getAllTags(this);
            const formattedData = JSON.stringify(allMetaData, null, 2);
            document.getElementById('output').textContent = formattedData || 'No EXIF data found.';
          });
        };
      };
  
      reader.readAsDataURL(file);
    } else {
      document.getElementById('output').textContent = 'Please select an image file.';
    }
  });
  