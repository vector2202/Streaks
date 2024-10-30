      document.addEventListener('DOMContentLoaded', function() {
          var notificacionesDropdown = document.getElementById('notificacionesDropdown');
          if (notificacionesDropdown) {
              notificacionesDropdown.addEventListener('show.bs.dropdown', function () {
                  // Realizar la solicitud AJAX para marcar las notificaciones como leídas
                  fetch("{% url 'marcar_notificaciones_leidas' %}", {
                      method: 'POST',
                      headers: {
                          'X-CSRFToken': '{{ csrf_token }}',  // Incluir el CSRF token si es necesario
                          'Content-Type': 'application/json'
                      },
                      credentials: 'same-origin'
                  })
                  .then(response => {
                      if (!response.ok) {
                          throw new Error('Error en la respuesta del servidor');
                      }
                      return response.json();  // Esperar la respuesta como JSON
                  })
                  .then(data => {
                      if (data.status === 'ok') {
                          console.log('Notificaciones marcadas como leídas.');
                      } else {
                          console.error('Error en la respuesta:', data.message);
                      }
                  })
                  .catch(error => console.error('Error en la solicitud AJAX:', error));
              });
          }
      });
      
   