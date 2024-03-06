from django.http import JsonResponse
from django.shortcuts import render
from Quickmart.form import customuserform
from . models import *
from django.contrib import messages
from django.shortcuts import redirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
import json


def home(request):
    products=product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})

def fav_view_page(request):
    if request.user.is_authenticated:
        fav_item=favourite.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"fav":fav_item})
    else:
        return redirect("/login")

def remove_fav(request,fid):
    item=favourite.objects.get(id=fid)
    item.delete()
    return redirect("/fav_view_page")

def cart_page(request):
    if request.user.is_authenticated:
        user_cart=cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{'cart':user_cart})
    else:
        return redirect("/login")

def remove_cart(request,cid):
    cartitem=cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart_page")

def fav_page(request):
    if request.headers.get('x-Requested-With')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.loads(request.body)
            product_id=data.get('pid')
            product_status=product.objects.get(id=product_id)
            if product_status:
                if favourite.objects.filter(user=request.user,product_id=product_id):
                    return JsonResponse({'status':'Product Already in favourite'},status=200)
                else:
                       favourite.objects.create(user=request.user,product_id=product_id )
                       return JsonResponse({'status':'product Added to cart'},status=200)
        else:
            return JsonResponse({'status':'Login to Add favourite'},status=200)
    else:
        return JsonResponse({'status':'Invalid Access'},status=200)

def add_to_cart(request):
    if request.headers.get('x-Requested-With')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.loads(request.body)
            product_qty=data.get('product_qty')
            product_id=data.get('pid')
            product_status=product.objects.get(id=product_id)
            if product_status:
                if cart.objects.filter(user=request.user,product_id=product_id):
                    return JsonResponse({'status':'Product Already in cart'},status=200)
                else:
                    if  product_status.quantity >= product_qty:
                       cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                       return JsonResponse({'status':'product Added to cart'},status=200)
                    else:
                        return JsonResponse({'status':'product stock not Available'},status=200)
        else:
            return JsonResponse({'status':'Login to Add cart'},status=200)
    else:
        return JsonResponse({'status':'Invalid Access'},status=200)
        

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=="POST":
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect('/')
            else:
                messages.error(request,"Invalid User Name or Password")
                return redirect('/login')
        return render(request,"shop/login.html")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged Out Successfully")
        return redirect('/')

def register(request):
    form=customuserform()
    if request.method=='POST':
        form=customuserform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You Can Login Now..!")
            return redirect('/login')
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    category=catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"category":category})

def collectionsview(request,name):
    if(catagory.objects.filter(name=name,status=0)):
        products=product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products,"category":name})
    else:
        messages.warning(request,"No Such Catagory Found")
        return redirect('collections')

def product_details(request,cname,pname):
    if (catagory.objects.filter(name=cname,status=0)):
        if(product.objects.filter(name=pname,status=0)):
            products=product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product_details.html",{"products":products})
        else:
            messages.error(request,"No Such Product Fount")
            return redirect('collections')
    else:
        messages.error(request,"No Such Category Found")
        return redirect('collections')