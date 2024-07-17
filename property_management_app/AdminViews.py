import json
import requests
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from property_management_app.forms import AddTenantForm, EditTenantForm
from property_management_app.models import CustomUser, Staffs, Properties, Caretakers, Tenants, SessionYearModel, \
    FeedBackTenant, FeedBackStaffs, LeaveReportTanant, LeaveReportStaff, Arrears, ArrearsReport, \
    NotificationTenant, NotificationStaffs


def admin_home(request):
    tenant_count1 = Tenants.objects.all().count()
    staff_count = Staffs.objects.all().count()
    caretaker_count = Caretakers.objects.all().count()
    property_count = Properties.objects.all().count()

    property_all = Properties.objects.all()
    property_name_list = []
    caretaker_count_list = []
    tenant_count_list_in_property = []

    for property in property_all:
        caretaker_count = Caretakers.objects.filter(property_id=property.id).count()
        tenant_count = Tenants.objects.filter(property_id=property.id).count()
        property_name_list.append(property.property_name)
        caretaker_count_list.append(caretaker_count)
        tenant_count_list_in_property.append(tenant_count)

    Caretakers_all = Caretakers.objects.all()
    caretaker_list = []
    tenant_count_list_in_caretaker = []

    for caretaker in Caretakers_all:
        property = Properties.objects.get(id=caretaker.property_id.id)
        tenant_count = Tenants.objects.filter(property_id=property.id).count()
        caretaker_list.append(caretaker.caretaker_name)
        tenant_count_list_in_caretaker.append(tenant_count)

    staffs = Staffs.objects.all()
    arrears_present_list_staff = []
    arrears_absent_list_staff = []
    staff_name_list = []

    for staff in staffs:
        caretaker_ids = Caretakers.objects.filter(staff_id=staff.admin.id)
        arrears_count = Arrears.objects.filter(staff_id=staff.id).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        arrears_present_list_staff.append(arrears_count)
        arrears_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    Tenants_all = Tenants.objects.all()
    arrears_present_list_tenant = []
    arrears_absent_list_tenant = []
    tenant_name_list = []

    for tenant in Tenants_all:
        arrears_count = ArrearsReport.objects.filter(tenant_id=tenant.id, status=True).count()
        absent_count = ArrearsReport.objects.filter(tenant_id=tenant.id, status=False).count()
        arrears_present_list_tenant.append(arrears_count)
        arrears_absent_list_tenant.append(leaves + absent_count)
        tenant_name_list.append(tenant.admin.username)

    context = {
        "tenant_count": tenant_count1,
        "staff_count": staff_count,
        "caretaker_count": caretaker_count,
        "property_count": property_count,
        "property_name_list": property_name_list,
        "caretaker_count_list": caretaker_count_list,
        "tenant_count_list_in_property": tenant_count_list_in_property,
        "tenant_count_list_in_caretaker": tenant_count_list_in_caretaker,
        "caretaker_list": caretaker_list,
        "staff_name_list": staff_name_list,
        "arrears_present_list_staff": arrears_present_list_staff,
        "arrears_absent_list_staff": arrears_absent_list_staff,
        "tenant_name_list": tenant_name_list,
        "arrears_present_list_tenant": arrears_present_list_tenant,
        "arrears_absent_list_tenant": arrears_absent_list_tenant,
    }

    return render(request, "admin_template/home_content.html", context)

def add_staff(request):
    return render(request,"admin_template/add_staff_template.html")

def add_staff_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.staffs.address=address
            user.save()
            messages.success(request,"Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request,"Failed to Add Staff")
            return HttpResponseRedirect(reverse("add_staff"))

def add_property(request):
    return render(request,"admin_template/add_property_template.html")

def add_property_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        property=request.POST.get("property")
        try:
            property_model=Properties(property_name=property)
            property_model.save()
            messages.success(request,"Successfully Added property")
            return HttpResponseRedirect(reverse("add_property"))
        except Exception as e:
            print(e)
            messages.error(request,"Failed To Add property")
            return HttpResponseRedirect(reverse("add_property"))

def add_tenant(request):
    form=AddTenantForm()
    return render(request,"admin_template/add_tenant_template.html",{"form":form})

def add_tenant_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddTenantForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            property_id=form.cleaned_data["property"]
            sex=form.cleaned_data["sex"]

            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)

            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.Tenants.address=address
                property_obj=Properties.objects.get(id=property_id)
                user.Tenants.property_id=property_obj
                session_year=SessionYearModel.object.get(id=session_year_id)
                user.Tenants.session_year_id=session_year
                user.Tenants.gender=sex
                user.Tenants.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added Tenant")
                return HttpResponseRedirect(reverse("add_tenant"))
            except:
                messages.error(request,"Failed to Add Tenant")
                return HttpResponseRedirect(reverse("add_tenant"))
        else:
            form=AddTenantForm(request.POST)
            return render(request, "admin_template/add_tenant_template.html", {"form": form})


