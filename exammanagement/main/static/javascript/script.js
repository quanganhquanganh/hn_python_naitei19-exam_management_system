jQuery(document).ready(function ($) {
  $("#sidebarToggle").on("click", function (event) {
    event.preventDefault();
    $("body").toggleClass("sb-sidenav-toggled");
  });
  $(".close").on("click", function (event) {
    event.preventDefault();
    $(".message-toast").remove();
  });
});
