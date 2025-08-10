from pydantic import BaseModel, constr, condecimal

class SetPriceRequest(BaseModel):
    name: constr(min_length=1, max_length=40, regex=r"^[A-Za-z\s\-']+$")
    price: condecimal(gt=0, decimal_places=2)
