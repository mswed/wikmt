from flask_login import logout_user
from models import db, User


class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get a user by Id
        :param user_id: int, user id
        :returns: Tuple(User, str), User and error message
        """
        user = db.session.query(User).get(user_id)
        if not user:
            logout_user()
            return None, "Session expired. Please login again"

        return user, None

    @staticmethod
    def update_user_password(user, current_password, new_password):
        """
        Update a user's password
        :param user: Object, User object
        :param current_password: str, currrent user password
        :param new_password: str, new password
        :returns: Tuple(User, str), User and error message
        """
        try:
            # We can update the login
            updated_user = user.update_password(current_password, new_password)

            if not updated_user:
                return None, "Wrong password!"

            db.session.add(updated_user)
            db.session.commit()

            return updated_user, None

        except Exception as e:
            print("error", e)
            import traceback

            print(traceback.format_exc())
            db.session.rollback()
            return None, "Failed to update password"

    @staticmethod
    def update_user_details(user, birth_year, sex, race, ethnicity):
        """
        Update a user's details
        :param user: Object, User object
        :param birth_year: int, year the user was born
        :param sex: str, user's sex
        :param race: str, user's race
        :param ethnicity: str, user's ethnicity
        :returns: Tuple(User, str), User and error message
        """
        try:
            # We can update the login
            updated_user = user.update_details(birth_year, sex, race, ethnicity)
            if not updated_user:
                return None, "Failed to update user details!"
            db.session.add(updated_user)
            db.session.commit()

            return updated_user, None

        except Exception as e:
            db.session.rollback()
            return None, "Failed to update user details!"
