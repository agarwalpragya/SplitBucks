from pydantic import BaseModel, constr

class RemovePersonRequest(BaseModel):
    name: constr(min_length=1, max_length=40, regex=r"^[A-Za-z\s\-']+$")
