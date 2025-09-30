from pydantic import BaseModel,Field,EmailStr , field_validator ,ConfigDict


class SignupModel(BaseModel):
    model_config = ConfigDict(extra='forbid') 
    name: str = Field(..., min_length=2, max_length=50)
    email : EmailStr   = Field(...,min_length=5 ,max_length=50)
    password :str  = Field(...,max_length=128) 
    
    @field_validator('password')
    @classmethod
    def password_must_be_long_enough(cls, password: str) -> str:
        """Validates that the password has at least 8 characters."""
        min_length = 8
        if len(password) < min_length:
            # This is where you raise the error with your custom message
            raise ValueError(f'Password should have at least {min_length} characters')
        return password
    

class SignInModel(BaseModel):
    email : EmailStr   = Field(...,min_length=5 ,max_length=50)
    password :str  = Field(...,min_length=8,max_length=128) 
    