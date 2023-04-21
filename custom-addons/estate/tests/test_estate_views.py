from odoo.tests import common


class TestEstateViews(common.TransactionCase):
    def setUp(self):
        super(TestEstateViews, self).setUp()
        self.EstateProperty = self.env["estate.property"]

    def test_views_load(self):
        """Test if the views are loaded properly."""
        property_views = [
            "estate.estate_property_view_form",
            "estate.estate_property_view_tree",
            "estate.estate_property_view_search",
            "estate.estate_property_view_kanban",
        ]

        for view_ref in property_views:
            view_id = self.env.ref(view_ref)
            self.assertTrue(view_id.exists(), f"View '{view_ref}' not found.")
            self.EstateProperty.with_context(view_id=view_id.id).search([], limit=10)
