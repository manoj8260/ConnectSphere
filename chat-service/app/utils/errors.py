
class ChatException(Exception):
    '''This is the base class for all the Auth/User errors'''
    def __init__(self, message : str , status_code : int =400,resulation :str = "Contact support"):
        self.message = message
        self.status_code = status_code
        self.resulation = resulation
        super().__init__(message)
    
class InvalidOrExpireToken(ChatException):
    '''User has provided the invalid or expire token'''
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, status_code=401, resulation="Login again with a valid token")
        
class RevokedToken(ChatException):
    '''User has provided the token that has been revoked '''
    def __init__(self, message: str = "Token has been revoked"):
        super().__init__(message, status_code=401, resulation="Request a new token by logging in again")
        
class AccessTokenRequired(ChatException):
    '''User has provided the refresh token when the access toke is needed'''
    def __init__(self, message: str = "Access token required"):
        super().__init__(message, status_code=401, resulation="Provide a valid access token in the request")
class RefreshTokenRequired(ChatException):
    '''User has provided the access token when the refresh toke is needed'''
    def __init__(self, message: str = "Refresh token required"):
        super().__init__(message, status_code=401, resulation="Use your refresh token to request a new access token")
        
class RoomAleradyExists(ChatException):
    '''The room is already exists exceptiom '''
    def __init__(self, message: str = "room  already exists with this name"):
        super().__init__(message, status_code=409, resulation="Try create diff room name")
        
class RoomNotFound(ChatException):
    '''Room is not avilavale (Room is not Exists)'''
    def __init__(self, message: str = "Room not found"):
        super().__init__(message, status_code=404, resulation="you enter invalid room name")
        

class UserNotFound(ChatException):
    '''User is not avilavale (User is not Exists)'''
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404, resulation="Check the user ID/email and try again")

