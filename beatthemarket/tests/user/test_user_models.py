from beatthemarket.blueprints.user.models import User


# class TestUser(object):
#     def test_serialize_token(self, token):
#         """ Token serializer serializes a JWS correctly. """
#         assert token.count('.') == 2
#
#     def test_deserialize_token(self, token):
#         """ Token de-serializer de-serializes a JWS correctly. """
#         user = User.deserialize_token(token)
#         assert user.email == 'admin@local.host'
