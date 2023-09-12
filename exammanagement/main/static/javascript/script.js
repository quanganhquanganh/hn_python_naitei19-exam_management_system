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
});
