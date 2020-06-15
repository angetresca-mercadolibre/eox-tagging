"""
Test classes for Tags model
"""
import datetime

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase, override_settings

from eox_tagging.constants import AccessLevel
from eox_tagging.models import Tag
from eox_tagging.test_utils import CourseEnrollments, CourseOverview


@override_settings(
    EOX_TAGGING_DEFINITIONS=[
        {
            "tag_type": "example_tag_1",
            "validate_owner_object": {"object": "User"},  # default = Site
            "validate_target_object": {"object": "User"},
            "validate_access": {"equals": "PRIVATE"},
            "validate_tag_value": {"in": ["example_tag_value", "example_tag_value_1"]},
        },
        {
            "tag_type": "example_tag_2",
            "owner_object": "Site",
            "validate_target_object": {"object": "CourseOverview"},
            "validate_tag_value": {"opaque_key": "CourseKey"},
        },
        {
            "tag_type": "example_tag_3",
            "validate_tag_value": {"regex": r".*eduNEXT$"},
            "validate_target_object": {"object": "CourseEnrollments"},
            "validate_expiration_date": {"exist": True},
        },
        {
            "tag_type": "example_tag_4",
            "validate_tag_value": {"in": ["example_tag_value", "example_tag_value_1"]},
            "validate_resource_locator": {"opaque_key": "CourseKey"},
        },
    ])
