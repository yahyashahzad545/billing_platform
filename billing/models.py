from django.db import models
import uuid


# ─────────────────────────────────────────
# 1. PROVIDER  (aapka existing - same raha)
# ─────────────────────────────────────────
class Provider(models.Model):
    PROVIDER_TYPE_CHOICES = [
        ('doctor',     'Doctor'),
        ('nurse',      'Nurse'),
        ('therapist',  'Therapist'),
        ('specialist', 'Specialist'),
        ('other',      'Other'),
    ]
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    specialty     = models.CharField(max_length=100, blank=True)
    npi_number    = models.CharField(max_length=20, unique=True)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPE_CHOICES, default='doctor')
    is_active     = models.BooleanField(default=True)
    email         = models.EmailField(blank=True)
    phone         = models.CharField(max_length=15, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


# ─────────────────────────────────────────
# 2. PATIENT  ← NEW
# ─────────────────────────────────────────
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    # ── form.py wale fields ──
    full_name     = models.CharField(max_length=200)          # ← ADD
    guardian_name = models.CharField(max_length=200, blank=True)  # ← ADD
    blood_group   = models.CharField(                          # ← ADD
                        max_length=5,
                        choices=BLOOD_GROUP_CHOICES,
                        blank=True
                    )

    # ── baqi fields same rahenge ──
    first_name    = models.CharField(max_length=100, blank=True)
    last_name     = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    email         = models.EmailField(blank=True)
    phone         = models.CharField(max_length=15, blank=True)
    address       = models.TextField(blank=True)
    insurance_id  = models.CharField(max_length=50, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['full_name']


# ─────────────────────────────────────────
# 3. PAYER (Insurance Company)  ← NEW
# ─────────────────────────────────────────
class Payer(models.Model):
    name       = models.CharField(max_length=200)
    payer_id   = models.CharField(max_length=50, unique=True)  # EDI Payer ID
    phone      = models.CharField(max_length=15, blank=True)
    email      = models.EmailField(blank=True)
    address    = models.TextField(blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ─────────────────────────────────────────
# 4. CLAIM  (updated — ForeignKeys add hue)
# ─────────────────────────────────────────
class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid',     'Paid'),
    ]
    claim_id      = models.CharField(max_length=20, unique=True, editable=False)
    patient       = models.ForeignKey(Patient, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='claims')
    patient_name  = models.CharField(max_length=100)   # fallback / display
    payer         = models.ForeignKey(Payer, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='claims')
    provider      = models.ForeignKey(Provider, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='claims')
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    charge_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_date  = models.DateField(null=True, blank=True)
    description   = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.claim_id:
            last = Claim.objects.order_by('-id').first()
            next_num = (int(last.claim_id.split('-')[1]) + 1) if last else 1
            self.claim_id = f"CLM-{str(next_num).zfill(4)}"
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return self.charge_amount - self.paid_amount

    def __str__(self):
        return f"{self.claim_id} - {self.patient_name}"

    class Meta:
        ordering = ['-created_at']


# ─────────────────────────────────────────
# 5. CLAIM LINE ITEM  ← NEW
# ─────────────────────────────────────────
class ClaimLineItem(models.Model):
    claim       = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='line_items')
    cpt_code    = models.CharField(max_length=10)        # Medical procedure code
    description = models.CharField(max_length=255)
    quantity    = models.PositiveIntegerField(default=1)
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cpt_code} - {self.description}"


# ─────────────────────────────────────────
# 6. PAYMENT  ← NEW
# ─────────────────────────────────────────
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('check',       'Check'),
        ('eft',         'EFT / Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('cash',        'Cash'),
        ('other',       'Other'),
    ]
    claim          = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='payments')
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date   = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='eft')
    reference_no   = models.CharField(max_length=100, blank=True)  # Check no. ya Transaction ID
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.claim.claim_id}"

    class Meta:
        ordering = ['-payment_date']