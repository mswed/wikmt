from .auth_service import AuthService
from .search_service import SearchService
from .address_service import AddressService
from .home_service import HomeService
from .user_service import UserService
from .risk_service import RiskService
from .geo_service import GeoService

auth_service = AuthService()
address_service = AddressService()
search_service = SearchService(address_service)
home_service = HomeService(address_service, search_service)
user_service = UserService()
risk_service = RiskService()
geo_service = GeoService()
