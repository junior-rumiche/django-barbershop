from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from django.contrib.auth.decorators import login_required


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard:home")
        else:
            return render(
                request, "login.html", {"error": "Usuario o contraseña inválidos"}
            )
