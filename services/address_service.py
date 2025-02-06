from models import db, Address, Search


class AddressService:
    @staticmethod
    def get_user_addresses(user_id):
        """
        Get all addresses for a user
        :param user_id: int, user ID
        :returns: list(Address), list of user addresses
        """
        return db.session.query(Address).filter(Address.user_id == user_id).all()

    @staticmethod
    def create_address(user_id, address, mapbox_id):
        """
        Create a new address
        :param user_id: int, user ID
        :param address: str, address
        :param mapbox_id: str, address id in mapbox
        :returns: Tuple(Address, str), Address and error message
        """

        # Validate required fields
        if not all([address, mapbox_id]):
            return None, "Missing required fields (address, mapbox_id)"
        try:
            new_address = Address(
                user_id=user_id,
                address=address,
                mapbox_id=mapbox_id,
            )

            db.session.add(new_address)
            db.session.commit()

            return new_address, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_address_by_mapbox_id(user_id, mapbox_id):
        """
        Find a user's address based on its mapbox id
        :param user_id: int, user id
        :param mapbox_id: str, address id in mapbox
        :returns: Address, address object if address is found, else None
        """

    @staticmethod
    def delete_address(user_id, address_id):
        """
        Delete an address if it's not attached to any searches

        :param user_id: int, user ID
        :param address_id: int, address ID
        :returns: tuple(success(bool), message(str), status code(int))
        """
        try:
            address = db.session.query(Address).get(address_id)
            if not address:
                return False, "Could not find address", 404

            if address.user_id != user_id:
                return False, "You are not authorized to delete this address", 403

            # Check if address is attached to searches
            if (
                db.session.query(Search)
                .filter_by(address_id=address_id, user_id=user_id)
                .first()
            ):
                return (
                    False,
                    "This address is attached to a search. Please delete the search first.",
                    409,
                )

            db.session.delete(address)
            db.session.commit()
            return True, "Deleted address", 200

        except Exception as e:
            db.session.rollback()
            return False, str(e), 500
