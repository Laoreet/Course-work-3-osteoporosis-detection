$(document).ready(function () {
    // Init
    $('.image-section').hide()
    $('.loader').hide()
    $('#result').hide()

    const img = document.getElementById('test_img');
  
    // Upload Preview
    function readURL(input) {
      }
      $('#imageUpload').change(function () {
        $('.image-section').show()
        $('#btn-predict').show()
        $('#result').text('')
        $('#result').hide()
        $('#img_axial').attr('src', '')
        $('#img_sagital').attr('src', '')
        $('#img_sag_map').attr('src', '')
        readURL(this)
      })
  
    // Predict
    $('#btn-predict').click(function () {
      var form_data = new FormData($('#upload-file')[0])
  
      // Show loading animation
      $(this).hide()
      $('.loader').show()
  
      // Make prediction by calling api /predict
      $.ajax({
        type: 'POST',
        url: '/predict',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: true,
        
        success: function (data) {
            console.log(data[1])
          // Get and display the result
          $('.loader').hide()
          $('#result').fadeIn(600)
          $('#result').text(data[0][0])
          $('#img_axial').attr({'src' : data[1][0],
                                "style" : ""})
          $('#img_sagital').attr({'src' : data[1][1],
                                "style" : ""})
          $('#img_sag_map').attr({'src' : data[0][1],
                                "style" : ""})
          console.log('Success!')
        },
      })
    })
  })