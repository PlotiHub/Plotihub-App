import os
import datetime
import json
import requests
# from plotihub import settings
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from property_management_app.EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate, login, logout, get_backends
from property_management_app.models import CustomUser, Properties, SessionYearModel


def showDemoPage(request):
    return render(request,"demo.html")

def ShowLoginPage(request):
    return render(request,"login_page.html")

def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        captcha_token = request.POST.get("g-recaptcha-response")
        cap_url = "https://www.google.com/recaptcha/api/siteverify"
        cap_secret = "6LeWtqUZAAAAANlv3se4uw5WAg-p0X61CJjHPxKT"
        cap_data = {"secret": cap_secret, "response": captcha_token}
        cap_server_response = requests.post(url=cap_url, data=cap_data)
        cap_json = json.loads(cap_server_response.text)

        if not cap_json['success']:
            messages.error(request, "Invalid Captcha Try Again")
            return HttpResponseRedirect("/")

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = EmailBackEnd().authenticate(request, username=email, password=password)
        
        if user is not None:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("staff_home"))
            else:
                return HttpResponseRedirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")
  
def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")
    
def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")   

def Testurl(request):
    return HttpResponse("Ok")

def signup_admin(request):
    return render(request,"signup_admin_page.html")

def signup_tenant(request):
    properties=Properties.objects.all()
    session_years=SessionYearModel.object.all()
    return render(request,"signup_tenant_page.html",{"Properties":properties,"session_years":session_years})

def signup_staff(request):
    return render(request,"signup_staff_page.html")

def do_admin_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=1)
        user.save()
        messages.success(request,"Successfully Created Admin")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Admin")
        return HttpResponseRedirect(reverse("show_login"))

def do_staff_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")
    address=request.POST.get("address")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=2)
        user.staffs.address=address
        user.save()
        messages.success(request,"Successfully Created Staff")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Staff")
        return HttpResponseRedirect(reverse("show_login"))

def do_signup_tenant(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")
    session_year_id = request.POST.get("session_year")
    course_id = request.POST.get("course")
    sex = request.POST.get("sex")

    profile_pic = request.FILES['profile_pic']
    fs = FileSystemStorage()
    filename = fs.save(profile_pic.name, profile_pic)
    profile_pic_url = fs.url(filename)

    #try:
    user = CustomUser.objects.create_user(username=username, password=password, email=email, last_name=last_name,
                                          first_name=first_name, user_type=3)
    user.tenants.address = address
    property_obj = Properties.objects.get(id=course_id)
    user.tenants.course_id = property_obj
    session_year = SessionYearModel.object.get(id=session_year_id)
    user.tenants.session_year_id = session_year
    user.tenants.gender = sex
    user.tenants.profile_pic = profile_pic_url
    user.save()
    messages.success(request, "Successfully Added tenant")
    return HttpResponseRedirect(reverse("show_login"))
    #except:
     #   messages.error(request, "Failed to Add tenant")
      #  return HttpResponseRedirect(reverse("show_login"))