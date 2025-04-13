from django.shortcuts import render, redirect
from django.contrib import messages
from userapp.models import *

# Create your views here.
def admin_cnn(req):
    return render(req,'admin/cnn.html')

def admin_feedback(req):
    feed = UserFeedbackModels.objects.all()

    return render(req,"admin/feedback.html",{'back':feed})

def admin_graphanalysis(req):
    return render(req,'admin/graphanalysis.html') 

def admin_index(req):
    files = UploadedFile.objects.filter(folder__isnull=True).count()  # Fetch only standalone files
    folders = UploadedFolder.objects.all().count()
    rejected = UserDetails.objects.filter(user_status = "pending").count()
    accepted = UserDetails.objects.filter(user_status = "Accepted").count()

    return render(req, 'admin/index.html', {"files": files,"folders": folders, "rejected":rejected, 'accepted':accepted})


def admin_manageusers(req):
    user = UserDetails.objects.all()
    return render(req,'admin/manageusers.html', context = {'u':user})

def admin_pendingusers(req):
    users = UserDetails.objects.filter(user_status = "pending")
    return render(req,'admin/pendingusers.html', context = {"u":users})

def admin_sentimentanalysis(req):
    feed = UserFeedbackModels.objects.all()
    return render(req,"admin/sentimentanalysis.html",{'back':feed})

def admin_sentimentgraph(req):
    positive = UserFeedbackModels.objects.filter(sentment = 'positive').count()
    very_positive = UserFeedbackModels.objects.filter(sentment = 'very positive').count()
    negative = UserFeedbackModels.objects.filter(sentment = 'negative').count()
    very_negative = UserFeedbackModels.objects.filter(sentment = 'very negative').count()
    neutral = UserFeedbackModels.objects.filter(sentment = 'neutral').count()
    context ={
        'vp': very_positive, 'p':positive, 'n':negative, 'vn':very_negative, 'ne':neutral
    }
    return render(req,"admin/sentimentgraph.html", context)

def Admin_Reject_Btn(request, x):
    user = UserDetails.objects.get(id=x)
    user.user_status = "Rejected" 
    messages.success(request,"Status Changed  Successfully")
    user.save()
    return redirect("admin_pendingusers")

def Admin_Accept_Button(request,x):
    user=UserDetails.objects.get(id=x)
    user.user_status="Accepted"
    messages.success(request,'Accepted')
    user.save()
    return redirect("admin_pendingusers")

def change_status(request, x, obj_type, status):
    """Handles accepting or rejecting files and folders."""
    if obj_type == "file":
        obj = UploadedFile.objects.get(id=x)
        obj.file_status = status
        redirect_url = "pendingfiles"
    elif obj_type == "folder":
        obj = UploadedFolder.objects.get(id=x)
        obj.folder_status = status
        redirect_url = "pending_folders"
    else:
        messages.error(request, "Invalid object type!")
        return redirect("admin_index")

    obj.save()
    messages.success(request, f"Status changed to {status} successfully!")
    return redirect(redirect_url)

def Change_Status(request,x):
    user = UserDetails.objects.get(id=x)
    if user.user_status == "Accepted":
        user.user_status = "Rejected"
        user.save()
        messages.success(request,"Status Changed Successfully")
        return redirect('admin_manageusers')

    elif user.user_status == "Rejected":
        user.user_status="Accepted"
        user.save()
        messages.success(request,"Status Changed Successfully")
    return redirect("admin_manageusers")

def delete_Files(request,id):
    file = UploadedFile.objects.get(id=id)
    file.delete()
    messages.info(request,"File deleted")

    return redirect("manage_files")
 
  

def delete_User(request,x):
    user = UserDetails.objects.get(id=x)
    user.delete()
    messages.info(request,"User deleted")

    return redirect("admin_manageusers")


def pending_folders(request):
    folders = UploadedFolder.objects.filter(folder_status="pending").prefetch_related("files")
    return render(request, "admin/pendingfolders.html", {"folders": folders})


def pendingfiles(request):
    files = UploadedFile.objects.filter(file_status="pending", folder__isnull=True)  
    return render(request, "admin/pendingfiles.html", {"files": files})

  
import os
import zipfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
 
def download_folder(request, folder_id):
    folder = get_object_or_404(UploadedFolder, id=folder_id)
     
    # Define a temporary zip file
    zip_filename = f"{folder.name}.zip"
    zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)  # Save inside MEDIA_ROOT

    # Create a zip file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in folder.files.all():
            file_path = file.file.path  # Assuming 'file' field has a valid path
            if os.path.exists(file_path):  # Ensure the file exists
                zipf.write(file_path, os.path.basename(file_path))

    # Serve the zip file as a response
    with open(zip_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'

    # Optionally delete the zip file after serving
    os.remove(zip_path)

    return response  # Return the file instead of redirecting


def delete_folder(req,id):
    folders = UploadedFolder.objects.get(id=id)
    folders.delete()
    messages.info(req,"Folder deleted")

    return redirect('manage_folders')