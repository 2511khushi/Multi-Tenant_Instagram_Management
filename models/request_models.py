from pydantic import BaseModel

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
    imageDescription: str
