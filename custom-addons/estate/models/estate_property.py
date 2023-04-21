from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    # Private Attributes
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "Expected price cannot be negative or zero",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price >= 0)",
            "The offer price must be positive",
        ),
    ]

    # Custom method for date availability field
    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    # Fields
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From",
        default=lambda self: self._default_date_availability(),
        copy=False,
        help="When will the property be available?",
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", copy=False, readonly=True)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")

    # Selection fields
    garden_orientation = fields.Selection(
        selection=[
            ("N", "North"),
            ("S", "South"),
            ("E", "East"),
            ("W", "West"),
        ],
        string="Garden Orientation",
        help="Which direction is the garden facing?",
    )
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
        help="At what stage the process is in",
    )
    # Special field
    active = fields.Boolean(
        "Active", default=True, help="Special field, turn the record On or Off"
    )

    # Relations
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    user_id = fields.Many2one(
        "res.users", string="Salesman", default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one("res.partner", string="Buyer", readonly=True, copy=False)
    tag_ids = fields.Many2many(
        "estate.property.tag", string="Tags", help="Example: Cozy, Warm, Modern etc."
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # Computed
    total_area = fields.Integer(
        "Total Area (sqm)",
        compute="_compute_total_area",
        help="Total area = Garden area + Living area.",
    )
    best_price = fields.Float(
        "Best Offer", compute="_compute_best_price", help="Best offer received"
    )

    # Methods for Computed Fields
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for prop in self:
            prop.best_price = (
                max(prop.offer_ids.mapped("price")) if prop.offer_ids else 0.0
            )

    # Onchange triggers & constraints
    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for prop in self:
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(
                    prop.selling_price,
                    prop.expected_price * 90.0 / 100.0,
                    precision_rounding=0.01,
                )
                < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "N"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # CRUD Methods
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled properties can be deleted.")

    # Actions
    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("You cannot sell a cancelled property..")
        return self.write({"state": "sold"})

    def action_cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("You cannot cancel a sold property.")
        return self.write({"state": "canceled"})
