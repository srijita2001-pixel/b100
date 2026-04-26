"""
URL configuration for financial_warehouse project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from api.views import (
    CompanyViewSet, AnalysisViewSet, BalanceSheetViewSet,
    ProfitLossViewSet, CashFlowViewSet, HealthScoreViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'analysis', AnalysisViewSet)
router.register(r'balance-sheet', BalanceSheetViewSet)
router.register(r'profit-loss', ProfitLossViewSet)
router.register(r'cash-flow', CashFlowViewSet)
router.register(r'health-scores', HealthScoreViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
