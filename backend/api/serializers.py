"""
Django REST Framework serializers for financial data.
"""
from rest_framework import serializers
from warehouse.models import (
    DimCompany, DimYear, DimSector, DimHealthLabel,
    FactProfitLoss, FactBalanceSheet, FactCashFlow,
    FactAnalysis, FactMLScores, FactProsCons
)


class DimCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DimCompany
        fields = [
            'symbol', 'company_name', 'sector', 'sub_sector',
            'company_logo', 'website', 'nse_url', 'bse_url',
            'face_value', 'book_value', 'about_company', 'updated_at'
        ]


class DimYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimYear
        fields = [
            'year_id', 'year_label', 'fiscal_year', 'quarter',
            'month', 'is_ttm', 'is_half_year', 'sort_order'
        ]


class DimSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimSector
        fields = ['sector_id', 'sector_name', 'sector_code', 'description']


class DimHealthLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimHealthLabel
        fields = ['label_id', 'label_name', 'min_score', 'max_score', 'color_hex']


class FactProfitLossSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    year_label = serializers.CharField(source='year.year_label', read_only=True)
    
    class Meta:
        model = FactProfitLoss
        fields = [
            'id', 'company_symbol', 'company_name', 'year_label',
            'sales', 'expenses', 'operating_profit', 'opm_pct',
            'other_income', 'interest', 'depreciation', 'profit_before_tax',
            'tax_pct', 'net_profit', 'eps', 'dividend_payout_pct',
            'net_profit_margin_pct', 'expense_ratio_pct', 'interest_coverage',
            'updated_at'
        ]


class FactBalanceSheetSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    year_label = serializers.CharField(source='year.year_label', read_only=True)
    
    class Meta:
        model = FactBalanceSheet
        fields = [
            'id', 'company_symbol', 'company_name', 'year_label',
            'fixed_assets', 'cwip', 'investments', 'other_assets', 'total_assets',
            'equity_capital', 'reserves', 'borrowings', 'other_liabilities', 'total_liabilities',
            'debt_to_equity', 'equity_ratio', 'book_value_per_share',
            'updated_at'
        ]


class FactCashFlowSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    year_label = serializers.CharField(source='year.year_label', read_only=True)
    
    class Meta:
        model = FactCashFlow
        fields = [
            'id', 'company_symbol', 'company_name', 'year_label',
            'operating_activity', 'investing_activity', 'financing_activity',
            'net_cash_flow', 'free_cash_flow', 'cash_conversion_ratio',
            'updated_at'
        ]


class FactAnalysisSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = FactAnalysis
        fields = [
            'id', 'company_symbol', 'company_name', 'period_label',
            'compounded_sales_growth_pct', 'compounded_profit_growth_pct',
            'stock_price_cagr_pct', 'roe_pct', 'updated_at'
        ]


class FactMLScoresSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    health_label_name = serializers.CharField(source='health_label.label_name', read_only=True)
    
    class Meta:
        model = FactMLScores
        fields = [
            'id', 'company_symbol', 'company_name', 'overall_score',
            'health_label_name', 'profitability_score', 'growth_score',
            'leverage_score', 'cashflow_score', 'dividend_score', 'trend_score',
            'computed_at', 'updated_at'
        ]


class FactProsConsSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    
    class Meta:
        model = FactProsCons
        fields = [
            'id', 'company_symbol', 'is_pro', 'category', 'text',
            'source', 'confidence', 'generated_at'
        ]


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Extended company serializer with related data"""
    sector_name = serializers.CharField(source='sector', read_only=True)
    latest_profit_loss = serializers.SerializerMethodField()
    latest_balance_sheet = serializers.SerializerMethodField()
    latest_analysis = serializers.SerializerMethodField()
    health_scores = serializers.SerializerMethodField()
    
    class Meta:
        model = DimCompany
        fields = [
            'symbol', 'company_name', 'sector_name', 'sub_sector',
            'company_logo', 'website', 'nse_url', 'bse_url',
            'face_value', 'book_value', 'about_company',
            'latest_profit_loss', 'latest_balance_sheet',
            'latest_analysis', 'health_scores', 'updated_at'
        ]
    
    def get_latest_profit_loss(self, obj):
        try:
            pnl = FactProfitLoss.objects.filter(company=obj).latest('year__sort_order')
            return FactProfitLossSerializer(pnl).data
        except FactProfitLoss.DoesNotExist:
            return None
    
    def get_latest_balance_sheet(self, obj):
        try:
            bs = FactBalanceSheet.objects.filter(company=obj).latest('year__sort_order')
            return FactBalanceSheetSerializer(bs).data
        except FactBalanceSheet.DoesNotExist:
            return None
    
    def get_latest_analysis(self, obj):
        try:
            analysis = FactAnalysis.objects.filter(company=obj, period_label='TTM')
            if analysis.exists():
                return FactAnalysisSerializer(analysis.first()).data
            return None
        except FactAnalysis.DoesNotExist:
            return None
    
    def get_health_scores(self, obj):
        try:
            scores = FactMLScores.objects.filter(company=obj).latest('computed_at')
            return FactMLScoresSerializer(scores).data
        except FactMLScores.DoesNotExist:
            return None
