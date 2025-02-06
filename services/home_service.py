class HomeService:
    """
    A class for fetching data for the two possible home pages. Logged in,
    and not logged in
    """

    def __init__(self, address_service, search_service):
        """
        :param address_service: instance, address service
        :param search_service: instance, search service
        """
        self.address_service = address_service
        self.search_service = search_service

    def get_authenticated_home_data(self, user_id):
        """
        Get data needed for displaying the authenticated home page
        :param user_id: int, user ID
        :returns: dict{addresses, searches}, found adddresses and searches
        """
        return {
            "addresses": self.address_service.get_user_addresses(user_id),
            "searches": self.search_service.get_user_searches(user_id),
        }

    def get_public_home_data(self):
        """
        Get data needed for displaying the nonauthenticated home page
        :returns: dict{recent_searches}
        """

        return {"recent_searches": self.search_service.get_recent_searches()}

