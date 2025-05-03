# unit_admin/middleware.py
from django.http import HttpResponseForbidden

class AdminAccessControl:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.memberships.filter(role='OFFI').exists():
                return HttpResponseForbidden("""
                    <div dir="rtl" style="padding: 20px;">
                        <h2>۴۰۳ - دسترسی ممنوع</h2>
                        <p>
                            شما از پنل مدیریت اختصاصی خود استفاده کنید:
                            <a href="/unit-admin/">پنل مدیریت واحد</a>
                        </p>
                    </div>
                """)
        return self.get_response(request)