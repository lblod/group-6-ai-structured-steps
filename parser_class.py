from pydantic import BaseModel, Field

class Product(BaseModel):
    uri: str = Field(description='Uri of the product')
    title: str = Field(description='Title of the product.')
    description: str = Field(description='Description of the product.')
    #procedure: str = Field(description='Procedure to apply for the product.')    
    procedure_as_steps: str = Field(description='Please rewrite the procedure as a series of numbered steps. Ensure each step starts with a chronological number, is specific, concise, and action-oriented, focusing on clear instructions for execution.')
