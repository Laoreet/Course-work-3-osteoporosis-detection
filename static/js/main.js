$(document).ready(function () {
    $('.image-section').hide()
    $('.loader').hide()
    $('#result').hide()
  
    // Загружаем стандартные значения элементов на страничке
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
  

    $('#btn-predict').click(function () {
      var form_data = new FormData($('#upload-file')[0])
  
      // Выводим анимацию обработки/загрузки данных
      $(this).hide()
      $('.loader').show()
  
      // Делаем обработку загруженных данных через переход на /predict
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
          // Обновляем данные на страничке в соответствии с результатами обработки
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