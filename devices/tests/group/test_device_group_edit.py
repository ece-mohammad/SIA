from test.pages.common import DeviceGroupDetails, DeviceGroupEdit
from test.utils.helpers import client_login, create_member, page_in_response
from typing import *

from django.test import TestCase

from devices.models import DeviceGroup

FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="testpassword",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="testpassword",
)

FIRST_DEVICE_GROUPS_DATA: Final[List[Dict[str, str]]] = [
    dict(
        name="test_group_1",
        description="first member test description 1",
    ),
    dict(
        name="test_group_2",
        description="first member test description 2",
    ),
    dict(
        name="test_group_3",
        description="first member test description 3",
    ),
    dict(
        name="test_group_4",
        description="first member test description 4",
    ),
]

SECOND_DEVICE_GROUPS_DATA: Final[List[Dict[str, str]]] = [
    dict(
        name="test_group_5",
        description="second member test description 5",
    ),
    dict(
        name="test_group_6",
        description="second member test description 6",
    ),
    dict(
        name="test_group_7",
        description="second member test description 7",
    ),
    dict(
        name="test_group_8",
        description="second member test description 8",
    ),
]


class BaseTestDeviceGroupEditTestCase(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.second_member = create_member(**SECOND_MEMBER)

        self.first_device_groups = DeviceGroup.objects.bulk_create(
            [
                DeviceGroup(**group_data, owner=self.first_member)
                for group_data in FIRST_DEVICE_GROUPS_DATA
            ],
            ignore_conflicts=True,
        )

        self.second_device_groups = DeviceGroup.objects.bulk_create(
            [
                DeviceGroup(**group_data, owner=self.second_member)
                for group_data in SECOND_DEVICE_GROUPS_DATA
            ],
            ignore_conflicts=True,
        )

        client_login(self.client, FIRST_MEMBER)

        return super().setUp()


class TestDeviceGroupEditRendering(BaseTestDeviceGroupEditTestCase):
    def test_device_group_edit_rendering(self):
        """Test that device group edit page renders correctly"""
        device_group = self.first_member.devicegroup_set.first()
        response = self.client.get(
            path=DeviceGroupEdit.get_url(group_name=device_group.name), follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(DeviceGroupEdit, response)[0])


class TestDeviceGroupEditForm(BaseTestDeviceGroupEditTestCase):
    def test_device_group_edit_form_fields(self):
        """Test device group edit form fields and their initial data"""
        device_group = self.first_member.devicegroup_set.first()
        response = self.client.get(
            path=DeviceGroupEdit.get_url(group_name=device_group.name), follow=True
        )
        form = response.context.get("form")

        # Check that the form has the correct number of fields and that the correct fields are required.
        self.assertEqual(len(form.fields), 2)
        self.assertEqual(form.fields.get("name").required, True)
        self.assertEqual(form.fields.get("description").required, False)

        # Check that the form's fields have the correct initial values.
        self.assertEqual(form.initial["name"], device_group.name)
        self.assertEqual(form.initial["description"], device_group.description)

    def test_device_group_edit_form_required_name(self):
        """Test that name field is required"""
        device_group = self.first_member.devicegroup_set.first()
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=device_group.name),
            data=dict(name="", description=device_group.description),
        )
        form = response.context.get("form")

        self.assertEqual(response.status_code, 200)
        self.assertFormError(form, "name", ["This field is required."])
        self.assertContains(response, "This field is required.")

    def test_device_group_edit_form_optional_description(self):
        """Test that description field is optional"""
        device_group_name = FIRST_DEVICE_GROUPS_DATA[0]["name"]
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=device_group_name),
            data=dict(
                name=device_group_name,
                description="",
            ),
            follow=True,
        )

        self.assertRedirects(
            response,
            DeviceGroupDetails.get_url(group_name=device_group_name),
            302,
            200,
            fetch_redirect_response=True,
        )


class TestDeviceGroupEditView(BaseTestDeviceGroupEditTestCase):
    def test_device_group_edit_unique_name(self):
        """Test that device group's name must be unique"""
        device_group = self.first_member.devicegroup_set.first()
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=device_group),
            data=dict(
                name=FIRST_DEVICE_GROUPS_DATA[1]["name"],
                description=FIRST_DEVICE_GROUPS_DATA[1]["description"],
            ),
            follow=True,
        )
        form = response.context.get("form")
        device_group.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            form, "name", ["A device group with this name already exists."]
        )
        self.assertContains(response, "A device group with this name already exists.")

        # Check that the device group was not updated
        device_group.refresh_from_db()
        self.assertEqual(device_group.name, FIRST_DEVICE_GROUPS_DATA[0]["name"])
        self.assertEqual(
            device_group.description, FIRST_DEVICE_GROUPS_DATA[0]["description"]
        )

    def test_device_group_edit_changes_name(self):
        """Tets that device group's name is changed to new value"""
        device_group = self.first_member.devicegroup_set.first()
        new_device_group_name = "new_device_group_name"
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=device_group),
            data=dict(
                name=new_device_group_name,
                description=device_group.description,
            ),
            follow=True,
        )
        device_group.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            DeviceGroupDetails.get_url(group_name=new_device_group_name),
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertContains(response, new_device_group_name)
        self.assertEqual(device_group.name, new_device_group_name)

    def test_device_group_edit_changes_description(self):
        """Test that device group's description is changed"""
        device_group_name = FIRST_DEVICE_GROUPS_DATA[0]["name"]
        device_group_desc = "new device group description"
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=device_group_name),
            data=dict(
                name=device_group_name,
                description=device_group_desc,
            ),
            follow=True,
        )
        edited_device_group = DeviceGroup.objects.get(
            name=device_group_name, owner=self.first_member
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            DeviceGroupDetails.get_url(group_name=device_group_name),
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertContains(response, device_group_name)
        self.assertEqual(edited_device_group.name, device_group_name)
        self.assertEqual(edited_device_group.description, device_group_desc)

    def test_device_group_edit_unknown_device_group_404(self):
        """Test that editing a device group that does not exist returns 404"""
        device_group_name = SECOND_DEVICE_GROUPS_DATA[-1]["name"]
        device_group_desc = SECOND_DEVICE_GROUPS_DATA[-1]["description"]
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=device_group_name),
            data=dict(
                name=device_group_name,
                description=device_group_desc,
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)

    def test_device_group_another_member_404(self):
        response = self.client.get(
            path=DeviceGroupEdit.get_url(group_name=self.second_device_groups[0].name),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)

    def test_device_group_edit_no_changed_data(self):
        response = self.client.post(
            path=DeviceGroupEdit.get_url(group_name=self.first_device_groups[0].name),
            data=dict(
                name=self.first_device_groups[0].name,
                description=self.first_device_groups[0].description,
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            DeviceGroupDetails.get_url(group_name=self.first_device_groups[0].name),
            302,
            200,
            fetch_redirect_response=True,
        )