@CourseOverview.fake_me
@CourseEnrollments.fake_me
class TestTag(TestCase):
    """Class for testing the Tag model."""

    def setUp(self):
        """ Model setup used to create objects used in tests."""
        self.target_object = User.objects.create(username="Tag")
        self.owner_object = User.objects.create(username="User")
        self.fake_owner_object = Site.objects.create()
        self.fake_object_target_course = CourseOverview.objects.create()  # pylint: disable=no-member
        self.fake_object_target_enroll = CourseEnrollments.objects.create()  # pylint: disable=no-member

        self.test_tag = Tag.objects.create(
            tag_value="example_tag_value",
            tag_type="example_tag_1",
            target_object=self.target_object,
            owner_object=self.owner_object,
            access=AccessLevel.PRIVATE,
        )

        Tag.objects.create(
            tag_value="course-v1:demo-courses+DM101+2017",
            tag_type="example_tag_2",
            target_object=self.fake_object_target_course,
            owner_object=self.fake_owner_object,
        )

    @override_settings(
        EOX_TAGGING_DEFINITIONS=[
            {
                "tag_type": "example_tag_4",
                "validate_tag_value": {"belongs": ["example_tag_value", "example_tag_value_1"]},
                "validate_resource_locator": {"opaque_key": "CourseKey"},
            }
        ])
    def test_bad_validation_config(self):
        """Used to check that if the config is not correct, then """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="course-v1:demo-courses+DM101+2017",
                tag_type="example_tag_2",
                target_object=self.fake_object_target_course,
                owner_object=self.fake_owner_object,
            )

    @override_settings(
        EOX_TAGGING_DEFINITIONS=[
            {
                "tag_type": "example_tag_4",
                "validate_tag_name": {"in": ["example_tag_value", "example_tag_value_1"]},
                "validate_resource_locator": {"opaque_key": "CourseKey"},
            }
        ])
    def test_bad_field_config(self):
        """Used to check that if the config is not correct, then """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="course-v1:demo-courses+DM101+2017",
                tag_type="example_tag_2",
                target_object=self.fake_object_target_course,
                owner_object=self.fake_owner_object,
            )

    @override_settings(EOX_TAGGING_DEFINITIONS=[])
    def test_empty_setting(self):
        """
        Used to test saving without validations defined.
        If the definitions array is empty then the tag cannot be created.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="example_tag_1",
                tag_type="example_tag_value",
                target_object=self.target_object,
                owner_object=self.owner_object,
            )

    def test_valid_tag(self):
        """ Used to confirm that the tags created are valid."""
        tag_status = getattr(self.test_tag, "status")

        self.assertEqual(tag_status, 1)

    def test_tag_value(self):
        """ Used to confirm that the tag_value is correct."""
        tag_value = getattr(self.test_tag, "tag_value")

        self.assertEqual(tag_value, "example_tag_value")

    def test_tag_type(self):
        """ Used to confirm that the tag_type is correct."""
        tag_value = getattr(self.test_tag, "tag_type")

        self.assertEqual(tag_value, "example_tag_1")

    def test_tag_value_not_in_settings(self):
        """
        Used to confirm validation error when the value is not defined in settings.
        If the key validate_tag_value or tag_value is defined in the config settings
        of the tag, then tag_value must exist or match the validation defined.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="testValues",
                tag_type="example_tag_1",
                target_object=self.target_object,
                owner_object=self.owner_object,
            )

    def test_tag_type_not_in_settings(self):
        """
        Used to confirm validation error when the value is not defined in settings.
        Due to tag_type is a required field, it must exist in any case and match the
        value defined.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="testValue",
                tag_type="testTypes",
                target_object=self.target_object,
                owner_object=self.owner_object,
            )

    def test_tag_different_generic_objects_fail(self):
        """
        Used to confirm that tags can't be created if the target_object does not match
        the definition.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="course-v1:demo-courses+DM101+2017",
                tag_type="example_tag_2",
                target_object=self.fake_object_target_enroll,
                owner_object=self.fake_owner_object,
            )

    def test_tag_validation_regex_accepts_pattern(self):
        """ Used to confirm that tags can accept a pattern if defined in settings."""
        Tag.objects.create(
            tag_value="example by eduNEXT",
            tag_type="example_tag_3",
            target_object=self.fake_object_target_enroll,
            owner_object=self.fake_owner_object,
            expiration_date=datetime.date(2020, 10, 19),
        )

    def test_tag_validation_regex_accepts_pattern_fail(self):
        """ Used to confirm that saving fails if tag does not match pattern defined in settings."""
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="example by edx",
                tag_type="example_tag_3",
                target_object=self.fake_object_target_enroll,
                owner_object=self.owner_object,
                expiration_date=datetime.date(2020, 10, 19),
            )

    def test_tag_inmutable(self):
        """ Used to confirm that the tags can't be updated."""
        setattr(self.test_tag, "tag_value", "value")
        with self.assertRaises(ValidationError):
            self.test_tag.save()

    def test_find_by_owner(self):
        """ Used to confirm that can retrieve tags by owner_object."""
        tags_owned = Tag.objects.find_by_owner(self.owner_object)
        tags_owned_fake = Tag.objects.find_by_owner(self.fake_owner_object)

        self.assertEqual(tags_owned.first().owner_object_id, self.owner_object.id)
        self.assertEqual(tags_owned_fake.first().owner_object_id, self.fake_owner_object.id)

    def test_find_all_tags_for(self):
        """Used to confirm that can retrieve tags by target object."""
        tags = Tag.objects.find_all_tags_for(self.target_object)
        tags_fake = Tag.objects.find_all_tags_for(self.fake_object_target_course)

        self.assertEqual(tags.first().target_object_id, self.target_object.id)
        self.assertEqual(tags_fake.first().target_object_id, self.fake_object_target_course.id)

    def test_tag_soft_delete(self):
        """ Used to confirm that the tags can be invalidated soft deleting them."""
        self.test_tag.delete()

        with self.assertRaises(ObjectDoesNotExist):
            Tag.objects.valid().get(id=1)

        # Exists in invalid objects
        Tag.objects.invalid().get(id=1)

    def test_only_resource_locator(self):
        """
        Used to test that a tag can be created using as the `target object` a resource locator.
        This means that target_object can be None. For this, EOX_TAGGING_DEFINITIONS must not contain
        a definition for target_object.
        """
        Tag.objects.create(
            tag_value="example_tag_value",
            tag_type="example_tag_4",
            owner_object=self.fake_owner_object,
            resource_locator="course-v1:demo-courses+DM101+2017",
        )

    def test_resource_locator_validation_fail(self):
        """
        Used to test that if added to settings a resource locator can be validated as a course_key.
        Given that the resource_locator it's not a course_key, it raises a validation error.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="example_tag_value",
                tag_type="example_tag_4",
                owner_object=self.fake_owner_object,
                resource_locator="resourceLocatorFail",
            )

    def test_create_tag_without_resource_or_target_object(self):
        """
        Used to test that a tag can't be created without a resource locator or
        a model.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="example_tag_value",
                tag_type="example_tag_4",
                owner_object=self.fake_owner_object,
            )

    def test_create_without_default_owner(self):
        """
        Used to test that if the configuration does not have an owner defined, then
        the tag must belong to a site.
        """
        with self.assertRaises(ValidationError):
            Tag.objects.create(
                tag_value="example_tag_value",
                tag_type="example_tag_4",
                owner_object=self.owner_object,  # Owner type: user
                resource_locator="course-v1:demo-courses+DM101+2017",
            )
