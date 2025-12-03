from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, View
from django_filters.views import FilterView
from django.forms import inlineformset_factory
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

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


class OrderPrintView(BasePageMixin, View):
    permission_required = "backoffice.can_print_order"

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="orden_{order.pk}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        # --- Configuration ---
        # Colors
        color_primary = colors.HexColor("#1a1a1a") # Almost black
        color_secondary = colors.HexColor("#555555") # Dark Gray
        color_accent = colors.HexColor("#435ebe") # Brand Blue-ish
        color_bg_light = colors.HexColor("#f8f9fa") # Light Gray BG
        color_line = colors.HexColor("#e0e0e0") # Light Line
        
        # Status Colors
        status_colors = {
            'PAID': colors.HexColor("#28a745"),     # Green
            'PENDING': colors.HexColor("#ffc107"),  # Orange
            'CANCELED': colors.HexColor("#dc3545")  # Red
        }
        status_labels = {
            'PAID': 'PAGADO',
            'PENDING': 'PENDIENTE',
            'CANCELED': 'ANULADO'
        }

        # Helpers
        def draw_right(c, x, y, text, font="Helvetica", size=10, color=color_primary):
            c.setFont(font, size)
            c.setFillColor(color)
            w = c.stringWidth(text, font, size)
            c.drawString(x - w, y, text)

        def draw_center(c, x, y, text, font="Helvetica", size=10, color=color_primary):
            c.setFont(font, size)
            c.setFillColor(color)
            c.drawCentredString(x, y, text)

        # --- Watermark ---
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
        if os.path.exists(logo_path):
            p.saveState()
            p.setFillAlpha(0.08)
            wm_size = width * 0.5
            p.drawImage(logo_path, (width - wm_size)/2, (height - wm_size)/2, 
                        width=wm_size, height=wm_size, mask='auto', preserveAspectRatio=True, anchor='c')
            p.restoreState()

        # --- Header Section ---
        # Logo (Top Left)
        if os.path.exists(logo_path):
            p.drawImage(logo_path, 40, height - 90, width=50, height=50, mask='auto', preserveAspectRatio=True)
        
        # Brand
        p.setFont("Helvetica-Bold", 20)
        p.setFillColor(color_primary)
        p.drawString(100, height - 60, "4 Pelos Club Barbers")
        p.setFont("Helvetica-Oblique", 10)
        p.setFillColor(color_secondary)
        p.drawString(100, height - 75, "Barbería & Estilo")

        # Right Header Block (Status + Order Info)
        # Status Badge
        status_key = order.status
        badge_color = status_colors.get(status_key, colors.gray)
        badge_text = status_labels.get(status_key, status_key)
        
        # Badge Rect
        p.setFillColor(badge_color)
        p.roundRect(width - 140, height - 55, 100, 20, 4, stroke=0, fill=1)
        draw_center(p, width - 90, height - 48, badge_text, "Helvetica-Bold", 10, colors.white)
        
        # Order Meta
        draw_right(p, width - 40, height - 75, f"Nº DE ORDEN: {order.pk:06d}", "Helvetica-Bold", 10, color_primary)
        draw_right(p, width - 40, height - 88, f"Fecha: {order.created_at.strftime('%d/%m/%Y')}", "Helvetica", 9, color_secondary)
        draw_right(p, width - 40, height - 100, f"Hora: {order.created_at.strftime('%I:%M %p')}", "Helvetica", 9, color_secondary)

        # --- Info Section (Boxed) ---
        # Adjusted y position to avoid overlap with header
        y_info_box = height - 170
        box_height = 50
        
        # Background Box
        p.setFillColor(color_bg_light)
        p.setStrokeColor(color_line)
        p.roundRect(40, y_info_box, width - 80, box_height, 6, stroke=1, fill=1)
        
        # Client Info
        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(color_secondary)
        p.drawString(55, y_info_box + 30, "CLIENTE")
        p.setFont("Helvetica", 11)
        p.setFillColor(color_primary)
        p.drawString(55, y_info_box + 15, order.client_name)
        
        # Vertical Separator
        p.setStrokeColor(color_line)
        p.line(width/2, y_info_box + 10, width/2, y_info_box + 40)
        
        # Staff Info
        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(color_secondary)
        p.drawString((width/2) + 15, y_info_box + 30, "ATENDIDO POR")
        staff_name = order.created_by.get_full_name() or order.created_by.username
        p.setFont("Helvetica", 11)
        p.setFillColor(color_primary)
        p.drawString((width/2) + 15, y_info_box + 15, staff_name)

        # --- Table Section ---
        y_table = y_info_box - 30
        
        # Header Background
        p.setFillColor(colors.HexColor("#eeeeee"))
        p.rect(40, y_table, width - 80, 20, stroke=0, fill=1)
        
        # Header Labels
        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(color_primary)
        p.drawString(50, y_table + 6, "DESCRIPCIÓN")
        draw_center(p, 350, y_table + 6, "CANT.")
        draw_right(p, 450, y_table + 6, "P. UNIT")
        draw_right(p, 540, y_table + 6, "TOTAL")
        
        # Items
        y_row = y_table - 25
        p.setFont("Helvetica", 10)
        
        for item in order.items.all():
            p.setFillColor(color_primary)
            p.drawString(50, y_row, str(item.product.name)[:45])
            draw_center(p, 350, y_row, str(item.quantity))
            draw_right(p, 450, y_row, f"S/ {item.unit_price:.2f}")
            draw_right(p, 540, y_row, f"S/ {item.subtotal:.2f}")
            
            # Separator Line
            p.setStrokeColor(color_line)
            p.setLineWidth(0.5)
            p.line(40, y_row - 8, width - 40, y_row - 8)
            
            y_row -= 25
            
            if y_row < 100:
                p.showPage()
                y_row = height - 50

        # --- Totals Section ---
        y_total = y_row - 15
        
        # Total Box/Line
        # p.setFillColor(color_bg_light)
        # p.roundRect(width - 200, y_total - 10, 160, 35, 4, stroke=0, fill=1)
        
        p.setFont("Helvetica-Bold", 12)
        draw_right(p, 450, y_total, "TOTAL A PAGAR:", color=color_secondary)
        
        p.setFont("Helvetica-Bold", 16)
        draw_right(p, 540, y_total - 2, f"S/ {order.total_amount:.2f}", size=16, color=color_primary)

        # --- Footer ---
        # Line
        p.setStrokeColor(color_line)
        p.setLineWidth(1)
        p.line(40, 60, width - 40, 60)
        
        draw_center(p, width/2, 40, "¡Gracias por tu preferencia!", "Helvetica-Oblique", 10, color_secondary)
        
        # Print Timestamp
        from django.utils import timezone
        now = timezone.localtime(timezone.now())
        draw_center(p, width/2, 25, f"Impreso el {now.strftime('%d/%m/%Y %H:%M')}", "Helvetica", 7, colors.gray)
        
        p.showPage()
        p.save()
        return response
