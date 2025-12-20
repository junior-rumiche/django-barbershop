from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.apps import apps
from core.apps.backoffice.models import Category, Product, Order, OrderItem, SupplyEntry, BarberProfile, WorkSchedule, Appointment


class SupplyEntryForm(forms.ModelForm):
    class Meta:
        model = SupplyEntry
        fields = ["product", "quantity", "unit_cost", "supplier"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select choices"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0"}
            ),
            "unit_cost": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "supplier": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del proveedor"}
            ),
        }
        labels = {
            "product": "Producto",
            "quantity": "Cantidad",
            "unit_cost": "Costo Unitario",
            "supplier": "Proveedor",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos (no servicios)
        self.fields['product'].queryset = Product.objects.filter(is_service=False).order_by('name')

        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["client_name", "status"]
        widgets = {
            "client_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Cliente Ocasional"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "client_name": "Cliente",
            "status": "Estado",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select product-select"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control quantity-input", "min": "1"}
            ),
            "unit_price": forms.NumberInput(
                attrs={"class": "form-control price-input", "readonly": "readonly"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        if product and quantity:
            if not product.is_service and product.stock_qty < quantity:
                self.add_error(
                    "quantity", f"Stock insuficiente. Disponible: {product.stock_qty}."
                )
        return cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "price",
            "cost",
            "is_service",
            "duration",
            "stock_qty",
            "min_stock_alert",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del producto"}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "cost": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "is_service": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
            "duration": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "30"}
            ),
            "stock_qty": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0"}
            ),
            "min_stock_alert": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "5"}
            ),
        }
        labels = {
            "name": "Nombre",
            "category": "Categoría",
            "price": "Precio Venta",
            "cost": "Costo Compra",
            "is_service": "¿Es Servicio?",
            "duration": "Duración (min)",
            "stock_qty": "Stock Actual",
            "min_stock_alert": "Alerta Stock Mínimo",
        }
        error_messages = {
            "name": {
                "unique": "Ya existe un producto con este nombre.",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la categoría"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción detallada",
                }
            ),
            "status": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
        }
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "status": "Activo",
        }
        error_messages = {
            "name": {
                "unique": "Ya existe una categoría con este nombre.",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Contraseña"}
        ),
        required=False,
        label="Contraseña",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirmar Contraseña"}
        ),
        required=False,
        label="Confirmar Contraseña",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de usuario"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombres"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellidos"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Correo electrónico"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "groups": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "username": "Usuario",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Email",
            "is_active": "Activo",
            "is_staff": "Staff",
            "is_superuser": "Superusuario",
            "groups": "Grupos",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            self.add_error("password_confirm", "Las contraseñas no coinciden.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()  # Important for saving groups
        return user


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "permissions"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del grupo"}
            ),
            "permissions": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "name": "Nombre",
            "permissions": "Permisos",
        }

    def get_grouped_permissions(self):
        """
        Returns permissions grouped by ContentType (App | Model).
        Maps the form's bound widgets to the correct structure.
        """
        widgets = {}
        for widget in self["permissions"]:
            widgets[int(str(widget.data["value"]))] = widget

        perms = Permission.objects.select_related("content_type").order_by(
            "content_type__app_label", "content_type__model", "codename"
        )

        grouped = {}
        for p in perms:
            app_label = p.content_type.app_label
            try:
                app_config = apps.get_app_config(app_label)
                app_verbose = app_config.verbose_name
            except LookupError:
                app_verbose = app_label.title()

            model_class = p.content_type.model_class()
            if model_class:
                model_verbose = model_class._meta.verbose_name
            else:
                model_verbose = p.content_type.name

            label = f"{app_verbose} | {model_verbose.title()}"

            if label not in grouped:
                grouped[label] = []

            if p.id in widgets:
                widget = widgets[p.id]

                codename = p.codename
                perm_label = p.name

                if model_class:
                    model_name_lower = model_verbose.lower()
                    if codename.startswith("add_"):
                        perm_label = f"Agregar {model_name_lower}"
                    elif codename.startswith("change_"):
                        perm_label = f"Editar {model_name_lower}"
                    elif codename.startswith("delete_"):
                        perm_label = f"Eliminar {model_name_lower}"
                    elif codename.startswith("view_"):
                        perm_label = f"Ver {model_name_lower}"

                widget.custom_label = perm_label
                grouped[label].append(widget)

        return grouped.items()


