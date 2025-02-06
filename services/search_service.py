from models import db, Search, Address
from .address_service import AddressService


class SearchService:
    def __init__(self, address_service) -> None:
        self.address_service = address_service or address_service()

    @staticmethod
    def get_recent_searches(limit=5):
        """
        Get most recent searches
        :param limit: int, number of searches to fetch
        :returns: list(Search), list of found searches
        """
        # TODO: sort by latest search
        return db.session.query(Search).limit(limit).all()

    @staticmethod
    def get_user_searches(user_id):
        """
        Get all searches for a specific user
        :param user_id: int, user ID
        :returns: list(Search), list of found user searches
        """
        return db.session.query(Search).filter(Search.user_id == user_id).all()

    def create_search(self, user_id, start_date, end_date, address, mapbox_id):
        """
        Create a new address
        :param user_id: int, user ID
        :param start_date: str, search start date
        :param end_date: str, search end date
        :param address: str, address
        :param mapbox_id: str, address id in mapbox
        :returns: Tuple(Search, str), Search and error message
        """

        # Validate required fields
        if not all([start_date, end_date]):
            return None, "Missing required fields (start_date, end_date)"

        target_address = None

        # If we have an address the search needs to save it
        if mapbox_id and mapbox_id != "undefined":
            # Look for the address
            saved_address = self.address_service.get_address_by_mapbox_id(
                user_id, mapbox_id
            )

            if not saved_address:
                saved_address, error = self.address_service.create_address(
                    user_id, address, mapbox_id
                )
                if error:
                    return None, "Failed to save address. Can not save search"

            target_address = saved_address.id

        try:
            new_search = Search(
                user_id=user_id,
                address_id=target_address,
                start_date=start_date,
                end_date=end_date,
            )

            db.session.add(new_search)
            db.session.commit()

            return new_search, None

        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_search(user_id, search_id):
        """
        Delete a search

        :param user_id: int, user ID
        :param address_id: int, address ID
        :returns: tuple(success(bool), message(str), status code(int))
        """
        try:
            search = db.session.query(Search).get(search_id)
            if not search:
                return False, "Could not find search", 404

            if search.user_id != user_id:
                return False, "You are not authorized to delete this search", 403

            db.session.delete(search)
            db.session.commit()

            return True, "Deleted search", 200

        except Exception as e:
            db.session.rollback()
            return False, str(e), 500

    @staticmethod
    def load_search(search_id):
        """
        Load search info based on an id

        :param search_id: int, search ID
        :returns: tuple(Search data(dict), message(str), status_code(int))
        """
        try:
            search = db.session.query(Search).get(search_id)

            if not search:
                return None, "Could not find search", 404

            # Address and mapbox id might be empty if the search is date based
            search_address = None if search.address is None else search.address.address
            search_mapbox_id = (
                None if search.address is None else search.address.mapbox_id
            )

            search_data = {
                "address": search_address,
                "mapboxId": search_mapbox_id,
                "startDate": search.start_date.strftime("%Y-%m-%d"),
                "endDate": search.end_date.strftime("%Y-%m-%d"),
            }

            return search_data, None, 200

        except Exception as e:
            db.session.rollback()
            return None, str(e), 500
