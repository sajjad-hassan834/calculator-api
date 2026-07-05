from enum import Enum


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class CalculatorType(str, Enum):
    LOAN = "loan"
    MORTGAGE = "mortgage"
    INVESTMENT = "investment"
    SAVINGS = "savings"
    RETIREMENT = "retirement"
    TAX = "tax"
    INSURANCE = "insurance"
    CURRENCY = "currency"
    BUSINESS = "business"
    EDUCATION = "education"
    PERSONAL_FINANCE = "personal_finance"


class EngineType(str, Enum):
    FORMULA = "formula"
    PYTHON = "python"
    JAVASCRIPT = "javascript"


class InputType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    RANGE = "range"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    DATE = "date"
    BOOLEAN = "boolean"


class MediaType(str, Enum):
    IMAGE = "image"
    ILLUSTRATION = "illustration"
    ICON = "icon"
    PDF = "pdf"
    DOWNLOAD = "download"
    AVATAR = "avatar"
    VIDEO = "video"


class SectionType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    TABLE = "table"
    CTA = "cta"
    CALCULATOR_EMBED = "calculator_embed"


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"


class AdType(str, Enum):
    BANNER = "banner"
    SIDEBAR = "sidebar"
    NATIVE = "native"
    POPUP = "popup"
    IN_CONTENT = "in_content"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    ARCHIVE = "archive"
    RESTORE = "restore"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    SETTING_CHANGE = "setting_change"
    PERMISSION_CHANGE = "permission_change"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RoleName(str, Enum):
    SUPER_ADMIN = "super-admin"
    ADMIN = "admin"
    EDITOR = "editor"
    SEO_MANAGER = "seo-manager"
    CONTENT_WRITER = "content-writer"
    REVIEWER = "reviewer"
    SUPPORT = "support"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class RelationshipType(str, Enum):
    RELATED = "related"
    ALTERNATIVE = "alternative"
    COMPLEMENTARY = "complementary"


VALID_CONTENT_STATUSES = [s.value for s in ContentStatus]
VALID_CALCULATOR_TYPES = [t.value for t in CalculatorType]
VALID_ENGINE_TYPES = [e.value for e in EngineType]
VALID_INPUT_TYPES = [i.value for i in InputType]
VALID_MEDIA_TYPES = [m.value for m in MediaType]
VALID_SECTION_TYPES = [s.value for s in SectionType]
VALID_CHART_TYPES = [c.value for c in ChartType]
VALID_AD_TYPES = [a.value for a in AdType]
VALID_AUDIT_ACTIONS = [a.value for a in AuditAction]
VALID_SEVERITIES = [s.value for s in Severity]
VALID_ROLE_NAMES = [r.value for r in RoleName]
VALID_DIFFICULTY_LEVELS = [d.value for d in DifficultyLevel]
VALID_RELATIONSHIP_TYPES = [r.value for r in RelationshipType]
