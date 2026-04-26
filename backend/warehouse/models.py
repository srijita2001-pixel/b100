"""
Star schema models for financial data warehouse.
Dimension tables: Companies, Years, Sectors, Health Labels
Fact tables: ProfitLoss, BalanceSheet, CashFlow, Analysis, MLScores, ProsCons
"""
from django.db import models


class DimCompany(models.Model):
    """Company dimension - master data for all companies"""
    symbol = models.CharField(max_length=20, primary_key=True)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, null=True, blank=True)
    sub_sector = models.CharField(max_length=100, null=True, blank=True)
    company_logo = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    nse_url = models.URLField(null=True, blank=True)
    bse_url = models.URLField(null=True, blank=True)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    book_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    about_company = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dim_company'

    def __str__(self):
        return f"{self.symbol} - {self.company_name}"


class DimYear(models.Model):
    """Year dimension - standardized time periods"""
    year_id = models.AutoField(primary_key=True)
    year_label = models.CharField(max_length=20)  # e.g., 'Mar 2024', 'Q4 2024'
    fiscal_year = models.IntegerField()  # e.g., 2024
    quarter = models.CharField(max_length=5, null=True, blank=True)  # e.g., 'Q4', 'Q1'
    month = models.CharField(max_length=10, null=True, blank=True)  # e.g., 'Mar', 'Sep'
    is_ttm = models.BooleanField(default=False)  # Trailing Twelve Months
    is_half_year = models.BooleanField(default=False)  # H1, H2
    sort_order = models.IntegerField()  # For chronological ordering
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dim_year'
        ordering = ['sort_order']

    def __str__(self):
        return self.year_label


class DimSector(models.Model):
    """Sector dimension - industry classification"""
    sector_id = models.AutoField(primary_key=True)
    sector_name = models.CharField(max_length=100, unique=True)
    sector_code = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dim_sector'

    def __str__(self):
        return self.sector_name


class DimHealthLabel(models.Model):
    """Health label dimension - score categories"""
    label_id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=20)  # EXCELLENT, GOOD, AVERAGE, WEAK, POOR
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    color_hex = models.CharField(max_length=7)  # e.g., '#16a34a'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dim_health_label'

    def __str__(self):
        return self.label_name


class FactProfitLoss(models.Model):
    """Profit & Loss fact table - 1 row per company per year"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE)
    year = models.ForeignKey(DimYear, on_delete=models.CASCADE)
    
    # Core P&L metrics
    sales = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    expenses = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    operating_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    opm_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    other_income = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    interest = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    depreciation = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    profit_before_tax = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    tax_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    net_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    eps = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dividend_payout_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Computed columns
    net_profit_margin_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    expense_ratio_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    interest_coverage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_profit_loss'
        unique_together = ('company', 'year')

    def __str__(self):
        return f"{self.company.symbol} - {self.year.year_label}"


class FactBalanceSheet(models.Model):
    """Balance Sheet fact table - 1 row per company per year"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE)
    year = models.ForeignKey(DimYear, on_delete=models.CASCADE)
    
    # Assets
    fixed_assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    cwip = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    investments = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    other_assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Liabilities & Equity
    equity_capital = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    reserves = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    borrowings = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    other_liabilities = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_liabilities = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Computed columns
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    equity_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    book_value_per_share = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_balance_sheet'
        unique_together = ('company', 'year')

    def __str__(self):
        return f"{self.company.symbol} - {self.year.year_label}"


class FactCashFlow(models.Model):
    """Cash Flow fact table - 1 row per company per year"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE)
    year = models.ForeignKey(DimYear, on_delete=models.CASCADE)
    
    # Cash flow components
    operating_activity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    investing_activity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    financing_activity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    net_cash_flow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Computed columns
    free_cash_flow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    cash_conversion_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_cash_flow'
        unique_together = ('company', 'year')

    def __str__(self):
        return f"{self.company.symbol} - {self.year.year_label}"


class FactAnalysis(models.Model):
    """Multi-period analysis fact table - 1 row per company per period (10Y/5Y/3Y/TTM)"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE)
    period_label = models.CharField(max_length=10)  # '10Y', '5Y', '3Y', 'TTM'
    
    # Growth metrics
    compounded_sales_growth_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    compounded_profit_growth_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stock_price_cagr_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    roe_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_analysis'
        unique_together = ('company', 'period_label')

    def __str__(self):
        return f"{self.company.symbol} - {self.period_label}"


class FactMLScores(models.Model):
    """ML-generated health scores - 1 row per company per run"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE)
    
    # Overall score
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)
    health_label = models.ForeignKey(DimHealthLabel, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Component scores
    profitability_score = models.DecimalField(max_digits=5, decimal_places=2)
    growth_score = models.DecimalField(max_digits=5, decimal_places=2)
    leverage_score = models.DecimalField(max_digits=5, decimal_places=2)
    cashflow_score = models.DecimalField(max_digits=5, decimal_places=2)
    dividend_score = models.DecimalField(max_digits=5, decimal_places=2)
    trend_score = models.DecimalField(max_digits=5, decimal_places=2)
    
    computed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_ml_scores'

    def __str__(self):
        return f"{self.company.symbol} - Score: {self.overall_score}"


class FactProsCons(models.Model):
    """Pros and Cons insights for companies"""
    CATEGORY_CHOICES = [
        ('GROWTH', 'Growth'),
        ('PROFITABILITY', 'Profitability'),
        ('RISK', 'Risk'),
        ('DIVIDEND', 'Dividend'),
        ('MANAGEMENT', 'Management'),
        ('MARKET', 'Market Position'),
        ('OTHER', 'Other'),
    ]
    
    SOURCE_CHOICES = [
        ('MANUAL', 'Manual'),
        ('ML', 'Machine Learning'),
    ]
    
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE)
    is_pro = models.BooleanField()  # True = Pro, False = Con
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    text = models.TextField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    confidence = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fact_pros_cons'

    def __str__(self):
        return f"{'Pro' if self.is_pro else 'Con'} - {self.company.symbol}"
