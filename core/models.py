"""Pydantic models for structured policy data."""

from pydantic import BaseModel, Field


class PolicyCoverage(BaseModel):
    name: str = Field(description="Coverage type name")
    limit: str = Field(default="Not specified")
    sub_limit: str = Field(default="None")
    copay: str = Field(default="None")
    waiting_period: str = Field(default="None")


class PolicyExclusion(BaseModel):
    description: str = Field(description="What is excluded")
    category: str = Field(default="General")


class PolicySummary(BaseModel):
    insurer: str = Field(default="Unknown")
    product_name: str = Field(default="Unknown")
    policy_type: str = Field(default="Unknown")
    sum_insured: str = Field(default="Unknown")
    premium: str = Field(default="Unknown")
    policy_term: str = Field(default="Unknown")
    coverages: list[PolicyCoverage] = Field(default_factory=list)
    exclusions: list[PolicyExclusion] = Field(default_factory=list)
    waiting_periods: list[str] = Field(default_factory=list)
    key_benefits: list[str] = Field(default_factory=list)
    key_limitations: list[str] = Field(default_factory=list)


class ComparisonResult(BaseModel):
    better_in_policy_a: list[str] = Field(default_factory=list)
    better_in_policy_b: list[str] = Field(default_factory=list)
    same_in_both: list[str] = Field(default_factory=list)
    hidden_gotchas: list[str] = Field(default_factory=list)
    verdict: str = Field(default="")


class UserProfile(BaseModel):
    age: int | None = None
    city: str | None = None
    family_members: int | None = None
    income_range: str | None = None
    existing_conditions: list[str] = Field(default_factory=list)
    existing_coverage: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)


class RenewalAdvice(BaseModel):
    life_changes_detected: list[str] = Field(default_factory=list)
    coverage_gaps: list[str] = Field(default_factory=list)
    over_coverage: list[str] = Field(default_factory=list)
    recommendation: str = Field(default="")
    action_items: list[str] = Field(default_factory=list)
