function readURL(input) {
  const file = input.files[0];
  const fileError = document.getElementById("fileError");

  if (file && file.type.startsWith("image/")) {
    var reader = new FileReader();

    reader.onload = function(e) {
      document.querySelector('.image-upload-wrap').style.display = 'none';
      document.querySelector('.file-upload-image').src = e.target.result;
      document.querySelector('.file-upload-content').style.display = 'block';
      document.querySelector('.image-title').textContent = file.name;
      document.getElementById('uploadButton').style.display = 'block';
      fileError.textContent = ""; // Clear any previous error messages
    };

    reader.readAsDataURL(file);
  } else {
    removeUpload();
    fileError.textContent = "Please upload a valid image file.";
  }
}

function removeUpload() {
  var fileInput = document.querySelector('.file-upload-input');
  fileInput.value = '';
  document.querySelector('.file-upload-content').style.display = 'none';
  document.querySelector('.image-upload-wrap').style.display = 'block';
  document.getElementById('uploadButton').style.display = 'none';
}

document.querySelector('.image-upload-wrap').addEventListener('dragover', function() {
  this.classList.add('image-dropping');
});

document.querySelector('.image-upload-wrap').addEventListener('dragleave', function() {
  this.classList.remove('image-dropping');
});

function validateForm() {
  const firstname = document.getElementById("firstName").value;
  const lastname = document.getElementById("lastName").value;
  const patientAge = document.getElementById("patientAge").value;
  const firstnameError = document.getElementById("firstNameError");
  const lastnameError = document.getElementById("lastNameError");
  const ageError = document.getElementById("ageError");
  let isValid = true;

  // Regex patterns
  const nameRegex = /^[A-Za-z\s]{1,50}$/;
  const ageRegex = /^(?:1[01][0-9]|120|1[2-9]|[2-9][0-9])$/;

  if (!nameRegex.test(firstname)) {
    firstnameError.textContent = "Please enter a valid first name (letters only, max 50 characters).";
    isValid = false;
  } else {
    firstnameError.textContent = "";
  }

  if (!nameRegex.test(lastname)) {
    lastnameError.textContent = "Please enter a valid last name (letters only, max 50 characters).";
    isValid = false;
  } else {
    lastnameError.textContent = "";
  }

  if (!ageRegex.test(patientAge)) {
    ageError.textContent = "Please enter a valid age (12-120 years).";
    isValid = false;
  } else {
    ageError.textContent = "";
  }

  return isValid;
}

document.querySelector("#patientForm").addEventListener("submit", function(event) {
  if (!validateForm()) {
    event.preventDefault();
  }
});
