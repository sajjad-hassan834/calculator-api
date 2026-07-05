from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# Common Config
# ==========================================
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Nested Schemas (Inputs, Outputs, etc.)
# ==========================================

# Calculator Input
class CalculatorInputBase(BaseSchema):
    key: str
    label: str
    input_type: str
    data_type: str = "number"
    placeholder: str | None = None
    help_text: str | None = None
    suffix: str | None = None
    prefix: str | None = None
    default_value: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    step_value: float | None = None
    options: dict[str, Any] | None = None
    validation_rules: dict[str, Any] | None = None
    conditional_rules: dict[str, Any] | None = None
    is_required: bool = True
    is_visible: bool = True
    sort_order: int = 0


class CalculatorInputCreate(CalculatorInputBase):
    pass


class CalculatorInputUpdate(CalculatorInputBase):
    pass


class CalculatorInputResponse(CalculatorInputBase):
    id: str


# Calculator Output
class CalculatorOutputBase(BaseSchema):
    key: str
    label: str
    description: str | None = None
    output_type: str
    data_type: str = "number"
    prefix: str | None = None
    suffix: str | None = None
    format: str | None = None
    decimal_places: int = 2
    is_primary: bool = False
    is_visible: bool = True
    chart_data_mapping: dict[str, Any] | None = None
    sort_order: int = 0


class CalculatorOutputCreate(CalculatorOutputBase):
    pass


class CalculatorOutputUpdate(CalculatorOutputBase):
    pass


class CalculatorOutputResponse(CalculatorOutputBase):
    id: str


# Calculator Formula
class CalculatorFormulaBase(BaseSchema):
    name: str
    description: str | None = None
    formula_text: str
    formula_python: str | None = None
    formula_javascript: str | None = None
    variables: dict[str, Any] | None = None
    is_primary: bool = False
    sort_order: int = 0


class CalculatorFormulaCreate(CalculatorFormulaBase):
    pass


class CalculatorFormulaUpdate(CalculatorFormulaBase):
    pass


class CalculatorFormulaResponse(CalculatorFormulaBase):
    id: str


# Calculator FAQ
class CalculatorFAQBase(BaseSchema):
    question: str
    answer: str
    schema_type: str = "FAQPage"
    is_published: bool = True
    sort_order: int = 0


class CalculatorFAQCreate(CalculatorFAQBase):
    pass


class CalculatorFAQUpdate(CalculatorFAQBase):
    pass


class CalculatorFAQResponse(CalculatorFAQBase):
    id: str


# Calculator Example
class CalculatorExampleBase(BaseSchema):
    title: str | None = None
    description: str | None = None
    input_values: dict[str, Any]
    expected_outputs: dict[str, Any]
    explanation: str | None = None
    is_featured: bool = False
    sort_order: int = 0


class CalculatorExampleCreate(CalculatorExampleBase):
    pass


class CalculatorExampleUpdate(CalculatorExampleBase):
    pass


class CalculatorExampleResponse(CalculatorExampleBase):
    id: str


# Calculator Reference
class CalculatorReferenceBase(BaseSchema):
    title: str
    url: str | None = None
    source_name: str | None = None
    citation_text: str | None = None
    sort_order: int = 0


class CalculatorReferenceCreate(CalculatorReferenceBase):
    pass


class CalculatorReferenceUpdate(CalculatorReferenceBase):
    pass


class CalculatorReferenceResponse(CalculatorReferenceBase):
    id: str


# Calculator Chart
class CalculatorChartBase(BaseSchema):
    chart_type: str
    title: str | None = None
    description: str | None = None
    data_mapping: dict[str, Any]
    options: dict[str, Any] | None = Field(default_factory=dict)
    width: int | None = None
    height: int | None = None
    is_primary: bool = False
    sort_order: int = 0


class CalculatorChartCreate(CalculatorChartBase):
    pass


class CalculatorChartUpdate(CalculatorChartBase):
    pass


