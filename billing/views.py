from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient
from .forms import PatientForm
from django.shortcuts import render



# 📋 Patient List + Search
def patient_list(request):
    query    = request.GET.get('q', '')
    patients = Patient.objects.filter(
        full_name__icontains=query
    ) if query else Patient.objects.all()
    return render(request, 'patients/patient_list.html', {
        'patients': patients, 'query': query
    })

# ➕ Register New Patient
def patient_create(request):
    form = PatientForm(request.POST or None)
    if form.is_valid():
        patient = form.save()
        return redirect('patient_detail', pk=patient.pk)
    return render(request, 'patients/patient_form.html', {'form': form})

# 👁️ Patient Detail
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/patient_detail.html', {'patient': patient})

# ✏️ Edit Patient
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form    = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        return redirect('patient_detail', pk=pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'edit': True})


def dashboard(request):
    return render(request, 'dashboard.html')

def claims_list(request):
    return render(request, 'claims.html')