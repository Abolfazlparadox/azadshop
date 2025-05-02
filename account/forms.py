# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Membership, Address
from iranian_cities.models import Province, City
from university.models import University

class SignupForm(UserCreationForm):
    fullname = forms.CharField(
        label=_("نام و نام خانوادگی"),
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': _('نام و نام خانوادگی'), 'class': 'form-control'})
    )
    terms_accepted = forms.BooleanField(
        label=_("شرایط و قوانین را می‌پذیرم"),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        # include the two password fields from UserCreationForm
        fields = ['fullname', 'email', 'password1', 'password2', 'terms_accepted']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('آدرس ایمیل خود را وارد کنید')
            }),
        }

    def clean_fullname(self):
        fullname = self.cleaned_data['fullname'].strip()
        if len(fullname.split()) < 2:
            raise forms.ValidationError(_("لطفا نام و نام خانوادگی را به صورت کامل وارد کنید"))
        return fullname

    def save(self, commit=True):
        user = super().save(commit=False)
        # split fullname into first/last
        first, *rest = self.cleaned_data['fullname'].split(maxsplit=1)
        user.first_name = first
        user.last_name = rest[0] if rest else ''
        user.username = self.cleaned_data['email']
        # role and other defaults
        user.role = 'CUST'
        if commit:
            user.save()
        return user

class VerifyTokenForm(forms.Form):
    token = forms.CharField(
        label=_("کد تأیید ایمیل"),
        max_length=64,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('کد تأیید خود را وارد کنید')
        })
    )

class VerifiedAuthenticationForm(AuthenticationForm):
        def confirm_login_allowed(self, user):
            super().confirm_login_allowed(user)
            if not user.email_verified:
                raise forms.ValidationError(
                    _("شما باید ابتدا ایمیل خود را تأیید کنید."),
                    code='email_not_verified'
                )

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("آدرس ایمیل"),
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': _('آدرس ایمیل خود را وارد کنید')})
    )
    password = forms.CharField(
        label=_("رمز عبور"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': _('رمز عبور خود را وارد کنید')})
    )

    error_messages = {
        'invalid_login': _("ایمیل یا رمز عبور صحیح نیست."),
        'inactive': _("حساب کاربری شما غیرفعال شده است."),
    }

class RequestRoleForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['university','role','code']
        widgets = {
            'university': forms.Select(attrs={'class':'form-select'}),
            'role':       forms.Select(attrs={'class':'form-select'}),
            'code':       forms.TextInput(attrs={'class':'form-control','placeholder':_('کد نقش را وارد کنید')}),
        }

class ForgotPasswordForm(forms.Form):
    username = forms.EmailField(
        label=_("ایمیل"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('ایمیل خود را وارد کنید')
        })
    )

class OTPForm(forms.Form):
    otp_code = forms.CharField(
        label=_("کد بازیابی"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('کد بازیابی را وارد کنید')
        })
    )

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label=_("رمز جدید"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('رمز جدید')
        })
    )
    confirm_password = forms.CharField(
        label=_("تکرار رمز جدید"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('تکرار رمز جدید')
        })
    )

class UserDashboardForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_("نام"),
        required=True,
        help_text=_("نام خود را وارد کنید"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('نام خود را وارد کنید'),
        }),
        error_messages={'required': _("وارد کردن نام الزامی است.")}
    )
    last_name = forms.CharField(
        label=_("نام خانوادگی"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('نام خانوادگی خود را وارد کنید'),
        }),
        error_messages={'required': _("وارد کردن نام خانوادگی الزامی است.")}
    )
    email = forms.EmailField(
        label=_("ایمیل"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('آدرس ایمیل خود را وارد کنید'),
        }),
        error_messages={
            'required': _("وارد کردن ایمیل الزامی است."),
            'invalid': _("فرمت ایمیل صحیح نیست.")
        }
    )
    mobile = forms.CharField(
        label=_("شماره تماس"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('مثال: +98912xxxxxxx'),
            'maxlength': 15,
        }),
    )
    national_code = forms.CharField(
        label=_("کد ملی"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('کد ملی 10 رقمی'),
            'maxlength': 10,
        }),
        error_messages={'required': _("وارد کردن کد ملی الزامی است.")}
    )
    birthday = forms.DateField(
        label=_("تاریخ تولد"),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    avatar = forms.ImageField(
        label=_("تصویر پروفایل"),
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    province = forms.ModelChoiceField(
        label=_("استان"),
        queryset=Province.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.ModelChoiceField(
        label=_("شهر"),
        queryset=City.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    university = forms.ModelChoiceField(
        label=_("دانشگاه"),
        queryset=University.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        label=_("آدرس دقیق"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('آدرس کامل خود را وارد کنید'),
        })
    )
    postal_code = forms.CharField(
        label=_("کد پستی"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('کد پستی'),
            'maxlength': 10,
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'mobile', 'national_code',
            'birthday', 'avatar', 'province', 'city', 'university',
            'address', 'postal_code',
        ]

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'name','category','address',
            'postal_code','telephone','province',
            'city','active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('عنوان نشانی خود را وارد کنید'),
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('آدرس کامل خود را وارد کنید'),
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('کد پستی خود را وارد کنید'),
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('شماره تماس خود را وارد کنید'),
            }),
            'province': forms.Select(attrs={
                'class': 'form-select',
            }),
            'city': forms.Select(attrs={
                'class': 'form-select',
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }