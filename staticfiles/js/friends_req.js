$(document).ready(function() {
    $.ajax({
        url: '/api/get_data/',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
          console.log(data);
        },
        error: function(error) {
          console.error('Error fetching data:', error);
        }
    });
});