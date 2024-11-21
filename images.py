from sqlmodel import Field, SQLModel

class Images(SQLModel, table=True):
    id_image: str = Field(default=None, primary_key=True)
    uploaded: bool
    #created_at: data
    #created_by: user que criou
    name_img: str #esse campo nao precisa
