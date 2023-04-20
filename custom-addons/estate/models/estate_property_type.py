from odoo import fields, models


class EstatePropertyType(models.Model):
    # Private Attributes
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique"),
    ]

    # Fields
    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence", default=10)

    # Relatios
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )

    # Computed
    # offer count based on type
    offer_count = fields.Integer(string="Number of Offers", compute="_compute_offer")

    # Relation + Computed
    # offer id based on type
    offer_ids = fields.Many2many(
        "estate.property.offer", string="Offers", compute="_compute_offer"
    )

    # Compute Methods
    # This took a while...
    def _compute_offer(self):
        data = self.env["estate.property.offer"].read_group(
            [
                ("property_id.state", "!=", "canceled"),
                ("property_type_id", "!=", False),
            ],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {
            d["property_type_id"][0]: d["property_type_id_count"] for d in data
        }
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])

    # My first implementation, why is it bad? It makes a distinct search query
    # for each property type so if you have a lot of offers it will be slow.
    # def _compute_offer(self):
    #     offer_obj = self.env["estate.property.offer"]

    #     for prop_type in self:
    #         # Filtering offers with the current property type and not canceled state
    #         offers = offer_obj.search([
    #             ("property_id.state", "!=", "canceled"),
    #             ("property_type_id", "=", prop_type.id)
    #         ])

    #         prop_type.offer_count = len(offers)
    #         prop_type.offer_ids = [(6, 0, offers.ids)]

    # Action Method
    # filter offers related to current property
    def action_view_offers(self):
        res = self.env.ref("estate.estate_property_offer_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res
