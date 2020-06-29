""" Test classes for Tags viewset. """
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.urls import reverse
from mock import patch
from rest_framework.test import APIClient

from eox_tagging.api.v1.serializers import TagSerializer
from eox_tagging.constants import AccessLevel
from eox_tagging.models import Tag


@override_settings(
    EOX_TAGGING_DEFINITIONS=[
        {
            "tag_type": "example_tag_1",
            "validate_owner_object": "User",  # default = Site
            "validate_access": {"equals": "PRIVATE"},
            "validate_tag_value": {"in": ["example_tag_value", "example_tag_value_1"]},
            "validate_target_object": "User",
            "validate_expiration_date": {"exist": True},
        },
        {
            "tag_type": "example_tag_2",
            "validate_owner_object": "Site",
            "validate_access": {"equals": "PRIVATE"},
            "validate_tag_value": {"in": ["example_tag_value", "example_tag_value_1"]},
            "validate_target_object": "User",
            "validate_expiration_date": {"exist": True},
        },
        {
            "tag_type": "example_tag_3",
            "validate_owner_object": "User",
            "validate_access": {"equals": "PRIVATE"},
            "validate_tag_value": {"in": ["example_tag_value", "example_tag_value_1"]},
            "validate_target_object": "Site",
            "validate_expiration_date": {"exist": True},
        },
    ])
