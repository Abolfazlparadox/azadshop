# views.py
from django.urls import reverse_lazy
from datetime import date
from django.contrib.auth.views import LoginView
from django.views import View
from guardian.shortcuts import get_objects_for_user
from django.views.generic import CreateView,UpdateView
from iranian_cities.models import Province, City
from university.models import University
from django.utils.translation import gettext_lazy as _
from .forms import SignupForm, UserDashboardForm, CustomAuthenticationForm, AddressForm, VerifyTokenForm
from .models import User, Membership, Address
from django.contrib.auth.views import LogoutView
import random
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestRoleForm,ForgotPasswordForm, OTPForm, ResetPasswordForm
from django.contrib import messages
# views.py

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = "account/sign-up.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("ثبت‌نام شما با موفقیت انجام شد. اکنون می‌توانید وارد شوید."),
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumb"] = [
            {"name": _("حساب کاربری"), "url": reverse_lazy("login")},
            {"name": _("ثبت‌نام"), "url": ""},
        ]
        ctx["breadcrumb_title"] = _("حساب کاربری : ثبت‌نام")
        return ctx

class VerifyEmailView(View):
    form_class = VerifyTokenForm
    template_name = 'account/verify-email.html'

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, self.template_name, {
            'form': self.form_class(),
            'user': user
        })

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = self.form_class(request.POST)
        if form.is_valid():
            if form.cleaned_data['token'] == user.email_verification_token:
                user.email_verified = True
                user.email_verification_token = ''
                user.save(update_fields=['email_verified', 'email_verification_token'])
                messages.success(request, _("ایمیل شما با موفقیت تأیید شد. اکنون می‌توانید وارد شوید."))
                return redirect('login')
            else:
                form.add_error('token', _("کد اشتباه است. لطفا دوباره تلاش کنید."))
        return render(request, self.template_name, {
            'form': form,
            'user': user
        })

class CustomLoginView(LoginView):
    template_name = "account/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, _("شما با موفقیت وارد شدید."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("نام کاربری یا کلمه عبور اشتباه است."))
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("user_dashboard")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumb"] = [
            {"name": _("حساب کاربری"), "url": reverse_lazy("login")},
            {"name": _("ورود"), "url": ""},
        ]
        ctx["breadcrumb_title"] = _("حساب کاربری : ورود")
        return ctx

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _("شما با موفقیت خارج شدید."))
        return super().dispatch(request, *args, **kwargs)

class ForgotPasswordView(FormView):
    template_name = "account/forgot_password_email.html"
    form_class = ForgotPasswordForm
    success_url = reverse_lazy("verify_otp")

    def form_valid(self, form):
        email = form.cleaned_data["username"]
        user = User.objects.filter(email=email).first()
        if not user:
            form.add_error("username", _("حسابی با این ایمیل یافت نشد."))
            return self.form_invalid(form)

        user.otp_secret = str(random.randint(100000, 999999))
        user.save(update_fields=["otp_secret"])
        self.request.session["forgot_email"] = email
        messages.success(self.request, _("کد بازیابی به ایمیل شما ارسال شد."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumb"] = [
            {"name": _("حساب کاربری"), "url": reverse_lazy("login")},
            {"name": _("فراموشی رمز عبور"), "url": ""},
        ]
        ctx["breadcrumb_title"] = _("حساب کاربری : فراموشی رمز عبور")
        return ctx

class VerifyOTPView(FormView):
    template_name = "account/verify_otp.html"
    form_class = OTPForm
    success_url = reverse_lazy("reset_password")

    def form_valid(self, form):
        otp_input = form.cleaned_data["otp_code"]
        email = self.request.session.get("forgot_email")
        user = User.objects.filter(email=email).first()
        if not user or user.otp_secret != otp_input:
            form.add_error("otp_code", _("کد وارد شده صحیح نمی‌باشد."))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumb"] = [
            {"name": _("حساب کاربری"), "url": reverse_lazy("login")},
            {"name": _("تأیید کد بازیابی"), "url": ""},
        ]
        ctx["breadcrumb_title"] = _("حساب کاربری : تأیید کد بازیابی")
        return ctx

class ResetPasswordView(FormView):
    template_name = "account/reset_password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        pwd = form.cleaned_data["new_password"]
        cpwd = form.cleaned_data["confirm_password"]
        email = self.request.session.get("forgot_email")
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(self.request, _("حساب کاربری یافت نشد."))
            return redirect("forgot_password")
        if pwd != cpwd:
            form.add_error("confirm_password", _("رمز عبور و تکرار آن مطابقت ندارند."))
            return self.form_invalid(form)

        user.set_password(pwd)
        user.otp_secret = ""
        user.save(update_fields=["password", "otp_secret"])
        messages.success(
            self.request,
            _("رمز عبور با موفقیت تغییر یافت. لطفاً وارد شوید."),
        )
        self.request.session.pop("forgot_email", None)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumb"] = [
            {"name": _("حساب کاربری"), "url": reverse_lazy("login")},
            {"name": _("تغییر رمز عبور"), "url": ""},
        ]
        ctx["breadcrumb_title"] = _("حساب کاربری : تغییر رمز عبور")
        return ctx