def add_caretaker(request):
    properties=Properties.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"admin_template/add_caretaker_template.html",{"staffs":staffs,"properties":properties})

def add_caretaker_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        caretaker_name=request.POST.get("caretaker_name")
        property_id=request.POST.get("property")
        property=Properties.objects.get(id=property_id)
        staff_id=request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)

        try:
            caretaker=Caretakers(caretaker_name=caretaker_name,property_id=property,staff_id=staff)
            caretaker.save()
            messages.success(request,"Successfully Added caretaker")
            return HttpResponseRedirect(reverse("add_caretaker"))
        except:
            messages.error(request,"Failed to Add caretaker")
            return HttpResponseRedirect(reverse("add_caretaker"))


def manage_staff(request):
    staffs=Staffs.objects.all()
    return render(request,"admin_template/manage_staff_template.html",{"staffs":staffs})

def manage_tenant(request):
    tenants=Tenants.objects.all()
    return render(request,"admin_template/manage_tenant_template.html",{"tenants":tenants})

def manage_property(request):
    properties=Properties.objects.all()
    return render(request,"admin_template/manage_property_template.html",{"properties":properties})

def manage_caretaker(request):
    caretakers=Caretakers.objects.all()
    return render(request,"admin_template/manage_caretaker_template.html",{"caretakers":caretakers})

def edit_staff(request,staff_id):
    staff=Staffs.objects.get(admin=staff_id)
    return render(request,"admin_template/edit_staff_template.html",{"staff":staff,"id":staff_id})

