import json
import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
# from property_management_app.forms import AddTenantForm, EditTenantForm
from property_management_app.models import CustomUser, Staffs, Properties, Caretakers, Tenants, SessionYearModel, \
    FeedBackTenant, FeedBackStaffs, LeaveReportStaff, Arrears, ArrearsReport, \
    NotificationTenant, NotificationStaffs


def admin_home(request):
    tenant_count1 = Tenants.objects.all().count()
    staff_count = Staffs.objects.all().count()
    subject_count = Caretakers.objects.all().count()
    course_count = Properties.objects.all().count()

    course_all = Properties.objects.all()
    course_name_list = []
    subject_count_list = []
    tenant_count_list_in_course = []

    for course in course_all:
        caretaker_count = Caretakers.objects.filter(course_id=course.id).count()
        tenant_count = Tenants.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(caretaker_count)
        tenant_count_list_in_course.append(tenant_count)

    Caretakers_all = Caretakers.objects.all()
    subject_list = []
    tenant_count_list_in_subject = []

    for caretaker in Caretakers_all:
        course = Properties.objects.get(id=caretaker.course_id.id)
        tenant_count = Tenants.objects.filter(course_id=course.id).count()
        subject_list.append(caretaker.subject_name)
        tenant_count_list_in_subject.append(tenant_count)

    staffs = Staffs.objects.all()
    Arrears_present_list_staff = []
    Arrears_absent_list_staff = []
    staff_name_list = []

    for staff in staffs:
        subject_ids = Caretakers.objects.filter(staff_id=staff.admin.id)
        arrears_count = Arrears.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        Arrears_present_list_staff.append(arrears_count)
        Arrears_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    Tenants_all = Tenants.objects.all()
    Arrears_present_list_tenant = []
    Arrears_absent_list_tenant = []
    tenant_name_list = []

    for tenant in Tenants_all:
        arrears_count = ArrearsReport.objects.filter(tenant_id=tenant.id, status=True).count()
        absent_count = ArrearsReport.objects.filter(tenant_id=tenant.id, status=False).count()
        Arrears_present_list_tenant.append(arrears_count)
        Arrears_absent_list_tenant.append(leaves + absent_count)
        tenant_name_list.append(tenant.admin.username)

    context = {
        "tenant_count": tenant_count1,
        "staff_count": staff_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "tenant_count_list_in_course": tenant_count_list_in_course,
        "tenant_count_list_in_subject": tenant_count_list_in_subject,
        "subject_list": subject_list,
        "staff_name_list": staff_name_list,
        "Arrears_present_list_staff": Arrears_present_list_staff,
        "Arrears_absent_list_staff": Arrears_absent_list_staff,
        "tenant_name_list": tenant_name_list,
        "Arrears_present_list_tenant": Arrears_present_list_tenant,
        "Arrears_absent_list_tenant": Arrears_absent_list_tenant,
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
        course=request.POST.get("course")
        try:
            course_model=Properties(course_name=course)
            course_model.save()
            messages.success(request,"Successfully Added Course")
            return HttpResponseRedirect(reverse("add_property"))
        except Exception as e:
            print(e)
            messages.error(request,"Failed To Add Course")
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
            course_id=form.cleaned_data["course"]
            sex=form.cleaned_data["sex"]

            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)

            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.Tenants.address=address
                course_obj=Properties.objects.get(id=course_id)
                user.Tenants.course_id=course_obj
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


def add_subject(request):
    Properties=Properties.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"admin_template/add_subject_template.html",{"staffs":staffs,"Properties":Properties})

def add_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        course_id=request.POST.get("course")
        course=Properties.objects.get(id=course_id)
        staff_id=request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)

        try:
            subject=Caretakers(subject_name=subject_name,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,"Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))


def manage_staff(request):
    staffs=Staffs.objects.all()
    return render(request,"admin_template/manage_staff_template.html",{"staffs":staffs})

def manage_tenant(request):
    Tenants=Tenants.objects.all()
    return render(request,"admin_template/manage_tenant_template.html",{"Tenants":Tenants})

def manage_property(request):
    Properties=Properties.objects.all()
    return render(request,"admin_template/manage_property_template.html",{"Properties":Properties})

def manage_caretaker(request):
    Caretakers=Caretakers.objects.all()
    return render(request,"admin_template/manage_caretaker_template.html",{"Caretakers":Caretakers})

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
    Tenant=Tenants.objects.get(admin=tenant_id)
    form=EditTenantForm()
    form.fields['email'].initial=Tenant.admin.email
    form.fields['first_name'].initial=Tenant.admin.first_name
    form.fields['last_name'].initial=Tenant.admin.last_name
    form.fields['username'].initial=Tenant.admin.username
    form.fields['address'].initial=Tenant.address
    form.fields['course'].initial=Tenant.course_id.id
    form.fields['sex'].initial=Tenant.gender
    form.fields['session_year_id'].initial=Tenant.session_year_id.id
    return render(request,"admin_template/edit_tenant_template.html",{"form":form,"id":tenant_id,"username":Tenant.admin.username})

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
            course_id = form.cleaned_data["course"]
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

                Tenant=Tenants.objects.get(admin=tenant_id)
                Tenant.address=address
                session_year = SessionYearModel.object.get(id=session_year_id)
                Tenant.session_year_id = session_year
                Tenant.gender=sex
                course=Properties.objects.get(id=course_id)
                Tenant.course_id=course
                if profile_pic_url!=None:
                    Tenant.profile_pic=profile_pic_url
                Tenant.save()
                del request.session['tenant_id']
                messages.success(request,"Successfully Edited Tenant")
                return HttpResponseRedirect(reverse("edit_tenant",kwargs={"tenant_id":tenant_id}))
            except:
                messages.error(request,"Failed to Edit Tenant")
                return HttpResponseRedirect(reverse("edit_tenant",kwargs={"tenant_id":tenant_id}))
        else:
            form=EditTenantForm(request.POST)
            Tenant=Tenants.objects.get(admin=tenant_id)
            return render(request,"admin_template/edit_tenant_template.html",{"form":form,"id":tenant_id,"username":Tenant.admin.username})

def edit_subject(request,subject_id):
    subject=Caretakers.objects.get(id=subject_id)
    Properties=Properties.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"admin_template/edit_subject_template.html",{"subject":subject,"staffs":staffs,"Properties":Properties,"id":subject_id})

def edit_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")
        subject_name=request.POST.get("subject_name")
        staff_id=request.POST.get("staff")
        course_id=request.POST.get("course")

        try:
            subject=Caretakers.objects.get(id=subject_id)
            subject.subject_name=subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Properties.objects.get(id=course_id)
            subject.course_id=course
            subject.save()

            messages.success(request,"Successfully Edited Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))
        except:
            messages.error(request,"Failed to Edit Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))


def edit_course(request,course_id):
    course=Properties.objects.get(id=course_id)
    return render(request,"admin_template/edit_course_template.html",{"course":course,"id":course_id})

def edit_course_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id=request.POST.get("course_id")
        course_name=request.POST.get("course")

        try:
            course=Properties.objects.get(id=course_id)
            print(Properties.course_name)
            course.course_name=course_name
            course.save()
            messages.success(request,"Successfully Edited Course")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))
        except:
            messages.error(request,"Failed to Edit Course")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))


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
    leaves=LeaveReportTenant.objects.all()
    return render(request,"admin_template/tenant_leave_view.html",{"leaves":leaves})

def tenant_approve_leave(request,leave_id):
    leave=LeaveReportTenant.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("tenant_leave_view"))

def tenant_disapprove_leave(request,leave_id):
    leave=LeaveReportTenant.objects.get(id=leave_id)
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

def admin_view_Arrears(request):
    Caretakers=Caretakers.objects.all()
    session_year_id=SessionYearModel.object.all()
    return render(request,"admin_template/admin_view_Arrears.html",{"Caretakers":Caretakers,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_Arrears_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Caretakers.objects.get(id=subject)
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    Arrears=Arrears.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    Arrears_obj=[]
    for Arrears_single in Arrears:
        data={"id":Arrears_single.id,"Arrears_date":str(Arrears_single.Arrears_date),"session_year_id":Arrears_single.session_year_id.id}
        Arrears_obj.append(data)

    return JsonResponse(json.dumps(Arrears_obj),safe=False)


@csrf_exempt
def admin_get_Arrears_tenant(request):
    Arrears_date=request.POST.get("Arrears_date")
    Arrears=Arrears.objects.get(id=Arrears_date)

    Arrears_data=ArrearsReport.objects.filter(Arrears_id=Arrears)
    list_data=[]

    for Tenant in Arrears_data:
        data_small={"id":Tenant.tenant_id.admin.id,"name":Tenant.tenant_id.admin.first_name+" "+Tenant.tenant_id.admin.last_name,"status":Tenant.status}
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
    Tenants=Tenants.objects.all()
    return render(request,"admin_template/tenant_notification.html",{"Tenants":Tenants})

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

