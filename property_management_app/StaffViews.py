import json
from datetime import datetime
from uuid import uuid4

from django.contrib import messages
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from property_management_app.models import Caretakers, SessionYearModel, Tenants, Arrears, ArrearsReport, \
    LeaveReportStaff, Staffs, FeedBackStaffs, CustomUser, Properties, NotificationStaffs


def staff_home(request):
    #For Fetch All Tenant Under Staff
    caretakers=Caretakers.objects.filter(staff_id=request.user.id)
    property_id_list=[]
    for caretaker in caretakers:
        property=Properties.objects.get(id=caretaker.property_id.id)
        property_id_list.append(property.id)

    final_property=[]
    #removing Duplicate Course ID
    for property_id in property_id_list:
        if property_id not in final_property:
            final_property.append(property_id)

    tenants_count=Tenants.objects.filter(property_id__in=final_property).count()

    #Fetch All Arrears Count
    arrears_count=Arrears.objects.count()

    #Fetch All Approve Leave
    staff=Staffs.objects.get(admin=request.user.id)
    leave_count=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
    caretaker_count=caretakers.count()

    #Fetch Arrears Data by Subject
    caretaker_list=[]
    arrears_list=[]
    for caretaker in caretakers:
        arrears_count1=Arrears.objects.filter(caretaker_id=caretaker.id).count()
        caretaker_list.append(caretaker.caretaker_name)
        arrears_list.append(arrears_count1)

    tenants_arrears=Tenants.objects.filter(property_id__in=final_property)
    tenant_list=[]
    tenant_list_arrears_present=[]
    tenant_list_arrears_absent=[]
    for tenant in tenants_arrears:
        arrears_present_count=ArrearsReport.objects.filter(status=True,tenant_id=tenant.id).count()
        arrears_absent_count=ArrearsReport.objects.filter(status=False,tenant_id=tenant.id).count()
        tenant_list.append(tenant.admin.username)
        tenant_list_arrears_present.append(arrears_present_count)
        tenant_list_arrears_absent.append(arrears_absent_count)

    return render(request,"staff_template/staff_home_template.html",{"tenants_count":tenants_count,"arrears_count":arrears_count,"leave_count":leave_count,"caretaker_count":caretaker_count,"caretaker_list":caretaker_list,"arrears_list":arrears_list,"tenant_list":tenant_list,"present_list":tenant_list_arrears_present,"absent_list":tenant_list_arrears_absent})

def staff_take_arrears(request):
    caretakers=Caretakers.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.object.all()
    return render(request,"staff_template/staff_take_arrears.html",{"caretakers":caretakers,"session_years":session_years})

@csrf_exempt
def get_tenants(request):
    caretaker_id=request.POST.get("caretaker")
    session_year=request.POST.get("session_year")

    caretaker=Caretakers.objects.get(id=caretaker_id)
    session_model=SessionYearModel.object.get(id=session_year)
    tenants=Tenants.objects.filter(property_id=caretaker.property_id,session_year_id=session_model)
    list_data=[]

    for tenant in tenants:
        data_small={"id":tenant.admin.id,"name":tenant.admin.first_name+" "+tenant.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_arrears_data(request):
    tenant_ids=request.POST.get("tenant_ids")
    caretaker_id=request.POST.get("caretaker_id")
    arrears_date=request.POST.get("arrears_date")
    session_year_id=request.POST.get("session_year_id")

    caretaker_model=Caretakers.objects.get(id=caretaker_id)
    session_model=SessionYearModel.object.get(id=session_year_id)
    json_stenant=json.loads(tenant_ids)
    #print(data[0]['id'])


    try:
        arrears=Arrears(caretaker_id=caretaker_model,arrears_date=arrears_date,session_year_id=session_model)
        arrears.save()

        for stud in json_stenant:
             tenant=Tenants.objects.get(admin=stud['id'])
             arrears_report=ArrearsReport(tenant_id=tenant,arrears_id=arrears,status=stud['status'])
             arrears_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

def staff_update_arrears(request):
    caretakers=Caretakers.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.object.all()
    return render(request,"staff_template/staff_update_arrears.html",{"caretakers":caretakers,"session_year_id":session_year_id})

@csrf_exempt
def get_arrears_dates(request):
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
def get_arrears_tenant(request):
    arrears_date=request.POST.get("arrears_date")
    arrears=Arrears.objects.get(id=arrears_date)

    arrears_data=ArrearsReport.objects.filter(arrears_id=arrears)
    list_data=[]

    for tenant in arrears_data:
        data_small={"id":tenant.tenant_id.admin.id,"name":tenant.tenant_id.admin.first_name+" "+tenant.tenant_id.admin.last_name,"status":tenant.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_updatearrears_data(request):
    tenant_ids=request.POST.get("tenant_ids")
    arrears_date=request.POST.get("arrears_date")
    arrears=Arrears.objects.get(id=arrears_date)

    json_stenant=json.loads(tenant_ids)


    try:
        for stud in json_stenant:
             tenant=Tenants.objects.get(admin=stud['id'])
             arrears_report=ArrearsReport.objects.get(tenant_id=tenant,arrears_id=arrears)
             arrears_report.status=stud['status']
             arrears_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data=LeaveReportStaff.objects.filter(staff_id=staff_obj)
    return render(request,"staff_template/staff_apply_leave.html",{"leave_data":leave_data})

def staff_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStaff(staff_id=staff_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))


def staff_feedback(request):
    staff_id=Staffs.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaffs.objects.filter(staff_id=staff_id)
    return render(request,"staff_template/staff_feedback.html",{"feedback_data":feedback_data})

def staff_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaffs(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))

