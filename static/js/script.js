// This script handles the live preview for the photo upload.
document.getElementById('photo').addEventListener('change', function(e) {
  const file = e.target.files[0];
  const preview = document.getElementById('photoPreview');
  
  if (!file) {
    preview.src = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = function(event) {
    preview.src = event.target.result;
  }
  reader.readAsDataURL(file);
});

// Optional: You can add client-side validation here if you want
document.getElementById('cargoEmployeeForm').addEventListener('submit', function(e){
  console.log('Form is being submitted to the server...');
  // The form will now submit normally to the Flask backend.
});