class UserDashboardView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserDashboardForm
    template_name = "account/user-dashboard.html"
    success_url = reverse_lazy("user_dashboard")

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        if "avatar" in request.FILES:
            u = request.user
            u.avatar = request.FILES["avatar"]
            u.save(update_fields=["avatar"])
            messages.success(request, _("تصویر پروفایل با موفقیت بروزرسانی شد."))
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        user = self.request.user

        # Basic info
        ctx["full_name"] = user.get_full_name() or user.username
        ctx["email"]     = user.email

        # Location: "استان، شهر"
        province = user.province.name if user.province else ""
        city     = user.city.name     if user.city else ""
        ctx["location"] = "، ".join(filter(None, [province, city]))

        # Account age in years
        if user.date_joined:
            days = (date.today() - user.date_joined.date()).days
            ctx["activity_years"] = days // 365
        else:
            ctx["activity_years"] = 0

        # Other profile fields
        ctx.update({
            "national_code": user.national_code,
            "birthday":      user.birthday,
            "phone":         user.mobile,
            "address":       user.address,
            "postal_code":   user.postal_code,
        })

        # Determine if user is a unit-officer
        is_officer = Membership.objects.filter(
            user=user,
            role=Membership.Role.UNIT_OFFICER,
            is_confirmed=True
        ).exists()

        if is_officer:
            # Unit-officers see all memberships in THEIR city
            ctx["memberships"] = Membership.objects.filter(
                is_confirmed=True,
                university__city=user.city
            ).select_related("university", "user")
        else:
            # Others see only their own confirmed memberships
            ctx["memberships"] = user.memberships.filter(
                is_confirmed=True
            ).select_related("university")

        # Addresses & forms for Add/Edit modals
        ctx["address_form"]  = AddressForm()
        ctx["address_forms"] = {
            addr.id: AddressForm(instance=addr)
            for addr in user.addresses.all()
        }

        # Lookup data for selects
        ctx.update({
            "universities": University.objects.only("id", "name"),
            "provinces":    Province.objects.only("id", "name"),
            "cities":       City.objects.only("id", "name"),
        })

        # Breadcrumb
        ctx["breadcrumb"] = [
            {"name": _("حساب کاربری"), "url": reverse_lazy("user_dashboard")},
            {"name": _("داشبورد"),      "url": ""},
        ]
        ctx["breadcrumb_title"] = _("حساب کاربری : داشبورد")

        return ctx

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    # We won’t use a separate template; we’ll post back to the dashboard
    success_url = reverse_lazy('user_dashboard')

    def get_queryset(self):
        # Ensure users can only edit their own addresses
        return super().get_queryset().filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    success_url = reverse_lazy('user_dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AddressSetDefaultView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # clear old default
        Address.objects.filter(user=request.user, active=True).update(active=False)
        # set new default
        addr = get_object_or_404(Address, pk=pk, user=request.user)
        addr.active = True
        addr.save(update_fields=['active'])
        return redirect('user_dashboard')

class RequestRoleView(LoginRequiredMixin, FormView):
    template_name = 'account/request_role.html'
    form_class    = RequestRoleForm
    success_url   = reverse_lazy('user_dashboard')

    def form_valid(self, form):
        m, created = Membership.objects.get_or_create(
            user=self.request.user,
            university=form.cleaned_data['university'],
            role=form.cleaned_data['role'],
            defaults={'code': form.cleaned_data['code']}
        )
        if not created:
            messages.warning(self.request, _("شما قبلا برای این نقش درخواست داده‌اید."))
        else:
            messages.success(self.request, _("درخواست شما ثبت شد؛ منتظر تایید مدیر باشید."))
        return super().form_valid(form)

class LevelRequiredMixin:
    """
    Mixin to enforce a minimum access_level on class-based views.
    usage: subclass and set "min_level = User.Level.PROFILE_COMPLETED"
    """
    min_level = User.Level.EMAIL_CONFIRMED

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if user.access_level < self.min_level:
            messages.warning(request, _("برای دسترسی به این بخش باید ابتدا سطح دسترسی خود را ارتقا دهید."))
            # redirect to dashboard or a custom page
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)

class ProfileSettingsView(LoginRequiredMixin, LevelRequiredMixin, UpdateView):
    min_level = User.Level.PROFILE_COMPLETED
    model = User
    form_class = UserDashboardForm
    template_name = 'account/user-dashboard.html'

    def get_object(self):
        return self.request.user
