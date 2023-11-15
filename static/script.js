$(document).ready(function () {
    $('#parameter_select').change(function () {
        let selectedParameter = $(this).val();

        $.ajax({
            type: 'POST',
            url: '/get_limits',
            data: {'parameter': selectedParameter},
            dataType: 'json',
            success: function (response) {

                $('#limit_select').empty();

                $('#limit_select').append($('<option>', {
                    value: '',
                    text: 'Limit',
                    disabled: false,
                    selected: true
                }));

                $.each(response.limits, function (index, limit) {
                    $('#limit_select').append($('<option>', {
                        value: limit,
                        text: limit
                    }));
                });
            },
            error: function (error) {
                console.error('Error en la petición AJAX:', error);
            }
        });
    });

    $('#createLimitForm').submit(function(event) {
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: '/create',
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response) {
                let alarmFooter = $('#alarm-footer'); 

                if (response.status === 'success') {
                    alarmFooter.html('<div class="alert alert-success messages" role="alert">' + response.message + '</div>');
                    $('#createLimitForm')[0].reset();
                } else {
                    alarmFooter.html('<div class="alert alert-danger messages" role="alert">' + response.message + '</div>');
                    $('#createLimitForm')[0].reset();
                }

                setTimeout(function() {
                    alarmFooter.html('');
                }, 3000);
            },
            error: function(error) {
                console.error('Error en la petición AJAX:', error);
            }
        });
    });

    $('#limit_select').change(function() {
        let limit_name = $(this).val();

        $.ajax({
            type: 'GET',
            url: '/limits',
            data: {'limit_name': limit_name},
            dataType: 'json',
            success: function(response) {
                if (response.status === 'success') {
                    console.log(response.message);
                } else {
                    console.error('Operación fallida:', response.message);
                }
            },
            error: function(error) {
                console.error('Error en la petición AJAX:', error);
            }
        });
    });

    $('#selected_graphs').submit(function(event) {
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: '/graph',
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response) {
                let graphBody = $('#graph-body')

                if (response.status === 'success') {
                    graphBody.html(response.plot_div)
                }
                else {
                    graphBody.html('<div class="alert alert-danger" role="alert" id="message">' + response.message + '</div>');
                    setTimeout (function() {
                        graphBody.html('');
                    }, 1000);    
                }
            },
            error: function(error) {
                console.error('Error en la petición AJAX:', error);
            }
        })
    });
});

