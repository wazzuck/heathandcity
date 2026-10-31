var maxFileSize = 10;
var maxFileCount = 5;
var currentFileCount = 0;
var nextFileCount = [];
var validImageTypes = [
  'image/jpeg',
  'image/png',
  'application/pdf',
  'application/msword',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/octet-stream',
];

if (window.$ == undefined) window.$ = jQuery;

// Hide emergency wrapper
if (
  window.location.pathname == '/practice_response/' ||
  window.location.pathname == 'practice_response/' ||
  window.location.pathname == 'practice_response' ||
  window.location.pathname == '/practice_response'
) {
  var emergency = document.getElementById('emergency-popup-wrapper');

  if (emergency) {
    emergency.style.display = 'none';
  }
}

function patientFileChanged(element) {
  if ($(element)[0].files.length == 1) {
    var fileSizeExceded = false;
    var file = $(element)[0].files[0];
    var fileSize = file.size / 1024 / 1024;
    fileSize = fileSize.toFixed(2);

    if (fileSize >= maxFileSize) {
      fileSizeExceded = true;
    }

    var fileType = file.type;
    if ($.inArray(fileType, validImageTypes) < 0) {
      alert("You can only upload images, word documents and PDF's");

      $(element).val('');
      return;
    }

    var itemCount = $(element).attr('next-file');

    if (fileSizeExceded) {
      alert('The maximum allowed file size is 10MB.');
      $(element).val('');
      return;
    }

    setThumbnail(element, $('#patient_file_selector_' + itemCount + ' img'));

    if (currentFileCount > 0) {
      $('#add-file-button').html('Attach another file');
    }

    if (currentFileCount == 5) {
      $('#add-file-button').html('Maximum file limit of 5 reached');
    }

    if ($.inArray(fileType, ['image/jpeg', 'image/png']) < 0 || fileType.length == 0) {
      $('#patient_file_selector_' + itemCount).append(
        "<p class='file-preview-name'>" + file.name + '</p>'
      );
    }

    $('#patient_file_selector_' + itemCount).append(
      "<button class='remove-file' onclick='removeSelectedFile(" +
        itemCount +
        ")'>Remove</button>"
    );
  }
}

function addPatientFile(e) {
  e.preventDefault();

  if (currentFileCount < 5) {
    var count = currentFileCount;

    if (nextFileCount.length > 0) {
      count = nextFileCount[Math.floor(Math.random() * nextFileCount.length)];
    }

    if (nextFileCount.length > 0) {
      nextFileCount.splice(nextFileCount.indexOf(count), 1);
    }

    var nextFile = getNextAvaliablefile();
    $('#patient_files').append(
      "<div class='file-selection-item' id='patient_file_selector_" +
        nextFile +
        "'><img src='' class='file-upload-preview' /><input next-file='" +
        nextFile +
        "' onchange='patientFileChanged(this)' accept='.png,.PNG,.jpg,.jpeg,.JPG,.JPEG,.pdf,.msword,.doc,.docx,.xl,.xlsx' type='file' name='patient_file_" +
        nextFile +
        "' id='patient_file_" +
        nextFile +
        "' class='patient-file' /> </div>"
    );

    $('#patient_file_' + nextFile).click();

    if (currentFileCount == 5) {
      $('#add-file-button').html('You have reached the maximum of five attachments');
      $('#add-file-button').attr('disabled', true);
    }

    if (currentFileCount > 0) {
      $('#add-file-button').html('Attach another file');
    }

    currentFileCount = currentFileCount + 1;
  }
}

function removeSelectedFile(fileId) {
  $('#patient_file_selector_' + fileId).remove();
  nextFileCount.push(fileId);
  currentFileCount = currentFileCount - 1;

  if (currentFileCount == 0) {
    $('#add-file-button').html('Attach file');
  }

  if (currentFileCount < 5 && currentFileCount > 0) {
    $('#add-file-button').html('Attach another file');
    $('#add-file-button').attr('disabled', false);
  }
}

function setThumbnail(input, location) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function (e) {
      $(location).attr('src', e.target.result);
    };

    if (
      input.files[0].type.length == 0 ||
      input.files[0].type == 'application/pdf' ||
      input.files[0].type == 'application/msword' ||
      input.files[0].type ==
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      input.files[0].type ==
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ) {
      $(location).attr('src', '/wp-content/plugins/spForms/images/file.png');
    } else {
      reader.readAsDataURL(input.files[0]);
    }
  }
}

function getNextAvaliablefile() {
  for (var i = 0; i <= 4; i++) {
    if ($('#patient_file_selector_' + i).length == 0) {
      return i;
    }

    if ($('#patient_file_' + i) && $('#patient_file_' + i).get(0).files.length == 0) {
      removeSelectedFile(i);
      return i;
    }
  }
}

function showConcent(e) {
  e.preventDefault();
  var message =
    '<b>Warning</b>: Please do not upload intimate content e.g. images of genitalia, anus, breasts or intimate images of minors without prior communication with a clinician. If you are unsure about whether it is appropriate to upload your content, please contact the practice first.';

  jQuery('<div id="attach-photo-diaglog"></div>')
    .html(message)
    .dialog({
      dialogClass: 'no-close',
      title: 'Attach files or photos',
      modal: true,
      width: '400px',
      buttons: {
        Confirm: function () {
          addPatientFile(e);
          jQuery(this).dialog('destroy').remove();
        },
        Cancel: function () {
          jQuery(this).dialog('destroy').remove();
        }
      }
    });
}

$(document).ready(function () {
  window.fileUploadInitiated = false;

  var dropzoneItemsToReplace = $('.frm_dropzone');
  $('.frm_dropzone').map(function (item) {
    window.fileUploadInitiated = true;
    $(dropzoneItemsToReplace[item]).html(
      "<div><button id='add-file-button' class='add-file' onclick='showConcent(event)'>Attach file</button> <input onclick='this.value=null;' accept='.png,.PNG,.jpg,.jpeg,.JPG,.JPEG' next-file='0' type='file' onchange='patientFileChanged(this)' id='general-file-selector' style='display:none' /></div> <div class='patient_files' id='patient_files'></div>"
    );
  });

  if (window.fileUploadInitiated == false) {
    $('#inner-content').bind('DOMNodeInserted', function (e) {
      if (window.fileUploadInitiated == false) {
        var dropzoneItemsToReplace = $('.frm_dropzone');
        if (dropzoneItemsToReplace.length > 0) {
          $('#inner-content').unbind('DOMNodeInserted');
          $('.frm_dropzone').map(function (item) {
            $(dropzoneItemsToReplace[item]).html(
              "<div><button id='add-file-button' class='add-file' onclick='showConcent(event)'>Attach file</button> <input onclick='this.value=null;' accept='.png,.PNG,.jpg,.jpeg,.JPG,.JPEG' next-file='0' type='file' onchange='patientFileChanged(this)' id='general-file-selector' style='display:none' /></div> <div class='patient_files' id='patient_files'></div>"
            );
            window.fileUploadInitiated = true;
          });
        }
      }
    });
  }
});