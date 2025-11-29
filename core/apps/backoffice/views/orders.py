from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django_filters.views import FilterView
from django.forms import inlineformset_factory
from django.contrib import messages
from core.mixins import BasePageMixin
from core.apps.backoffice.models import Order, OrderItem
from core.apps.backoffice.forms import OrderForm, OrderItemForm
from core.apps.backoffice.filters import OrderFilter


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)


class OrderListView(BasePageMixin, FilterView):
    model = Order
    template_name = "backoffice/orders/list.html"
    context_object_name = "orders"
    filterset_class = OrderFilter
    paginate_by = 10
    page_title = "Ordenes"
    permission_required = "backoffice.view_order"

    def get_queryset(self):
        return (
            Order.objects.select_related("created_by", "collected_by")
            .prefetch_related("items")
            .order_by("-created_at")
        )


class OrderCreateView(BasePageMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "backoffice/orders/form.html"
    success_url = reverse_lazy("backoffice:order_list")
    page_title = "Nueva Orden"
    permission_required = "backoffice.add_order"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["items"] = OrderItemFormSet(self.request.POST)
        else:
            data["items"] = OrderItemFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context["items"]
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user  # Assign current user
            self.object.save()
            
            if items.is_valid():
                items.instance = self.object
                items.save()
                # Calculate total amount logic here if needed, or trust frontend/signals
                # For now, let's update total based on items
                total = sum(item.subtotal for item in self.object.items.all())
                self.object.total_amount = total
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, "Orden creada exitosamente.")
        return redirect(self.success_url)


class OrderUpdateView(BasePageMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "backoffice/orders/form.html"
    success_url = reverse_lazy("backoffice:order_list")
    page_title = "Editar Orden"
    permission_required = "backoffice.change_order"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["items"] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            data["items"] = OrderItemFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context["items"]
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.save()
                # Update total
                total = sum(item.subtotal for item in self.object.items.all())
                self.object.total_amount = total
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, "Orden actualizada exitosamente.")
        return redirect(self.success_url)


class OrderDeleteView(BasePageMixin, DeleteView):
    model = Order
    template_name = "backoffice/orders/delete.html"
    success_url = reverse_lazy("backoffice:order_list")
    permission_required = "backoffice.delete_order"