def edit_staff_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id=request.POST.get("staff_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")

        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()
            messages.success(request,"Successfully Edited Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))
        except:
            messages.error(request,"Failed to Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

def edit_tenant(request,tenant_id):
    request.session['tenant_id']=tenant_id
    tenant=Tenants.objects.get(admin=tenant_id)
    form=EditTenantForm()
    form.fields['email'].initial=tenant.admin.email
    form.fields['first_name'].initial=tenant.admin.first_name
    form.fields['last_name'].initial=tenant.admin.last_name
    form.fields['username'].initial=tenant.admin.username
    form.fields['address'].initial=tenant.address
    form.fields['property'].initial=tenant.property_id.id
    form.fields['sex'].initial=tenant.gender
    form.fields['session_year_id'].initial=tenant.session_year_id.id
    return render(request,"admin_template/edit_tenant_template.html",{"form":form,"id":tenant_id,"username":tenant.admin.username})

def edit_tenant_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        tenant_id=request.session.get("tenant_id")
        if tenant_id==None:
            return HttpResponseRedirect(reverse("manage_tenant"))

        form=EditTenantForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            property_id = form.cleaned_data["property"]
            sex = form.cleaned_data["sex"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None


            try:
                user=CustomUser.objects.get(id=tenant_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()

                tenant=Tenants.objects.get(admin=tenant_id)
                tenant.address=address
                session_year = SessionYearModel.object.get(id=session_year_id)
                tenant.session_year_id = session_year
                tenant.gender=sex
                property=Properties.objects.get(id=property_id)
                tenant.property_id=property
                if profile_pic_url!=None:
                    tenant.profile_pic=profile_pic_url
                tenant.save()
                del request.session['tenant_id']
                messages.success(request,"Successfully Edited Tenant")
                return HttpResponseRedirect(reverse("edit_tenant",kwargs={"tenant_id":tenant_id}))
            except:
                messages.error(request,"Failed to Edit Tenant")
                return HttpResponseRedirect(reverse("edit_tenant",kwargs={"tenant_id":tenant_id}))
        else:
            form=EditTenantForm(request.POST)
            tenant=Tenants.objects.get(admin=tenant_id)
            return render(request,"admin_template/edit_tenant_template.html",{"form":form,"id":tenant_id,"username":tenant.admin.username})

def edit_caretaker(request,caretaker_id):
    caretaker=Caretakers.objects.get(id=caretaker_id)
    properties=Properties.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"admin_template/edit_caretaker_template.html",{"caretaker":caretaker,"staffs":staffs,"properties":properties,"id":caretaker_id})

def edit_caretaker_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        caretaker_id=request.POST.get("caretaker_id")
        caretaker_name=request.POST.get("caretaker_name")
        staff_id=request.POST.get("staff")
        property_id=request.POST.get("property")

        try:
            caretaker=Caretakers.objects.get(id=caretaker_id)
            caretaker.caretaker_name=caretaker_name
            staff=CustomUser.objects.get(id=staff_id)
            caretaker.staff_id=staff
            property=Properties.objects.get(id=property_id)
            caretaker.property_id=property
            caretaker.save()

            messages.success(request,"Successfully Edited caretaker")
            return HttpResponseRedirect(reverse("edit_caretaker",kwargs={"caretaker_id":caretaker_id}))
        except:
            messages.error(request,"Failed to Edit caretaker")
            return HttpResponseRedirect(reverse("edit_caretaker",kwargs={"caretaker_id":caretaker_id}))


def edit_property(request,property_id):
    property=Properties.objects.get(id=property_id)
    return render(request,"admin_template/edit_property_template.html",{"property":property,"id":property_id})

def edit_property_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        property_id=request.POST.get("property_id")
        property_name=request.POST.get("property")

        try:
            property=Properties.objects.get(id=property_id)
            print(Properties.property_name)
            property.property_name=property_name
            property.save()
            messages.success(request,"Successfully Edited property")
            return HttpResponseRedirect(reverse("edit_property",kwargs={"property_id":property_id}))
        except:
            messages.error(request,"Failed to Edit property")
            return HttpResponseRedirect(reverse("edit_property",kwargs={"property_id":property_id}))


def manage_session(request):
    return render(request,"admin_template/manage_session_template.html")

def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def staff_feedback_message(request):
    feedbacks=FeedBackStaffs.objects.all()
    return render(request,"admin_template/staff_feedback_template.html",{"feedbacks":feedbacks})

def tenant_feedback_message(request):
    feedbacks=FeedBackTenant.objects.all()
    return render(request,"admin_template/tenant_feedback_template.html",{"feedbacks":feedbacks})

@csrf_exempt
def tenant_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackTenant.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def staff_leave_view(request):
    leaves=LeaveReportStaff.objects.all()
    return render(request,"admin_template/staff_leave_view.html",{"leaves":leaves})

def tenant_leave_view(request):
    leaves=LeaveReportTanant.objects.all()
    return render(request,"admin_template/tenant_leave_view.html",{"leaves":leaves})

def tenant_approve_leave(request,leave_id):
    leave=LeaveReportTanant.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("tenant_leave_view"))

def tenant_disapprove_leave(request,leave_id):
    leave=LeaveReportTanant.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("tenant_leave_view"))


def staff_approve_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def staff_disapprove_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def admin_view_arrears(request):
    caretakers=Caretakers.objects.all()
    session_year_id=SessionYearModel.object.all()
    return render(request,"admin_template/admin_view_arrears.html",{"caretakers":caretakers,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_arrears_dates(request):
    caretaker=request.POST.get("caretaker")
    session_year_id=request.POST.get("session_year_id")
    caretaker_obj=Caretakers.objects.get(id=caretaker)
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    arrears=Arrears.objects.filter(caretaker_id=caretaker_obj,session_year_id=session_year_obj)
    arrears_obj=[]
    for arrears_single in arrears:
        data={"id":arrears_single.id,"arrears_date":str(arrears_single.arrears_date),"session_year_id":arrears_single.session_year_id.id}
        arrears_obj.append(data)

    return JsonResponse(json.dumps(arrears_obj),safe=False)


@csrf_exempt
def admin_get_arrears_tenant(request):
    arrears_date=request.POST.get("arrears_date")
    arrears=Arrears.objects.get(id=arrears_date)

    arrears_data=ArrearsReport.objects.filter(arrears_id=arrears)
    list_data=[]

    for tenant in arrears_data:
        data_small={"id":tenant.tenant_id.admin.id,"name":tenant.tenant_id.admin.first_name+" "+tenant.tenant_id.admin.last_name,"status":tenant.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"admin_template/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_tenant(request):
    tenants=Tenants.objects.all()
    return render(request,"admin_template/tenant_notification.html",{"tenants":tenants})

def admin_send_notification_staff(request):
    staffs=Staffs.objects.all()
    return render(request,"admin_template/staff_notification.html",{"staffs":staffs})

@csrf_exempt
def send_tenant_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    Tenant=Tenants.objects.get(admin=id)
    token=Tenant.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Tenant Management System",
            "body":message,
            "click_action": "https://Tenantmanagementsystem22.herokuapp.com/tenant_all_notification",
            "icon": "http://Tenantmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationTenant(tenant_id=Tenant,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_staff_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    staff=Staffs.objects.get(admin=id)
    token=staff.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Tenant Management System",
            "body":message,
            "click_action":"https://Tenantmanagementsystem22.herokuapp.com/staff_all_notification",
            "icon":"http://Tenantmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationStaffs(staff_id=staff,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

