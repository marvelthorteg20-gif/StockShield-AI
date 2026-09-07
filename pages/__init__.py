"""v2 page shells. Each page is presentation-only and optional-result aware."""

from pages.fundamentals import render_fundamentals_page
from pages.news import render_news_page
from pages.overview import render_overview_page
from pages.portfolio import render_portfolio_page
from pages.reports import render_reports_page
from pages.technical import render_technical_page
from pages.watchlist import render_watchlist_page

__all__ = [
    "render_fundamentals_page",
    "render_news_page",
    "render_overview_page",
    "render_portfolio_page",
    "render_reports_page",
    "render_technical_page",
    "render_watchlist_page",
]
