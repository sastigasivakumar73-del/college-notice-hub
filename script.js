// College Notice Hub - small front-end enhancements

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss flash messages after 4 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 4000);
  });

  // Simple client-side preview of the selected file name for uploads
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(function (input) {
    input.addEventListener("change", function () {
      if (input.files && input.files.length > 0) {
        console.log("Selected file:", input.files[0].name);
      }
    });
  });
});