class TestTagViewSet(TestCase):
    """Test class for tags viewset."""

    patch_permissions = patch("eox_tagging.api.v1.permissions.EoxTaggingAPIPermission.has_permission",
                              return_value=True)

    def setUp(self):
        """ Model setup used to create objects used in tests."""
        self.target_object = User.objects.create(username="user_test")
        self.owner_site = Site.objects.get(id=settings.TEST_SITE)

        # Client authentication
        self.owner_user = User.objects.create(username="myuser")
        self.client = APIClient()
        self.client.force_authenticate(self.owner_user)

        self.example_tag = Tag.objects.create(
            tag_value="example_tag_value",
            tag_type="example_tag_1",
            target_object=self.target_object,
            owner_object=self.owner_user,
            access=AccessLevel.PRIVATE,
            expiration_date=datetime.datetime(2020, 10, 19, 10, 20, 30),
        )

        self.example_tag_1 = Tag.objects.create(
            tag_value="example_tag_value",
            tag_type="example_tag_2",
            target_object=self.target_object,
            owner_object=self.owner_site,
            access=AccessLevel.PRIVATE,
            expiration_date=datetime.datetime(2020, 10, 19, 10, 30, 40),
        )

        self.example_tag_2 = Tag.objects.create(
            tag_value="example_tag_value",
            tag_type="example_tag_2",
            target_object=self.target_object,
            owner_object=self.owner_site,
            access=AccessLevel.PRIVATE,
            expiration_date=datetime.date(2020, 10, 19),
        )

        self.example_tag_3 = Tag.objects.create(
            tag_value="example_tag_value",
            tag_type="example_tag_3",
            target_object=self.owner_site,
            owner_object=self.owner_user,
            access=AccessLevel.PRIVATE,
            expiration_date=datetime.date(2020, 10, 19),
        )
        self.KEY = self.example_tag.key.hex
        # Test URLs
        self.URL = reverse("tag-list")
        self.URL_DETAILS = reverse("tag-detail", args=[self.KEY])

    @patch_permissions
    def test_get_all_tags(self, _):
        """Used to test getting all tags."""
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200)

    @patch_permissions
    def test_retreive_tag(self, _):
        """Used to test getting a tag given its key."""
        response = self.client.get(self.URL_DETAILS)

        self.assertEqual(response.status_code, 200)

    @patch_permissions
    def test_create_tag(self, _):
        """"Used to test creating a tag."""

        data = {
            "tag_type": "example_tag_1",
            "tag_value": "example_tag_value",
            "target_type": "user",
            "target_id": "user_test",
            "owner_type": "user",
            "access": "PRIVATE",
            "expiration_date": "2020-12-04 10:20:30",
        }

        response = self.client.post(self.URL, data, format='json')

        self.assertEqual(response.status_code, 201)

    @patch_permissions
    def test_create_tag_without_owner(self, _):
        """"
        Used to test creating a tag without an owner. The owner should be set as a default
        to be the site.
        """
        data = {
            "tag_type": "example_tag_2",
            "tag_value": "example_tag_value",
            "target_type": "user",
            "target_id": "user_test",
            "access": "PRIVATE",
            "expiration_date": "2020-12-04 10:20:30",
        }

        response = self.client.post(self.URL, data, format='json')
        owner_type = response.data.get("meta").get("owner_type")
        self.assertEqual(owner_type, "Site")

    @patch_permissions
    def test_create_tag_with_iso_datetime_format(self, _):
        """"Used to test creating a tag using ISO format in datetime fields."""
        data = {
            "tag_type": "example_tag_1",
            "tag_value": "example_tag_value",
            "target_type": "user",
            "target_id": "user_test",
            "owner_type": "user",
            "access": "PRIVATE",
            "expiration_date": "2020-12-04T10:20:30.15785",
        }

        response = self.client.post(self.URL, data, format='json')

        self.assertEqual(response.status_code, 201)

    @patch_permissions
    def test_create_tag_with_wrong_datetime_format(self, _):
        """"
        Used to test creating a tag using wrong format in datetime fields. This results in a
        bad request.
        """
        data = {
            "tag_type": "example_tag_1",
            "tag_value": "example_tag_value",
            "target_type": "user",
            "target_id": "user_test",
            "owner_type": "user",
            "access": "PRIVATE",
            "expiration_date": "12-04-2020 10:20:30",
        }

        response = self.client.post(self.URL, data, format='json')

        self.assertEqual(response.status_code, 400)

    @patch_permissions
    def test_create_tag_with_owner_site(self, _):
        """"Used to test creating a tag with site as owner."""

        data = {
            "tag_type": "example_tag_2",
            "tag_value": "example_tag_value",
            "target_type": "user",
            "target_id": "user_test",
            "owner_type": "site",
            "access": "PRIVATE",
            "expiration_date": "2020-12-04 10:30:40",
        }

        response = self.client.post(self.URL, data, format='json')
        owner_type = response.data.get("meta").get("owner_type").lower()
        self.assertEqual(owner_type, "site")

    @patch_permissions
    def test_create_tag_with_wrong_owner(self, _):
        """"Used to test creating a tag with wrong owner_type. This results in bad request."""
        data = {
            "tag_type": "example_tag_1",
            "tag_value": "example_tag_value",
            "target_type": "user",
            "target_id": "user_test",
            "owner_type": "course",  # default is site
            "access": "PRIVATE",
            "expiration_date": "2020-12-04 10:30:40 ",
        }

        response = self.client.post(self.URL, data, format='json')

        self.assertEqual(response.status_code, 400)

    @patch_permissions
    def test_patch_tag(self, _):
        """Used to test that a tag can't be updated."""
        response = self.client.patch(self.URL_DETAILS)

        self.assertEqual(response.status_code, 405)

    @patch_permissions
    def test_put_tag(self, _):
        """Used to test that a tag can't be updated."""
        response = self.client.put(self.URL_DETAILS)

        self.assertEqual(response.status_code, 405)

    @patch_permissions
    def test_filter_by_tag_key(self, _):
        """Used to test getting a tag given its key."""
        query_params = {
            "key": self.example_tag.key.hex,
        }

        response = self.client.get(self.URL, query_params)

        data = response.json().get("results")[0]
        self.assertEqual(data.get("key").replace("-", ""), self.KEY)

    @patch_permissions
    def test_filter_by_username(self, _):
        """Used to test getting a tag given its target."""
        query_params = {
            "username": "user_test",
        }

        response = self.client.get(self.URL, query_params)

        data = response.json().get("results")[0].get("meta")
        self.assertEqual(data.get("target_id"), "user_test")

    @patch_permissions
    def test_filter_by_owner_user(self, _):
        """Used to test getting a tag given its owner of type user."""
        query_params = {
            "owner_type": "user",
        }

        response = self.client.get(self.URL, query_params)

        data = response.json().get("results")[0]
        owner_type = data.get("meta").get("owner_type").lower()
        self.assertEqual(owner_type, "user")

    @patch_permissions
    def test_filter_by_owner_user_and_target(self, _):
        """Used to test getting a tag given its owner of type user and target type."""
        query_params_with_target = {
            "owner_type": "user",
            "target_type": "user",
        }
        query_params_without_target = {
            "owner_type": "user",
        }

        response_with_target = self.client.get(self.URL, query_params_with_target)
        response_without_target = self.client.get(self.URL, query_params_without_target)

        results_with_target = response_with_target.json().get("results")
        results_without_target = response_without_target.json().get("results")
        owner_type = results_with_target[0].get("meta").get("owner_type")
        target_type = results_with_target[0].get("meta").get("target_type")
        self.assertEqual(len(results_with_target), 1)
        self.assertEqual(len(results_without_target), 2)
        self.assertEqual(owner_type, "User")
        self.assertEqual(target_type, "User")

    @patch_permissions
    def test_filter_by_owner_user_and_username(self, _):
        """Used to test getting a tag given its owner of type user and target username."""
        query_params_with_username = {
            "owner_type": "user",
            "username": "user_test",
        }
        query_params_without_username = {
            "owner_type": "user",
        }

        response_with_username = self.client.get(self.URL, query_params_with_username)
        response_without_username = self.client.get(self.URL, query_params_without_username)

        results_with_username = response_with_username.json().get("results")
        results_without_username = response_without_username.json().get("results")
        owner_type = results_with_username[0].get("meta").get("owner_type")
        target_type = results_with_username[0].get("meta").get("target_type")
        self.assertEqual(len(results_with_username), 1)
        self.assertEqual(len(results_without_username), 2)
        self.assertEqual(owner_type, "User")
        self.assertEqual(target_type, "User")

    @patch_permissions
    def test_filter_by_owner_site(self, _):
        """Used to test getting a tag given its owner of type user."""
        query_params = {
            "owner_type": "site",
        }

        response = self.client.get(self.URL, query_params)

        data = response.json().get("results")[0]
        owner_type = data.get("meta").get("owner_type").lower()
        self.assertEqual(owner_type, "site")

    @patch_permissions
    def test_filter_by_wrong_owner(self, _):
        """
        Used to test getting a tag given an undefined type of owner. This returns an empty
        queryset.
        """
        query_params = {
            "owner_type": "course",
        }

        response = self.client.get(self.URL, query_params)

        data = response.json().get("results")
        self.assertFalse(data)

    @patch_permissions
    def test_filter_by_type(self, _):
        """Used to test getting a tag given its target."""
        query_params = {
            "target_type": "user",
        }

        response = self.client.get(self.URL, query_params)

        self.assertEqual(response.status_code, 200)

    @patch_permissions
    def test_soft_delete(self, _):
        """Used to test a tag soft deletion."""
        response = self.client.delete(self.URL_DETAILS)

        self.assertEqual(response.status_code, 204)

    @patch_permissions
    def test_getting_meta_field(self, _):
        """Used to test getting tag most important technical information."""
        response = self.client.get(self.URL_DETAILS)

        data = response.json().get("meta")
        self.assertIsNotNone(data)
        self.assertEqual(data.get("target_id"), str(self.example_tag.target_object))
        self.assertEqual(data.get("target_type"), self.example_tag.target_object_type)
        self.assertEqual(data.get("owner_id"), str(self.example_tag.owner_object))
        self.assertEqual(data.get("owner_type"), self.example_tag.target_object_type)

    @patch_permissions
    def test_retreive_inactive_tag(self, _):
        """Used to test getting a tag given its key."""
        self.client.delete(self.URL_DETAILS)
        response = self.client.get(self.URL_DETAILS)

        self.assertEqual(response.data.get("key").replace("-", ""), self.KEY)
        self.assertEqual(response.data.get("status"), "INACTIVE")

    @patch_permissions
    def test_get_inactive_tag_with_filter(self, _):
        """Used to test getting a tag given its key."""
        query_params = {
            "key": self.KEY,
        }

        self.client.delete(self.URL_DETAILS)
        response = self.client.get(self.URL, query_params)

        data = response.json().get("results")[0]
        self.assertEqual(data.get("status"), "INACTIVE")
        self.assertEqual(data.get("key").replace("-", ""), self.KEY)

    @patch_permissions
    def test_listing_inactive_tags(self, _):
        """Used to test adding inactive tags to the list of tags."""
        query_params = {
            "include_inactive": "true"
        }

        self.client.delete(self.URL_DETAILS)
        response_exclude_inactive = self.client.get(self.URL)
        response_include_inactive = self.client.get(self.URL, query_params)

        exclude_inactive = [tag.get("key") for tag in response_exclude_inactive.json().get("results")]
        include_inactive = [tag.get("key") for tag in response_include_inactive.json().get("results")]
        serialized_tag = TagSerializer(self.example_tag).data
        self.assertNotIn(serialized_tag.get("key"), exclude_inactive)
        self.assertIn(serialized_tag.get("key"), include_inactive)
