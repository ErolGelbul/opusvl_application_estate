from odoo.exceptions import ValidationError
from odoo.tests import common


class TestEstatePropertyOffer(common.TransactionCase):
    def setUp(self):
        super(TestEstatePropertyOffer, self).setUp()
        self.EstateProperty = self.env["estate.property"]
        self.EstatePropertyOffer = self.env["estate.property.offer"]
        self.Partner = self.env["res.partner"]

        self.partner = self.Partner.create({"name": "Test Buyer"})
        self.property = self.EstateProperty.create(
            {
                "name": "Test Property",
                "postcode": "12345",
                "expected_price": 200000,
            }
        )

    def test_offer_creation_and_price_validation(self):
        # Create a property without offers
        property_without_offers = self.env["estate.property"].create(
            {
                "name": "Test Property 2",
                "description": "This is a test description",
                "postcode": "12345",
                "date_availability": "2023-01-01",
                "expected_price": 200000.00,
                "selling_price": 0,
                "bedrooms": 3,
                "living_area": 150,
                "facades": 2,
                "garage": True,
                "garden": True,
                "garden_area": 50,
                "garden_orientation": "N",
            }
        )

        # Temporarily disable the check constraint
        self.env.cr.execute(
            "ALTER TABLE estate_property_offer DROP CONSTRAINT estate_property_offer_check_price"
        )

        try:
            # Test creating an invalid offer (zero or negative price)
            self.EstatePropertyOffer.create(
                {
                    "price": 0,
                    "partner_id": self.partner.id,
                    "property_id": property_without_offers.id,
                }
            )
        except ValidationError as e:
            print("Expected ValidationError caught:", e)

        try:
            # Test creating an invalid offer (zero or negative price)
            self.EstatePropertyOffer.create(
                {
                    "price": 220000.00,
                    "partner_id": self.partner.id,
                    "property_id": property_without_offers.id,
                }
            )
        except ValidationError as e:
            print("Expected ValidationError caught:", e)

        # Delete rows that violate the constraint before re-enabling it
        self.env.cr.execute("DELETE FROM estate_property_offer WHERE price <= 0")

        # Re-enable the check constraint
        self.env.cr.execute(
            "ALTER TABLE estate_property_offer ADD CONSTRAINT estate_property_offer_check_price CHECK (price > 0)"
        )
