"""
Tests for hsmapper.core app
"""

from BeautifulSoup import BeautifulSoup
import json

from hsmapper.core.tests_helpers import BaseTestCase
from hsmapper.core.models import Facility, FacilityType


class NavigationTest(BaseTestCase):
    def test_logged_user(self):
        with self.superuser_login():
            response = self.get("index")
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Logged in as admin" in response.content)
            self.assertTrue("globals.username = " in response.content)

    def test_not_logged_user(self):
        response = self.get("index")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Logged in as" not in response.content)
        self.assertTrue("globals.username = " not in response.content)


class ApiTest(BaseTestCase):
    def test_get_hospitals(self):
        response = self.get("api-get-hospitals")
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.content)
        self.assertEqual(len(json_data["features"]), 15)
        feature = json_data["features"][0]

        for attr in ["geometry", "id", "properties"]:
            self.assertTrue(attr in feature)

    def test_get_hospital_info(self):
        response = self.get("api-info-hospital", 999)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Not found" in response.content)

        response = self.get("api-info-hospital", Facility.objects.all()[0].pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Not found" not in response.content)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.findAll("p")), 13)
        self.assertTrue(len(soup.findAll("span", {"class": "edit"})) > 0)

    def test_add_hospital(self):
        Facility.objects.all().delete()

        lat, lon = (4573151.1244973, 1405829.8812908)
        plat, plon = (4207169.978382852, 818856.3261896693)  # projected
        response = self.post("api-add-hospital", data={"lat": lat, "lon": lon})
        self.assertEqual(response.status_code, 401)

        with self.superuser_login():
            response = self.get("api-add-hospital")
            self.assertEqual(response.status_code, 405)

            response = self.post("api-add-hospital")
            self.assertEqual(response.status_code, 200)
            json_response = json.loads(response.content)
            self.assertFalse(json_response["success"])

            response = self.post("api-add-hospital",
                                 data={"lat": lat, "lon": lon})
            self.assertEqual(response.status_code, 200)
            obj = Facility.objects.get()
            json_response = json.loads(response.content)
            self.assertTrue(json_response["success"])
            self.assertEqual(obj.pk, int(json_response["id"]))
            self.assertEqual(obj.the_geom.coords, (plon, plat))

    def test_delete_hospital(self):
        pk_to_delete = Facility.objects.all()[0].pk
        response = self.post("api-delete-hospital", pk_to_delete)
        self.assertEqual(response.status_code, 401)

        with self.superuser_login():
            response = self.get("api-delete-hospital", pk_to_delete)
            self.assertEqual(response.status_code, 405)

            response = self.post("api-delete-hospital", 999)
            self.assertEqual(response.status_code, 200)
            json_response = json.loads(response.content)
            self.assertFalse(json_response["success"])

            response = self.post("api-delete-hospital", pk_to_delete)
            self.assertEqual(response.status_code, 200)
            with self.assertRaises(Facility.DoesNotExist):
                Facility.objects.get(pk=pk_to_delete)
            json_response = json.loads(response.content)
            self.assertTrue(json_response["success"])

    def _test_edit_hospital_data(self, key, param=None):
        response = self.get("api-edit-hospital-data", key)
        self.assertEqual(response.status_code, 401)

        with self.superuser_login():
            if param:
                response = self.get("api-edit-hospital-data", key, param=param)
            else:
                response = self.get("api-edit-hospital-data", key)
            self.assertEqual(response.status_code, 200)

        return json.loads(response.content)

    def test_edit_hospital_data_type(self):
        json_response = self._test_edit_hospital_data("type")
        self.assertEqual(len(json_response), len(FacilityType.objects.all()))

        a_type = FacilityType.objects.all()[0]
        self.assertEqual(json_response[str(a_type.pk)], a_type.name)

    def test_edit_hospital_data_manager(self):
        json_response = self._test_edit_hospital_data("manager")
        self.assertEqual(len(json_response), len(Facility.objects.all()) + 1)
        a_facility = Facility.objects.all()[0]
        self.assertEqual(json_response[str(a_facility.pk)],
                         unicode(a_facility))

    def test_edit_hospital_data_pathology(self):
        json_response = self._test_edit_hospital_data("pathology", {})
        self.assertEqual(json_response, {})

        param = {"q": "olog"}
        json_response = self._test_edit_hospital_data("pathology", param)
        self.assertTrue(len(json_response["results"]) == 2)

    def test_edit_hospital_data_service(self):
        json_response = self._test_edit_hospital_data("service", {})
        self.assertEqual(json_response, {})

        param = {"q": "hosp"}
        json_response = self._test_edit_hospital_data("service", param)
        self.assertTrue(len(json_response["results"]) == 1)
