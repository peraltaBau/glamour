// Actualizar contador del carrito
function updateCartCount() {
    fetch('/api/cart_count')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cart-count').textContent = data.count;
        })
        .catch(error => console.error('Error:', error));
}

// Agregar producto al carrito
function addToCart(productId, cantidad = 1) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('cantidad', cantidad);

    fetch('/add_to_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            showAlert(data.message, 'success');
        } else {
            showAlert(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al agregar al carrito', 'danger');
    });
}

// Actualizar cantidad en el carrito
function updateCartItem(productId, cantidad) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('cantidad', cantidad);

    fetch('/update_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            location.reload(); // Recargar para actualizar totales
        } else {
            showAlert(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al actualizar carrito', 'danger');
    });
}

// Eliminar producto del carrito
function removeFromCart(productId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
        return;
    }

    const formData = new FormData();
    formData.append('product_id', productId);

    fetch('/remove_from_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            showAlert(data.message, 'success');
            // Eliminar la fila del DOM
            document.getElementById(`cart-item-${productId}`).remove();
            // Recargar si el carrito queda vacío
            if (data.cart_count === 0) {
                location.reload();
            } else {
                // Recalcular totales
                location.reload();
            }
        } else {
            showAlert(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al eliminar del carrito', 'danger');
    });
}

// Mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

// Incrementar cantidad
function incrementQuantity(inputId) {
    const input = document.getElementById(inputId);
    input.value = parseInt(input.value) + 1;
}

// Decrementar cantidad
function decrementQuantity(inputId) {
    const input = document.getElementById(inputId);
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    
    // Manejar formularios de cantidad
    document.querySelectorAll('.quantity-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const productId = this.querySelector('input[name="product_id"]').value;
            const cantidad = this.querySelector('input[name="cantidad"]').value;
            addToCart(productId, parseInt(cantidad));
        });
    });
});
