import importlib
import django
from django.conf import settings

django.setup()

print("BASE_DIR:", settings.BASE_DIR)

print("\nINSTALLED_APPS (nome → arquivo origem):")
for app in settings.INSTALLED_APPS:
    try:
        mod = importlib.import_module(app)
        path = getattr(mod, "__file__", "(sem __file__)")
        print(f"- {app:40s} → {path}")
    except Exception as e:
        print(f"- {app:40s} → ERRO: {e}")

print("\nExiste pacote 'escola_no_ar'?")
try:
    m = importlib.import_module("escola_no_ar")
    print("✔ escola_no_ar:", getattr(m, "__file__", "(sem __file__)"))
except Exception as e:
    print("✘ escola_no_ar:", e)