class CalculatorChartResponse(CalculatorChartBase):
    id: str


# Calculator Section
class CalculatorSectionBase(BaseSchema):
    section_type: str
    title: str
    content: str | None = None
    is_published: bool = True
    sort_order: int = 0


class CalculatorSectionCreate(CalculatorSectionBase):
    pass


class CalculatorSectionUpdate(CalculatorSectionBase):
    pass


class CalculatorSectionResponse(CalculatorSectionBase):
    id: str


# Calculator Media
class CalculatorMediaBase(BaseSchema):
    media_id: str
    media_type: str | None = None
    sort_order: int = 0


class CalculatorMediaCreate(CalculatorMediaBase):
    pass


class CalculatorMediaUpdate(CalculatorMediaBase):
    pass


class CalculatorMediaResponse(CalculatorMediaBase):
    id: str


# ==========================================
# Main Calculator Schemas
# ==========================================

class CalculatorBase(BaseSchema):
    name: str
    slug: str | None = None
    category_id: str | None = None
    author_id: str | None = None
    reviewer_id: str | None = None
    seo_metadata_id: str | None = None
    short_description: str | None = None
    description: str | None = None
    meta_description: str | None = None
    keywords: list[str] | None = None
    calculator_type: str
    engine_type: str = "formula"
    engine_config: dict[str, Any] | None = Field(default_factory=dict)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    formula_expression: str | None = None
    default_values: dict[str, Any] | None = Field(default_factory=dict)
    validation_rules: dict[str, Any] | None = Field(default_factory=dict)
    currency: str = "USD"
    country: str = "US"
    is_featured: bool = False
    is_popular: bool = False
    is_calculator: bool = True
    is_active: bool = True
    is_published: bool = False
    status: str = "draft"
    sort_order: int = 0


class CalculatorCreate(CalculatorBase):
    inputs: list[CalculatorInputCreate] | None = None
    outputs: list[CalculatorOutputCreate] | None = None
    formulas: list[CalculatorFormulaCreate] | None = None
    faqs: list[CalculatorFAQCreate] | None = None
    examples: list[CalculatorExampleCreate] | None = None
    references: list[CalculatorReferenceCreate] | None = None
    charts: list[CalculatorChartCreate] | None = None
    sections: list[CalculatorSectionCreate] | None = None
    media: list[CalculatorMediaCreate] | None = None


class CalculatorUpdate(CalculatorBase):
    name: str | None = None
    calculator_type: str | None = None
    inputs: list[CalculatorInputUpdate] | None = None
    outputs: list[CalculatorOutputUpdate] | None = None
    formulas: list[CalculatorFormulaUpdate] | None = None
    faqs: list[CalculatorFAQUpdate] | None = None
    examples: list[CalculatorExampleUpdate] | None = None
    references: list[CalculatorReferenceUpdate] | None = None
    charts: list[CalculatorChartUpdate] | None = None
    sections: list[CalculatorSectionUpdate] | None = None
    media: list[CalculatorMediaUpdate] | None = None


class CalculatorResponse(CalculatorBase):
    id: str
    view_count: int
    published_at: datetime | None = None
    scheduled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    inputs: list[CalculatorInputResponse] = []
    outputs: list[CalculatorOutputResponse] = []
    formulas: list[CalculatorFormulaResponse] = []
    faqs: list[CalculatorFAQResponse] = []
    examples: list[CalculatorExampleResponse] = []
    references: list[CalculatorReferenceResponse] = []
    charts: list[CalculatorChartResponse] = []
    sections: list[CalculatorSectionResponse] = []
    media: list[CalculatorMediaResponse] = []


class CalculatorListResponse(CalculatorBase):
    # A lightweight version for list endpoints
    id: str
    view_count: int
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CalculatorStatsResponse(BaseSchema):
    total: int
    published: int
    draft: int
    archived: int
    recently_edited: int
    popular: int
