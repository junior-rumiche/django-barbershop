from django.views.generic import TemplateView
from django.db.models import Sum, Count, F, Avg
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta
import json

from django.contrib.auth.models import User
from core.mixins import BasePageMixin
from core.apps.backoffice.models import Order, Product, OrderItem


class DashboardView(BasePageMixin, TemplateView):
    template_name = "backoffice/dashboard.html"
    page_title = "Dashboard"
    permission_required = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use local date instead of UTC date
        today = timezone.localtime(timezone.now()).date()
        last_7_days = today - timedelta(days=6)

        # --- Summary Cards Data ---
        # Total Sales Today (Paid orders)
        total_sales_today = Order.objects.filter(
            status='PAID',
            paid_at__date=today
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Orders Today (All created today)
        orders_today_count = Order.objects.filter(
            created_at__date=today
        ).count()

        # Pending Orders
        pending_orders_count = Order.objects.filter(status='PENDING').count()

        # Low Stock Products (Only for non-services)
        low_stock_count = Product.objects.filter(
            is_service=False,
            stock_qty__lte=F('min_stock_alert')
        ).count()
        
        # Average Ticket (This Month)
        this_month_orders = Order.objects.filter(
            status='PAID',
            paid_at__month=today.month,
            paid_at__year=today.year
        )
        avg_ticket = this_month_orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0

        # Total Inventory Value (Cost * Stock)
        inventory_value = Product.objects.filter(
            is_service=False
        ).aggregate(
            total_value=Sum(F('cost') * F('stock_qty'))
        )['total_value'] or 0

        context['stats'] = {
            'sales_today': total_sales_today,
            'orders_today': orders_today_count,
            'pending_orders': pending_orders_count,
            'low_stock': low_stock_count,
            'avg_ticket': f"{avg_ticket:.2f}",
            'inventory_value': f"{inventory_value:.2f}",
        }

        # --- Chart Data: Sales Last 7 Days ---
        sales_data = []
        dates = []
        for i in range(7):
            date = last_7_days + timedelta(days=i)
            daily_sales = Order.objects.filter(
                status='PAID',
                paid_at__date=date
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            sales_data.append(float(daily_sales))
            dates.append(date.strftime("%d/%m"))

        context['chart_sales'] = json.dumps({
            'series': [{'name': 'Ventas', 'data': sales_data}],
            'categories': dates
        })
        
        # --- Chart Data: Services vs Products (This Month) ---
        services_sales = OrderItem.objects.filter(
            order__status='PAID',
            order__paid_at__month=today.month,
            order__paid_at__year=today.year,
            product__is_service=True
        ).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        
        products_sales = OrderItem.objects.filter(
            order__status='PAID',
            order__paid_at__month=today.month,
            order__paid_at__year=today.year,
            product__is_service=False
        ).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        
        context['chart_mix'] = json.dumps({
            'series': [float(services_sales), float(products_sales)],
            'labels': ['Servicios', 'Productos']
        })
        
        # --- Chart Data: Peak Hours (Activity Heatmap equivalent) ---
        # Initialize 24 hours with 0
        hours_data = [0] * 24
        orders_by_hour = Order.objects.annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        for item in orders_by_hour:
            # ExtractHour can return None if date is null (shouldn't happen for created_at)
            if item['hour'] is not None and 0 <= item['hour'] < 24:
                hours_data[item['hour']] = item['count']

        context['chart_peak_hours'] = json.dumps({
            'series': [{'name': 'Transacciones', 'data': hours_data}],
            'categories': [f"{h:02d}:00" for h in range(24)]
        })

        # --- Chart Data: Order Status Distribution ---
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        status_map = {item['status']: item['count'] for item in status_counts}
        
        # Ensure fixed order for colors: Paid, Pending, Canceled
        status_series = [
            status_map.get('PAID', 0),
            status_map.get('PENDING', 0),
            status_map.get('CANCELED', 0)
        ]
        
        context['chart_status'] = json.dumps({
            'series': status_series,
            'labels': ['Pagado', 'Pendiente', 'Anulado']
        })

        # --- Recent Orders ---
        context['recent_orders'] = Order.objects.select_related('created_by').order_by('-created_at')[:5]

        # --- Top Selling Products (All time) ---
        top_products = OrderItem.objects.filter(
            order__status='PAID'
        ).values('product__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        context['top_products'] = top_products
        
        # --- Top Staff (By Sales Amount - This Month) ---
        top_staff = Order.objects.filter(
            status='PAID',
            paid_at__month=today.month,
            paid_at__year=today.year
        ).values('created_by__username', 'created_by__first_name', 'created_by__last_name').annotate(
            total_sales=Sum('total_amount'),
            orders_count=Count('id')
        ).order_by('-total_sales')[:5]
        
        # Format for display
        top_staff = list(top_staff)
        for staff in top_staff:
            staff['total_sales'] = f"{staff['total_sales']:.2f}"
        
        context['top_staff'] = top_staff
        
        # --- Sales by Category (All Time) ---
        sales_by_category = OrderItem.objects.filter(
            order__status='PAID'
        ).values('product__category__name').annotate(
            total_sales=Sum('subtotal'),
            items_sold=Sum('quantity')
        ).order_by('-total_sales')[:5]
        
        # Format for display
        sales_by_category = list(sales_by_category)
        for cat in sales_by_category:
            cat['total_sales'] = f"{cat['total_sales']:.2f}"
        
        context['sales_by_category'] = sales_by_category

        return context
