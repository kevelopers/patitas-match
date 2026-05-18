from pydantic import BaseModel, ConfigDict


class AnimalBase(BaseModel):
    name: str
    animal_type: str
    size: str
    energy_level: str
    status: str = "available"


class AnimalCreate(AnimalBase):
    pass


class AnimalResponse(AnimalBase):
    id: int
    foundation_id: str
    model_config = ConfigDict(from_attributes=True)
