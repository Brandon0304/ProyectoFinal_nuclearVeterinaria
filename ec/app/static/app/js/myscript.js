$(document).ready(function() {
    // Configuración del carrusel
    $('#slider1, #slider2, #slider3').owlCarousel({
        loop: true,
        margin: 20,
        responsiveClass: true,
        responsive: {
            0: {
                items: 2,
                nav: false,
                autoplay: true,
            },
            600: {
                items: 4,
                nav: true,
                autoplay: true,
            },
            1000: {
                items: 6,
                nav: true,
                loop: true,
                autoplay: true,
            }
        }
    });

    // Funcionalidad para aumentar la cantidad en el carrito
    $('.plus-cart').click(function(){
        console.log("Botón plus-cart clickeado");
        var id = $(this).attr("pid").toString();
        console.log("ID del producto:", id);
        var eml = this.parentNode.children[2];
        $.ajax({
            type: "GET",
            url: "/pluscart/",
            data: {
                prod_id: id
            },
            success: function(data){
                console.log("Respuesta recibida:", data);
                eml.innerText = data.quantity;
                document.getElementById("amount").innerText = "Rs. " + data.amount.toFixed(2);
                document.getElementById("totalamount").innerText = "Rs. " + data.totalamount.toFixed(2);
            },
            error: function(xhr, status, error) {
                console.error("Error en la solicitud:", error);
                console.error("Detalles:", xhr.responseText);
            }
        });
    });

    // Funcionalidad para disminuir la cantidad en el carrito
    $('.minus-cart').click(function(){
        console.log("Botón minus-cart clickeado");
        var id = $(this).attr("pid").toString();
        console.log("ID del producto:", id);
        var eml = this.parentNode.children[2];
        $.ajax({
            type: "GET",
            url: "/minuscart/",
            data: {
                prod_id: id
            },
            success: function(data){
                console.log("Respuesta recibida:", data);
                eml.innerText = data.quantity;
                document.getElementById("amount").innerText = "Rs. " + data.amount.toFixed(2);
                document.getElementById("totalamount").innerText = "Rs. " + data.totalamount.toFixed(2);
            },
            error: function(xhr, status, error) {
                console.error("Error en la solicitud:", error);
                console.error("Detalles:", xhr.responseText);
            }
        });
    });

    // Funcionalidad para eliminar productos del carrito
    $('.remove-cart').click(function(){
        console.log("Botón remove-cart clickeado");
        var id = $(this).attr("pid").toString();
        console.log("ID del producto a eliminar:", id);
        var elm = this;
        $.ajax({
            type: "GET",
            url: "/removecart/",
            data: {
                prod_id: id
            },
            success: function(data){
                console.log("Respuesta recibida:", data);
                document.getElementById("amount").innerText = "Rs. " + data.amount.toFixed(2);
                document.getElementById("totalamount").innerText = "Rs. " + data.totalamount.toFixed(2);
                elm.parentNode.parentNode.parentNode.parentNode.remove();
                
                // Verificar si el carrito está vacío
                if(data.amount == 0){
                    $('.row').html('<h1 class="text-center mb-5">Cart is Empty</h1>');
                }
            },
            error: function(xhr, status, error) {
                console.error("Error en la solicitud:", error);
                console.error("Detalles:", xhr.responseText);
            }
        });
    });

    // Funcionalidad para la lista de deseos (wishlist)
    $('.plus-wishlist').click(function(){
        var id=$(this).attr("pid").toString();
        $.ajax({
            type:"GET",
            url:"/add-to-wishlist",
            data:{
                prod_id:id
            },
            success:function(data){
                if(data.status === 'success'){
                    alert('Producto añadido a favoritos');
                } else if(data.status === 'exists'){
                    alert('El producto ya está en favoritos');
                }
            }
        })
    })
    
    $('.minus-wishlist').click(function(){
        var id=$(this).attr("pid").toString();
        $.ajax({
            type:"GET",
            url:"/remove-from-wishlist",
            data:{
                prod_id:id
            },
            success:function(data){
                // Puedes manejar la eliminación de favoritos si es necesario
                window.location.href = `http://localhost:8000/product-detail/${id}`
            }
        })
    })
});