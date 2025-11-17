from django.shortcuts import render

def index(request):
    return render(request, 'portal/index.html')

def order(request):
    return render(request, 'portal/order.html')

def wizard(request):
    return render(request, 'portal/wizard.html')

def help_page(request):
    return render(request, 'portal/help.html')

def directory(request):  
	return render(request, 'portal/directory.html')
	
def staff(request):      
	return render(request, 'portal/staff.html')