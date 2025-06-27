from pydantic import BaseModel, HttpUrl

class IngestCommentsRepliesRequest(BaseModel):
    tenantId: str
    accountId: str
    postId: str
    accessToken: str

class GenerateReplyRequest(BaseModel):
    tenantId: str
    accountId: str
    postId: str
    commentText: str

class GenerateCaptionRequest(BaseModel):
    tenantId: str
    accountId: str
    imageUrl: str

class IngestPostCaptionAIRequest(BaseModel):
    tenantId: str
    accountId: str
    postId: str
    imageUrl: HttpUrl
    caption: str
