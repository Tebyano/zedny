from pydantic import BaseModel, Field

class LLMRequest(BaseModel):
    prompt: str = Field(..., description="النص الذي تريد توليد رد منه")
    max_tokens: int = Field(50, description="الحد الأقصى لعدد الرموز في النص الناتج")
    model: str = Field("command-r-plus", description="اسم نموذج Cohere المستخدم")


class LLMResponse(BaseModel):
    text: str = Field(..., description="النص الناتج من نموذج Cohere")
