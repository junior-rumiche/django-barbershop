from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.apps import apps
from core.apps.backoffice.models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "price", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del servicio"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción detallada",
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "price": "Precio",
            "status": "Activo",
        }


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
