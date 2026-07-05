"""Verify models can be imported and have correct table names."""
from app.models.auth import (
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
    UserSession,
)
from app.models.content import (
    BlogCalculator,
    BlogPost,
    BlogSection,
    Calculator,
    CalculatorChart,
    CalculatorExample,
    CalculatorFAQ,
    CalculatorFormula,
    CalculatorInput,
    CalculatorOutput,
    CalculatorReference,
    CalculatorSection,
    Category,
    Guide,
    GuideCalculator,
    GuideSection,
    RelatedCalculator,
)
from app.models.seo import (
    CustomPage,
    Redirect,
    SEOMetadata,
    Sitemap,
)
from app.models.media import (
    CalculatorMedia,
    BlogMedia,
    GuideMedia,
    Media,
    MediaFolder,
)
from app.models.site import (
    Advertisement,
    FooterColumn,
    FooterLink,
    HomepageSection,
    NavigationItem,
    NewsletterSubscriber,
    SiteSetting,
    Testimonial,
)
from app.models.people import (
    Author,
    Reviewer,
)
from app.models.analytics import (
    PageView,
    SearchHistory,
    PopularCalculator,
)
from app.models.audit import AuditLog
from app.models.future import (
    AIExplanation,
    Bookmark,
    Notification,
    SavedCalculation,
)


def test_all_models_have_tablenames():
    models = [
        User, UserProfile, Role, Permission, RolePermission, UserRole, UserSession,
        Category, Calculator, CalculatorInput, CalculatorOutput,
        CalculatorFormula, CalculatorFAQ, CalculatorExample, CalculatorReference,
        CalculatorChart, CalculatorSection, RelatedCalculator,
        Guide, GuideSection, GuideCalculator,
        BlogPost, BlogSection, BlogCalculator,
        SEOMetadata, Redirect, Sitemap, CustomPage,
        MediaFolder, Media, CalculatorMedia, BlogMedia, GuideMedia,
        HomepageSection, NavigationItem, FooterColumn, FooterLink,
        Advertisement, Testimonial, NewsletterSubscriber, SiteSetting,
        Author, Reviewer,
        PageView, SearchHistory, PopularCalculator,
        AuditLog,
        Bookmark, SavedCalculation, Notification, AIExplanation,
    ]
    for model in models:
        assert model.__tablename__ is not None, f"{model.__name__} missing __tablename__"


def test_user_relationship_refs():
    assert hasattr(User, "profile")
    assert hasattr(User, "roles")
    assert hasattr(User, "sessions")


def test_calculator_relationship_refs():
    assert hasattr(Calculator, "inputs")
    assert hasattr(Calculator, "outputs")
    assert hasattr(Calculator, "faqs")
    assert hasattr(Calculator, "examples")
    assert hasattr(Calculator, "charts")
    assert hasattr(Calculator, "sections")
    assert hasattr(Calculator, "related_calculators")
    assert hasattr(Calculator, "media")
    assert hasattr(Calculator, "author")
    assert hasattr(Calculator, "reviewer")


def test_blog_relationship_refs():
    assert hasattr(BlogPost, "sections")
    assert hasattr(BlogPost, "calculators")
    assert hasattr(BlogPost, "media")
    assert hasattr(BlogPost, "author")
    assert hasattr(BlogPost, "reviewer")