class BarberProfileForm(forms.ModelForm):
    class Meta:
        model = BarberProfile
        fields = ["user", "nickname", "photo", "is_active"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select choices"}),
            "nickname": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apodo"}
            ),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
        }
        labels = {
            "user": "Usuario",
            "nickname": "Apodo",
            "photo": "Foto",
            "is_active": "Disponible en Web",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = [
            "day_of_week",
            "start_hour",
            "end_hour",
            "lunch_start",
            "lunch_end",
        ]
        field_classes = {
            'lunch_start': forms.TimeField,
            'lunch_end': forms.TimeField,
        }
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "form-select"}),
            "start_hour": forms.TextInput(
                attrs={"class": "form-control flatpickr-time h-100", "placeholder": "09:00 AM"}
            ),
            "end_hour": forms.TextInput(
                attrs={"class": "form-control flatpickr-time h-100", "placeholder": "05:00 PM"}
            ),
            "lunch_start": forms.TextInput(
                attrs={"class": "form-control flatpickr-time h-100", "placeholder": "01:00 PM"}
            ),
            "lunch_end": forms.TextInput(
                attrs={"class": "form-control flatpickr-time h-100", "placeholder": "02:00 PM"}
            ),
        }
        labels = {
            "day_of_week": "Día",
            "start_hour": "Entrada",
            "end_hour": "Salida",
            "lunch_start": "Inicio Refrigerio",
            "lunch_end": "Fin Refrigerio",
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_hour")
        end = cleaned_data.get("end_hour")
        lunch_start = cleaned_data.get("lunch_start")
        lunch_end = cleaned_data.get("lunch_end")
        
        if start and end and start >= end:
            self.add_error("end_hour", "La hora de salida debe ser posterior a la de entrada.")

        if lunch_start and lunch_end:
            if lunch_start >= lunch_end:
                self.add_error("lunch_end", "El fin de refrigerio debe ser posterior al inicio.")
            if start and lunch_start < start:
                self.add_error("lunch_start", "El refrigerio no puede iniciar antes de la entrada.")
            
            if end and lunch_end > end:
                self.add_error("lunch_end", "El refrigerio no puede terminar después de la salida.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lunch_start'].required = False
        self.fields['lunch_end'].required = False
        
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class BaseWorkScheduleFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        days = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            
            day = form.cleaned_data.get("day_of_week")
            if day in days:
                form.add_error("day_of_week", "Este día ya está registrado.")
            elif day is not None:
                days.append(day)


WorkScheduleFormSet = forms.inlineformset_factory(
    BarberProfile,
    WorkSchedule,
    form=WorkScheduleForm,
    formset=BaseWorkScheduleFormSet,
    extra=7, 
    can_delete=True,
)


WorkScheduleUpdateFormSet = forms.inlineformset_factory(
    BarberProfile,
    WorkSchedule,
    form=WorkScheduleForm,
    formset=BaseWorkScheduleFormSet,
    extra=7,
    max_num=7,
    can_delete=True,
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo Electrónico",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        ):
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "client_name",
            "client_phone",
            "barber",
            "services",
            "date",
            "start_time",
            "end_time",
            "total_amount",
            "status",
        ]
        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "client_phone": forms.TextInput(attrs={"class": "form-control"}),
            "barber": forms.Select(attrs={"class": "form-select choices"}),
            "services": forms.SelectMultiple(attrs={"class": "form-select choices multiple-remove"}),
            "date": forms.TextInput(attrs={"class": "form-control flatpickr-date", "placeholder": "YYYY-MM-DD"}),
            "start_time": forms.TextInput(attrs={"class": "form-control flatpickr-time", "placeholder": "HH:MM"}),
            "end_time": forms.TextInput(attrs={"class": "form-control flatpickr-time", "placeholder": "HH:MM"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "client_name": "Nombre Cliente",
            "client_phone": "Teléfono / WhatsApp",
            "barber": "Barbero",
            "services": "Servicios",
            "date": "Fecha",
            "start_time": "Hora Inicio",
            "end_time": "Hora Fin",
            "total_amount": "Total Estimado",
            "status": "Estado",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter services to only show products marked as is_service=True
        self.fields['services'].queryset = Product.objects.filter(is_service=True)
        
        for field_name in self.errors:
            if field_name in self.fields:
                current_class = self.fields[field_name].widget.attrs.get("class", "")
                if "is-invalid" not in current_class:
                    self.fields[field_name].widget.attrs[
                        "class"
                    ] = f"{current_class} is-invalid".strip()