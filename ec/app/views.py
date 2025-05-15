from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.db.models import Count  # Import Count for aggregation
from . models import Customer, Product, Cart
from . forms import CustomerRegistrationForm, CustomerProfileForm# Import the Product model
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def home(request):
    return render(request, "app/home.html")

def about(request):
    return render(request, "app/about.html")

def contact(request):
    return render(request, "app/contact.html")

class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())

class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())
    

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Usuario registrado exitosamente!")
        else:
            messages.warning(request,"Datos Inválidos")
        return render(request, 'app/customerregistration.html',locals())


class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            
            reg = Customer(user=user,name=name,country=country,city=city,mobile=mobile,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"¡Perfil guardado exitosamente!")
        else:
            messages.warning(request,"Datos Inválidos")
        return render(request, 'app/profile.html',locals())

def address(request):
    if request.user.is_superuser:
        # Si es administrador, muestra todas las direcciones
        add = Customer.objects.all()
    else:
        # Si es un usuario normal, muestra solo sus direcciones
        add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.country = form.cleaned_data['country']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Perfil Actualizado Exitosamente")
        else:
            messages.warning(request,"Datos Inválidos")
        return redirect("address")

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    
    # Limpiar el valor del ID para quitar cualquier carácter no numérico
    if product_id:
        product_id = product_id.rstrip('/')
    
    product = Product.objects.get(id=product_id)
    
    # Verificar si el producto ya está en el carrito
    cart_item = Cart.objects.filter(user=user, products=product).first()
    
    if cart_item:
        # Si ya existe, incrementar la cantidad
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Si no existe, crear nuevo item
        Cart(user=user, products=product).save()
    
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.products.discounted_price
        amount = amount + value
    totalamount = amount + 4000.0 #4000.0 para gastos de envio
    return render(request, 'app/addtocart.html', locals())

# app/views.py
class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.products.discounted_price
            famount = famount + value
        totalamount = famount + 4000.0
        return render(request, 'app/checkout.html', locals())
    
    def post(self, request):
        custid = request.POST.get('custid')
        if not custid:
            messages.warning(request, "Por favor selecciona una dirección de envío")
            return redirect('checkout')
        
        # Aquí puedes guardar la dirección seleccionada para el pedido si es necesario
        
        # Redirigir a la página de pago
        return redirect('payment')



