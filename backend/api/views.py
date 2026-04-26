"""
Django REST Framework viewsets for financial data.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from warehouse.models import (
    DimCompany, DimYear, DimSector, DimHealthLabel,
    FactProfitLoss, FactBalanceSheet, FactCashFlow,
    FactAnalysis, FactMLScores, FactProsCons
)
from api.serializers import (
    DimCompanySerializer, DimYearSerializer, DimSectorSerializer,
    FactProfitLossSerializer, FactBalanceSheetSerializer, FactCashFlowSerializer,
    FactAnalysisSerializer, FactMLScoresSerializer, FactProsConsSerializer,
    CompanyDetailSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for company master data.
    
    Actions:
    - GET /api/companies/ - List all companies with pagination
    - GET /api/companies/{symbol}/ - Get company detail with related data
    - GET /api/companies/search/?q=term - Search companies by name
    - GET /api/companies/{symbol}/analysis/ - Get multi-period analysis
    - GET /api/companies/{symbol}/health-score/ - Get ML health score
    - GET /api/companies/{symbol}/pros-cons/ - Get pros and cons
    """
    queryset = DimCompany.objects.all()
    serializer_class = DimCompanySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol', 'company_name', 'sector']
    ordering_fields = ['symbol', 'company_name', 'sector']
    ordering = ['symbol']
    lookup_field = 'symbol'
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return DimCompanySerializer
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, symbol=None):
        """Get multi-period analysis for a company"""
        company = self.get_object()
        analysis = FactAnalysis.objects.filter(company=company).order_by('period_label')
        serializer = FactAnalysisSerializer(analysis, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def health_score(self, request, symbol=None):
        """Get latest ML health score"""
        company = self.get_object()
        try:
            score = FactMLScores.objects.filter(company=company).latest('computed_at')
            serializer = FactMLScoresSerializer(score)
            return Response(serializer.data)
        except FactMLScores.DoesNotExist:
            return Response({'detail': 'No health score found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def pros_cons(self, request, symbol=None):
        """Get pros and cons insights"""
        company = self.get_object()
        insights = FactProsCons.objects.filter(company=company)
        serializer = FactProsConsSerializer(insights, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def financial_data(self, request, symbol=None):
        """Get comprehensive financial data (P&L, BS, CF) for a company"""
        company = self.get_object()
        
        # Get last 5 years of data
        years = DimYear.objects.filter(is_ttm=False).order_by('-sort_order')[:5]
        
        pnl_data = FactProfitLoss.objects.filter(
            company=company, year__in=years
        ).order_by('year__sort_order')
        
        bs_data = FactBalanceSheet.objects.filter(
            company=company, year__in=years
        ).order_by('year__sort_order')
        
        cf_data = FactCashFlow.objects.filter(
            company=company, year__in=years
        ).order_by('year__sort_order')
        
        return Response({
            'company_symbol': company.symbol,
            'company_name': company.company_name,
            'profit_loss': FactProfitLossSerializer(pnl_data, many=True).data,
            'balance_sheet': FactBalanceSheetSerializer(bs_data, many=True).data,
            'cash_flow': FactCashFlowSerializer(cf_data, many=True).data,
        })


class AnalysisViewSet(viewsets.ModelViewSet):
    """
    API endpoint for multi-period growth analysis.
    Filter by period_label: 10Y, 5Y, 3Y, TTM
    """
    queryset = FactAnalysis.objects.all()
    serializer_class = FactAnalysisSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company__symbol', 'company__company_name', 'period_label']
    ordering_fields = ['company__symbol', 'period_label']
    ordering = ['company__symbol', 'period_label']
    
    @action(detail=False, methods=['get'])
    def by_period(self, request):
        """Get analysis data for a specific period across all companies"""
        period = request.query_params.get('period', 'TTM')
        data = FactAnalysis.objects.filter(period_label=period).order_by('company__symbol')
        serializer = FactAnalysisSerializer(data, many=True)
        return Response({
            'period': period,
            'count': len(data),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        """Get top 10 companies by growth metrics"""
        period = request.query_params.get('period', 'TTM')
        metric = request.query_params.get('metric', 'compounded_sales_growth_pct')
        
        data = FactAnalysis.objects.filter(
            period_label=period
        ).order_by(f'-{metric}')[:10]
        
        serializer = FactAnalysisSerializer(data, many=True)
        return Response({
            'period': period,
            'metric': metric,
            'data': serializer.data
        })


class BalanceSheetViewSet(viewsets.ModelViewSet):
    """API endpoint for balance sheet data"""
    queryset = FactBalanceSheet.objects.all()
    serializer_class = FactBalanceSheetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company__symbol', 'company__company_name']
    ordering_fields = ['company__symbol', 'year__sort_order']
    ordering = ['-year__sort_order']
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """Get balance sheet data for a specific company"""
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'error': 'symbol parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = FactBalanceSheet.objects.filter(
            company__symbol=symbol
        ).order_by('-year__sort_order')
        
        serializer = FactBalanceSheetSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def debt_analysis(self, request):
        """Get debt-to-equity analysis across companies"""
        latest_year = DimYear.objects.filter(is_ttm=False).latest('sort_order')
        
        data = FactBalanceSheet.objects.filter(
            year=latest_year
        ).order_by('-debt_to_equity')
        
        serializer = FactBalanceSheetSerializer(data, many=True)
        return Response({
            'year': latest_year.year_label,
            'metric': 'debt_to_equity',
            'data': serializer.data
        })


class ProfitLossViewSet(viewsets.ModelViewSet):
    """API endpoint for profit & loss data"""
    queryset = FactProfitLoss.objects.all()
    serializer_class = FactProfitLossSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company__symbol', 'company__company_name']
    ordering_fields = ['company__symbol', 'year__sort_order', 'net_profit_margin_pct']
    ordering = ['-year__sort_order']
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """Get P&L data for a specific company"""
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'error': 'symbol parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = FactProfitLoss.objects.filter(
            company__symbol=symbol
        ).order_by('-year__sort_order')
        
        serializer = FactProfitLossSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def margin_analysis(self, request):
        """Get net profit margin analysis"""
        latest_year = DimYear.objects.filter(is_ttm=False).latest('sort_order')
        
        data = FactProfitLoss.objects.filter(
            year=latest_year
        ).order_by('-net_profit_margin_pct')
        
        serializer = FactProfitLossSerializer(data, many=True)
        return Response({
            'year': latest_year.year_label,
            'metric': 'net_profit_margin_pct',
            'data': serializer.data
        })


class CashFlowViewSet(viewsets.ModelViewSet):
    """API endpoint for cash flow data"""
    queryset = FactCashFlow.objects.all()
    serializer_class = FactCashFlowSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company__symbol', 'company__company_name']
    ordering_fields = ['company__symbol', 'year__sort_order', 'free_cash_flow']
    ordering = ['-year__sort_order']
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """Get cash flow data for a specific company"""
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'error': 'symbol parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = FactCashFlow.objects.filter(
            company__symbol=symbol
        ).order_by('-year__sort_order')
        
        serializer = FactCashFlowSerializer(data, many=True)
        return Response(serializer.data)


class HealthScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for ML-generated health scores"""
    queryset = FactMLScores.objects.all()
    serializer_class = FactMLScoresSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company__symbol', 'company__company_name']
    ordering_fields = ['company__symbol', 'overall_score']
    ordering = ['-overall_score']
    
    @action(detail=False, methods=['get'])
    def rankings(self, request):
        """Get top-ranked companies by health score"""
        limit = int(request.query_params.get('limit', 20))
        
        data = FactMLScores.objects.order_by('-overall_score')[:limit]
        serializer = FactMLScoresSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_sector(self, request):
        """Get average health score by sector"""
        from django.db.models import Avg
        
        data = FactMLScores.objects.values(
            sector_name=Q('company__sector')
        ).annotate(
            avg_score=Avg('overall_score'),
            count=models.Count('id')
        ).order_by('-avg_score')
        
        return Response(data)
