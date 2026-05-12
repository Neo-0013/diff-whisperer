from pydantic import BaseModel, Field
from typing import List

class RiskItem(BaseModel):
    category: str = Field(..., description="Category of the risk (e.g., Security, Complexity)")
    description: str = Field(..., description="Brief assessment of the risk")
    level: str = Field(..., description="Risk level (Low, Medium, High)")

class AnalysisResponse(BaseModel):
    story: str = Field(..., description="The high-level narrative of the changes")
    risks: List[RiskItem] = Field(default_factory=list, description="List of identified risks")
    improvements: List[str] = Field(default_factory=list, description="List of suggested improvements")