def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        # Usar filter().first() en lugar de get()
        c = Cart.objects.filter(Q(products=prod_id) & Q(user=request.user)).first()
        if c:
            c.quantity += 1
            c.save()
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity * p.products.discounted_price
                amount = amount + value
            totalamount = amount + 4000.0
            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'Producto no encontrado en el carrito'})
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        # Usar filter().first() en lugar de get()
        c = Cart.objects.filter(Q(products=prod_id) & Q(user=request.user)).first()
        if c:
            if c.quantity > 1:
                c.quantity -= 1
                c.save()
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity * p.products.discounted_price
                amount = amount + value
            totalamount = amount + 4000.0
            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'Producto no encontrado en el carrito'})
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        # Usar filter() en lugar de get() y eliminar todos los duplicados
        cart_items = Cart.objects.filter(Q(products=prod_id) & Q(user=request.user))
        cart_items.delete()  # Eliminar todos los elementos duplicados
        
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.products.discounted_price
            amount = amount + value
        totalamount = amount + 4000.0
        data = {
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

# Añadir a views.py

# Versión mejorada para añadir a views.py
from django.db.models import Q
from .search_utils import get_query_suggestions, find_similar_terms

def search(request):
    query = request.GET.get('q', '')
    
    if not query:
        products = Product.objects.none()
        return render(request, "app/search_results.html", {'query': query, 'products': products})
    
    # Mapeo de términos comunes en lenguaje natural a categorías
    natural_language_mapping = {
        # Medicamentos
        'dolor': 'MD',
        'cabeza': 'MD',
        'fiebre': 'MD',
        'gripe': 'MD',
        'tos': 'MD',
        'resfriado': 'MD',
        'alergia': 'MD',
        'pastilla': 'MD',
        'medicina': 'MD',
        'medicamento': 'MD',
        'farmaco': 'MD',
        'ibuprofeno': 'MD',
        'paracetamol': 'MD',
        'aspirina': 'MD',
        'analgesico': 'MD',
        'antibiotico': 'MD',
        'antigripal': 'MD',
        'jarabe': 'MD',
        'gotas': 'MD',
        'pomada': 'MD',
        
        # Condones
        'condon': 'CN',
        'preservativo': 'CN',
        'proteccion': 'CN',
        'sexual': 'CN',
        'latex': 'CN',
        
        # Vitaminas y suplementos
        'vitamina': 'VS',
        'suplemento': 'VS',
        'energia': 'VS',
        'proteina': 'VS',
        'calcio': 'VS',
        'hierro': 'VS',
        'fortaleza': 'VS',
        'inmunidad': 'VS',
        'omega': 'VS',
        'magnesio': 'VS',
        'zinc': 'VS',
        'colageno': 'VS',
        'multivitaminico': 'VS',
        
        # Cuidado personal
        'jabon': 'CP',
        'shampoo': 'CP',
        'champu': 'CP',
        'desodorante': 'CP',
        'pasta': 'CP',
        'dientes': 'CP',
        'cepillo': 'CP',
        'higiene': 'CP',
        'personal': 'CP',
        'crema': 'CP',
        'locion': 'CP',
        'corporal': 'CP',
        'facial': 'CP',
        'acne': 'CP',
        'hidratante': 'CP',
        'humectante': 'CP',
        'protector': 'CP',
        'solar': 'CP',
        'afeitadora': 'CP',
        'maquina': 'CP',
        'afeitar': 'CP',
        
        # Para bebés
        'bebe': 'PB',
        'baby': 'PB',
        'niño': 'PB',
        'niña': 'PB',
        'pañal': 'PB',
        'leche': 'PB',
        'formula': 'PB',
        'infantil': 'PB',
        'toallitas': 'PB',
        'papilla': 'PB',
        'talco': 'PB',
        'chupete': 'PB',
        'tetero': 'PB',
        'biberon': 'PB',
        
        # Cosméticos
        'maquillaje': 'CM',
        'labial': 'CM',
        'cosmetico': 'CM',
        'cara': 'CM',
        'uñas': 'CM',
        'belleza': 'CM',
        'rubor': 'CM',
        'sombra': 'CM',
        'rimel': 'CM',
        'mascara': 'CM',
        'pestañas': 'CM',
        'lapiz': 'CM',
        'delineador': 'CM',
        'base': 'CM',
        'polvo': 'CM',
        'corrector': 'CM',
        'esmalte': 'CM',
        
        # Snacks
        'snack': 'SN',
        'galleta': 'SN',
        'chocolate': 'SN',
        'botana': 'SN',
        'dulce': 'SN',
        'comida': 'SN',
        'barra': 'SN',
        'cereal': 'SN',
        'energia': 'SN',
        'chicle': 'SN',
        'caramelo': 'SN',
    }
    
    # Situaciones comunes y síntomas relacionados con categorías
    symptoms_mapping = {
        'dolor de cabeza': 'MD',
        'no puedo dormir': 'MD',
        'me duele': 'MD',
        'tengo fiebre': 'MD',
        'gripe': 'MD',
        'estoy con gripe': 'MD',
        'tos': 'MD',
        'estoy resfriado': 'MD',
        'alergia': 'MD',
        'estomago': 'MD',
        'dolor de estomago': 'MD',
        'nauseas': 'MD',
        'acidez': 'MD',
        'diarrea': 'MD',
        'estreñimiento': 'MD',
        'infeccion': 'MD',
        'picazon': 'MD',
        'comezon': 'MD',
        'dolor muscular': 'MD',
        'dolor de espalda': 'MD',
        'inflamacion': 'MD',
        'cansancio': 'VS',
        'fatiga': 'VS',
        'necesito energia': 'VS',
        'vitaminas': 'VS',
        'suplementos': 'VS',
        'reforzar defensas': 'VS',
        'inmunidad': 'VS',
        'huesos': 'VS',
        'piel seca': 'CP',
        'acne': 'CP',
        'proteccion solar': 'CP',
        'cuidado del bebe': 'PB',
        'productos para bebe': 'PB',
        'proteccion sexual': 'CN',
        'anticonceptivo': 'CN',
    }
    
    # Normalizar la consulta
    query_lower = query.lower()
    
    # Verificar si hay términos incorrectos y corregirlos
    corrected_query = query_lower
    query_terms = query_lower.split()
    for i, term in enumerate(query_terms):
        similar_term = find_similar_terms(term, natural_language_mapping)
        if similar_term and similar_term != term:
            query_terms[i] = similar_term
    
    corrected_query = ' '.join(query_terms)
    
    # Buscar coincidencias en situaciones comunes primero
    categories_to_search = set()
    for symptom, category in symptoms_mapping.items():
        if symptom in query_lower or symptom in corrected_query:
            categories_to_search.add(category)
    
    # Si no encuentra situaciones, buscar palabras individuales
    if not categories_to_search:
        for word in corrected_query.split():
            if word in natural_language_mapping:
                categories_to_search.add(natural_language_mapping[word])
    
    # Si aún no hay categorías, intentar buscar con palabras originales
    if not categories_to_search:
        for word in query_lower.split():
            if word in natural_language_mapping:
                categories_to_search.add(natural_language_mapping[word])
    
    # Crear filtros para búsqueda
    title_filter = Q(title__icontains=query)
    desc_filter = Q(description__icontains=query)
    
    # Si hay categorías identificadas, añadir a los filtros
    category_filter = Q(pk__lt=0)  # Iniciar con un filtro que no retorne nada
    if categories_to_search:
        category_filter = Q(category__in=categories_to_search)
    
    # Buscar productos con todos los filtros
    products = Product.objects.filter(title_filter | desc_filter | category_filter).distinct()
    
    # Si no hay resultados con la búsqueda original, intentar con la consulta corregida
    if not products.exists() and corrected_query != query_lower:
        title_filter = Q(title__icontains=corrected_query)
        desc_filter = Q(description__icontains=corrected_query)
        products = Product.objects.filter(title_filter | desc_filter | category_filter).distinct()
    
    # Generar sugerencias de búsqueda
    suggestions = []
    if not products.exists():
        all_terms = {**natural_language_mapping, **{k: v for k, v in symptoms_mapping.items()}}
        suggestions = get_query_suggestions(query_lower, all_terms)
    
    # Verificar si hubo corrección de la consulta
    did_you_mean = None
    if corrected_query != query_lower and products.exists():
        did_you_mean = corrected_query
    
    return render(request, "app/search_results.html", {
        'query': query,
        'products': products,
        'suggestions': suggestions,
        'did_you_mean': did_you_mean,
    })



#-------------------------------------------------------------------------------------------------------



# app/views.py
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views import View
from .models import Payment, OrderPlaced, Customer, Cart
import uuid
import json
import requests

class PaymentView(View):
    def get(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            messages.warning(request, "No tienes productos en tu carrito")
            return redirect("showcart")
        
        # Calcular el monto total
        amount = 0
        for item in cart_items:
            amount += item.quantity * item.products.discounted_price
        
        # Añadir costo de envío
        total_amount = amount + 4000.0
        
        # Limitar el monto para respetar los límites de ePayco
        # Suponiendo que el límite es 150000 COP (ajusta este valor según tu cuenta)
        if total_amount > 150000:
            messages.warning(request, "El monto máximo permitido es 150,000 COP. Se ha ajustado el monto.")
            total_amount = 150000
        
        # Crear referencia única para el pago
        reference = f"pago-{uuid.uuid4().hex[:8]}"
        
        # Guardar el pago en la base de datos
        payment = Payment.objects.create(
            user=user,
            amount=total_amount,
            epayco_ref_code=reference
        )
        
        # Obtener datos del cliente
        try:
            customer = Customer.objects.get(user=user)
            customer_name = customer.name
            customer_email = user.email
            customer_phone = str(customer.mobile)
            customer_address = f"{customer.country}, {customer.city}"
        except Customer.DoesNotExist:
            messages.warning(request, "Por favor completa tu perfil antes de realizar un pago")
            return redirect("profile")
        
        # Contexto para la plantilla
        context = {
            'payment': payment,
            'amount': int(total_amount),  # ePayco requiere el monto en enteros
            'reference': reference,
            'description': f"Compra en PharmaPlus - {user.username}",
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'epayco_key': settings.EPAYCO_PUBLIC_KEY,
            'epayco_test': 'true' if settings.EPAYCO_TEST else 'false',
        }
        
        return render(request, 'app/payment.html', context)

@csrf_exempt
def payment_response(request):
    """Vista para manejar la respuesta del usuario desde ePayco"""
    if request.method == 'GET':
        # ePayco envía ref_payco en la URL
        ref_payco = request.GET.get('ref_payco', '')
        
        if not ref_payco:
            messages.error(request, "No se recibió referencia de pago")
            return redirect('home')
        
        try:
            # Primero, consultar el estado actual del pago en ePayco
            # Esto es opcional pero recomendado para tener el estado más actual
            api_url = f"https://secure.epayco.co/validation/v1/reference/{ref_payco}"
            response = requests.get(api_url)
            data = response.json()
            
            if 'success' in data and data['success']:
                payment_info = data['data']
                # Esta es la referencia de tu sistema, no la de ePayco
                ref_code = payment_info.get('x_id_invoice')
                status = payment_info.get('x_response')
                
                # Buscar el pago en tu sistema usando tu referencia
                payment = Payment.objects.get(epayco_ref_code=ref_code)
                
                # Actualizar el estado del pago si es necesario
                payment.epayco_status = status
                payment.epayco_transaction_id = ref_payco
                payment.save()
                
                context = {
                    'payment': payment,
                    'ref_code': ref_code,
                    'status': status,
                    'amount': payment.amount
                }
                
                return render(request, 'app/payment_response.html', context)
            else:
                messages.error(request, "Error al verificar el pago")
                return redirect('home')
                
        except Payment.DoesNotExist:
            messages.error(request, "No se encontró el pago en nuestro sistema")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('home')

@csrf_exempt
@require_POST
def payment_confirmation(request):
    """
    Vista para manejar la confirmación de pago desde ePayco.
    Esta es la URL a la que ePayco enviará la confirmación de pago.
    """
    data = request.POST.dict()
    
    # Validar la autenticidad de la confirmación
    # Aquí normalmente se verifica la firma usando la clave privada
    
    ref_payco = data.get('x_ref_payco')
    transaction_id = data.get('x_transaction_id')
    status = data.get('x_transaction_state')
    
    try:
        payment = Payment.objects.get(epayco_ref_code=ref_payco)
        payment.epayco_transaction_id = transaction_id
        payment.epayco_status = status
        
        if status == 'Aceptada':
            payment.paid = True
            
            # Procesar el pedido
            user = payment.user
            cart_items = Cart.objects.filter(user=user)
            
            try:
                customer = Customer.objects.get(user=user)
                
                # Crear pedidos para cada item del carrito
                for item in cart_items:
                    OrderPlaced.objects.create(
                        user=user,
                        customer=customer,
                        product=item.products,
                        quantity=item.quantity,
                        payment=payment
                    )
                
                # Limpiar el carrito
                cart_items.delete()
                
            except Customer.DoesNotExist:
                # Manejar el caso donde no existe el cliente
                pass
        
        payment.save()
        return HttpResponse("Confirmación recibida", status=200)
    
    except Payment.DoesNotExist:
        return HttpResponse("Pago no encontrado", status=404)

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views import View
from django.db.models import Q, Count
from .models import Customer, Product, Cart, Payment, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
import uuid
import json

