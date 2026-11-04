# Django

Django is Python's batteries-included full-stack web framework — [ORM](../../backend/data/orm.md), migrations, admin panel, built-in auth, template engine, form handling, and a development server all ship with the framework. WSGI-based and synchronous by default, with async view support added in Django 3.1 and async [ORM](../../backend/data/orm.md) operations added incrementally (still limited relative to a pure async [ORM](../../backend/data/orm.md)). When you also need a [REST](../../backend/api/rest.md) API layer, Django [REST](../../backend/api/rest.md) Framework (DRF) adds serializers, viewsets, routers, and browsable API tooling on top. Choose Django when you need the full stack; choose [FastAPI](fastapi.md) when building a pure API or microservice. See [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) for a full comparison.

## Core Concepts

| Term | Meaning |
|---|---|
| **Project** | The top-level Django package — `settings.py`, `urls.py`, `wsgi.py`/`asgi.py`; one project hosts multiple apps |
| **App** | A self-contained module inside a project — models, views, URLs, admin registration, migrations all live per-app |
| **Model** | A Python class inheriting `django.db.models.Model` — each field maps to a DB column; Django generates migration files from model changes |
| **Migration** | Auto-generated Python file that applies model changes to the DB schema — `makemigrations` creates them, `migrate` runs them |
| **View** | A function or class that receives an `HttpRequest` and returns an `HttpResponse` — can render a template or return [JSON](../fundamentals/json.md) |
| **URL conf** | `urls.py` — list of `path()` or `re_path()` entries mapping URL patterns to views |
| **Admin** | `django.contrib.admin` — auto-generates a CRUD management interface for all registered models at `/admin` |
| **QuerySet** | Lazy, chainable DB query object — `User.objects.filter(active=True).order_by("-created_at")` |
| **DRF Serializer** | Django [REST](../../backend/api/rest.md) Framework class that validates incoming data and serializes model instances to/from [JSON](../fundamentals/json.md) — the DRF equivalent of [Pydantic](pydantic.md) models in [FastAPI](fastapi.md) |

## Installation

```bash
pip install django djangorestframework
django-admin startproject myproject .
python manage.py startapp orders
python manage.py migrate          # applies initial migrations
python manage.py createsuperuser
python manage.py runserver
```

## Defining a Model and Migrating

```python
# orders/models.py
from django.db import models

class Order(models.Model):
    item = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
```

```bash
python manage.py makemigrations orders   # generates migrations/0001_initial.py
python manage.py migrate                 # applies it to the DB
```

## A DRF API Endpoint

```python
# orders/serializers.py
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "item", "quantity", "created_at"]


# orders/views.py
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


# orders/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r"orders", OrderViewSet)
urlpatterns = router.urls
```

This one `ModelViewSet` + `ModelSerializer` pair gives you GET list, GET detail, POST, PUT, PATCH, DELETE — and a browsable HTML API at `/api/orders/` in development.

## The Admin Panel

```python
# orders/admin.py
from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "item", "quantity", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["item"]
```

Navigate to `/admin` after `createsuperuser` — a full CRUD interface for all registered models, zero front-end code required.

## Async Views (Django 3.1+)

```python
# views.py
from django.http import JsonResponse
import httpx

async def fetch_external(request):
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.example.com/data")
    return JsonResponse(resp.json())
```

Django async views require an [ASGI](../../backend/architecture/asgi.md) server (Uvicorn or Daphne) instead of the default WSGI runner. The [ORM](../../backend/data/orm.md) is still sync by default; use `sync_to_async` to wrap [ORM](../../backend/data/orm.md) calls inside async views if needed.

## FastAPI vs Django Summary

| | Django + DRF | [FastAPI](fastapi.md) |
|---|---|---|
| [ORM](../../backend/data/orm.md) | Built-in Django ORM | Bring your own (SQLAlchemy, Tortoise) |
| Admin panel | Built-in `/admin` | None |
| Auth | Built-in session auth + django-allauth | Bring your own ([JWT](../../security/auth/jwt.md), OAuth) |
| Migrations | Built-in `makemigrations` | Alembic (SQLAlchemy) or Prisma |
| Validation | DRF Serializers (explicit class per endpoint) | [Pydantic](pydantic.md) (automatic from type hints) |
| [OpenAPI](../../backend/api/openapi.md) docs | drf-spectacular or manually configured | Auto-generated at `/docs` |
| Async | Partial (async views; ORM mostly sync) | Native [ASGI](../../backend/architecture/asgi.md) |

## When to Use Django

- Enterprise web application needing full stack: data model + admin + auth + content management
- CMS or back-office tool where the auto-admin pays off
- Team already fluent in Django with existing models and migrations
- SaaS product where you want ORM + migrations + auth built in from day one

## When to Use Something Else

- Pure API service or microservice — use [FastAPI](fastapi.md)
- High-concurrency async API ([LLM](../../ai/generation/llm.md) calls, streaming) — use [FastAPI](fastapi.md)
- Minimal prototype with no data model — use [Flask](flask.md)

## Related

- [FastAPI](fastapi.md) — async-native API framework; pure API alternative to Django + DRF
- [Flask](flask.md) — minimal micro-framework without ORM or admin
- [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) — comparison overview
- [Python Overview](../../../overviews/programming/python-overview.md)
- [Dependency Injection](../fundamentals/dependency-injection.md)
- [Pydantic](pydantic.md) — contrast with DRF serializers: [Pydantic](pydantic.md) derives schema from type hints; DRF serializers are explicit class definitions
