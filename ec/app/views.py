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

class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        
        # Verificar si hay elementos en el carrito
        if not cart_items.exists():
            messages.warning(request, "No tienes productos en el carrito")
            return redirect("showcart")
        
        # Verificar si hay direcciones registradas
        if not add.exists():
            messages.warning(request, "Por favor agrega una dirección antes de continuar")
            return redirect("profile")
        
        # Calcular montos
        amount = 0
        for p in cart_items:
            value = p.quantity * p.products.discounted_price
            amount = amount + value
        totalamount = amount + 4000.0
        
        context = {
            'add': add,
            'cart_items': cart_items,
            'amount': amount,
            'totalamount': totalamount
        }
        
        return render(request, 'app/checkout.html', context)
    
    def post(self, request):
        customer_id = request.POST.get('custid')
        
        if not customer_id:
            messages.warning(request, "Por favor selecciona una dirección de envío")
            return redirect('checkout')
            
        # Verificar que el cliente existe
        try:
            customer = Customer.objects.get(id=customer_id, user=request.user)
        except Customer.DoesNotExist:
            messages.warning(request, "Dirección de envío no encontrada")
            return redirect('checkout')
        
        # Redirigir a la página de pago
        return redirect(f"/payment/?customer_id={customer_id}")



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

def search_products(request):
    query = request.GET.get('search', '')
    if query:
        # Buscar productos que coincidan con el título o la descripción
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = []
    
    return render(request, 'app/search_results.html', {
        'products': products,
        'query': query
    })



