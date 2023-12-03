jQuery(document).ready(function ($) {
  $("#sidebarToggle").on("click", function (event) {
    event.preventDefault();
    $("body").toggleClass("sb-sidenav-toggled");
  });

  $(".close").on("click", function (event) {
    event.preventDefault();
    $(".message-toast").remove();
  });

  $("#registration-form").on("submit", function (e) {
    e.preventDefault();
    var formData = $(this).serialize();
    var registrationUrl = $(this).data("registration-url");

    $.ajax({
      url: registrationUrl,
      type: "POST",
      data: formData,
      success: function (data) {
        $("#registration-status").html(data.message);
        $("#enroll-button").prop("disabled", true);
        $("#enroll-button").text("Enrolled");
      },
      error: function () {
        $("#registration-status").html("An error occurred.");
      },
    });
  });
  const countdownElement = $("#countdown");
  let remainingTime = countdownElement.data("remaining-seconds");
  let intTime = parseInt(remainingTime);
  function submitExamAndRedirect() {
    $("#countdown").text("Countdown expired");
    // Automatically submit the exam form
    $("#exam-form").submit();
    localStorage.clear();
  }
  updateCountdown = function () {
    if (intTime > 0) {
      const minutes = Math.floor(intTime / 60);
      const seconds = intTime % 60;
      countdownElement.text(`${minutes}:${seconds < 10 ? "0" : ""}${seconds}`);
      --intTime;
      setTimeout(updateCountdown, 1000);
    } else if (intTime <= 0 && intTime != null) {
      submitExamAndRedirect();
    }
  };
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  };
  updateCountdown();
  const csrfToken = getCookie('csrftoken');

  $('input[type="radio"]').on("change", function () {
    var questionId = $(this).attr("name").replace("question_", "");
    var selectedAnswerId = $(this).val();

    localStorage.setItem("question_" + questionId, selectedAnswerId);
  });

  $('input[type="radio"]').each(function () {
    var questionId = $(this).attr("name").replace("question_", "");
    var selectedAnswerId = localStorage.getItem("question_" + questionId);
    if (selectedAnswerId === $(this).val()) {
      $(this).prop("checked", true);
    }
  });
  $("#exam-form").on("submit", function () {
    localStorage.clear();
  });
  $("#myTabs a").on("click", function (e) {
    e.preventDefault();
    $(this).tab("show");
  });
  $("#enrollTable").DataTable({
    order: [[2, "asc"]],
    ordering: true, // Enable sorting
  });
  $(".mark-as-read").on("click", function (e) {
    e.preventDefault();

    var postUrl = $(this).data("post-url");
    var notificationId = $(this).data("notification-id");
    var notificationUrl = $(this).data("notification-url");

    $.ajax({
        type: "POST",
        url: postUrl,
        data: {
            notification_id: notificationId,
            csrfmiddlewaretoken: csrfToken,
        },
        success: function (data) {
            var notificationBadge = $(".notification-badge");
            var notificationCount = parseInt(notificationBadge.text());

            notificationCount = notificationCount - 1;

            notificationBadge.text(notificationCount);

            if (notificationCount <= 0) {
                notificationBadge.hide();
                var notificationDropdown = $(".notification-dropdown");
                var noNewNotifications = $("<li><a class='dropdown-item' href='#'>No new notifications</a></li>");
                notificationDropdown.empty();
                notificationDropdown.append(noNewNotifications);
            }
            $("#notification-" + notificationId).remove();
            window.location.href = notificationUrl;
        },
        error: function (xhr, textStatus, errorThrown) {
            // Handle error (e.g., show an error message)
            console.error("Error: " + errorThrown);
        }
    });
  });
  var fileInput = $('<br><input type="file" id="file-input" accept="image/*">');
  $('#id_avatar').after(fileInput);
  $('#id_avatar').val('');
  fileInput.on('change', function() {
      var file = this.files[0];
      var reader = new FileReader();
      reader.onload = function(e) {
          $('#preview').attr('src', e.target.result);
      };
      reader.readAsDataURL(file);
  });
  var postUrl = $('#profile-form').data('post-url');

  $('#profile-form').on('submit', function(e) {
      e.preventDefault();

      // Get the file from the new file input field
      var file = $('#file-input')[0].files[0];

      // Get the presigned URL
      $.ajax({
          url: postUrl,
          type: 'POST',
          data: {
              filename: file.name,
              content_type: file.type,
              csrfmiddlewaretoken: csrfToken,
          },
          success: function(data) {
            // Put the fileType in the headers for the upload
            var headers = { 'Content-Type': file.type };
            var url = data.url;
            var getUrl = data.get_url;
            // Upload the file to S3
            $.ajax({
                url: url,
                type: 'PUT',
                headers: headers,
                data: file,
                processData: false,
                success: function(data) {
                    // Now that the file is uploaded, submit the form
                    $('#id_avatar').val(getUrl);
                    $('#profile-form').unbind('submit').submit();
                }
            });
          }
      });
  });
});
