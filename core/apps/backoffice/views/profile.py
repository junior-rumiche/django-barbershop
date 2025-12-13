from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.db.models import Sum
from core.apps.backoffice.forms import UserProfileForm
from core.apps.backoffice.models import Order

class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "backoffice/users/profile.html"
    success_message = "Perfil actualizado correctamente."
    
    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("backoffice:user_profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Mi Perfil"
        
        # Statistics
        user = self.request.user
        orders_query = Order.objects.filter(collected_by=user, status="PAID")
        
        sales_count = orders_query.count()
        sales_total = orders_query.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
        avg_ticket = sales_total / sales_count if sales_count > 0 else 0

        context["stats"] = {
            "sales_count": sales_count,
            "sales_total": sales_total,
            "avg_ticket": avg_ticket,
        }
        
        # Recent Activity (Last 5 orders)
        context["recent_orders"] = orders_query.order_by("-paid_at")[:5]
        
        return context