def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    return render(request,"staff_template/staff_profile.html",{"user":user,"staff":staff})

def staff_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        address=request.POST.get("address")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            staff=Staffs.objects.get(admin=customuser.id)
            staff.address=address
            staff.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("staff_profile"))

@csrf_exempt
def staff_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        staff=Staffs.objects.get(admin=request.user.id)
        staff.fcm_token=token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def staff_all_notification(request):
    staff=Staffs.objects.get(admin=request.user.id)
    notifications=NotificationStaffs.objects.filter(staff_id=staff.id)
    return render(request,"staff_template/all_notification.html",{"notifications":notifications})

def staff_add_result(request):
    caretakers=Caretakers.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.object.all()
    return render(request,"staff_template/staff_add_result.html",{"caretakers":caretakers,"session_years":session_years})

def save_tenant_result(request):
    if request.method!='POST':
        return HttpResponseRedirect('staff_add_result')
    tenant_admin_id=request.POST.get('tenant_list')
    assignment_marks=request.POST.get('assignment_marks')
    exam_marks=request.POST.get('exam_marks')
    caretaker_id=request.POST.get('caretaker')


    tenant_obj=Tenants.objects.get(admin=tenant_admin_id)
    caretaker_obj=Caretakers.objects.get(id=caretaker_id)

    try:
        check_exist=TenantResult.objects.filter(caretaker_id=caretaker_obj,tenant_id=tenant_obj).exists()
        if check_exist:
            result=TenantResult.objects.get(caretaker_id=caretaker_obj,tenant_id=tenant_obj)
            result.caretaker_assignment_marks=assignment_marks
            result.caretaker_exam_marks=exam_marks
            result.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("staff_add_result"))
        else:
            result=TenantResult(tenant_id=tenant_obj,caretaker_id=caretaker_obj,caretaker_exam_marks=exam_marks,caretaker_assignment_marks=assignment_marks)
            result.save()
            messages.success(request, "Successfully Added Result")
            return HttpResponseRedirect(reverse("staff_add_result"))
    except:
        messages.error(request, "Failed to Add Result")
        return HttpResponseRedirect(reverse("staff_add_result"))

@csrf_exempt
def fetch_result_tenant(request):
    caretaker_id=request.POST.get('caretaker_id')
    tenant_id=request.POST.get('tenant_id')
    tenant_obj=Tenants.objects.get(admin=tenant_id)
    result=TenantResult.objects.filter(tenant_id=tenant_obj.id,caretaker_id=caretaker_id).exists()
    if result:
        result=TenantResult.objects.get(tenant_id=tenant_obj.id,caretaker_id=caretaker_id)
        result_data={"exam_marks":result.caretaker_exam_marks,"assign_marks":result.caretaker_assignment_marks}
        return HttpResponse(json.dumps(result_data))
    else:
        return HttpResponse("False")

def returnHtmlWidget(request):
    return render(request,"widget.html")