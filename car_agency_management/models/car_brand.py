from odoo import models, fields, api


class CarBrand(models.Model):
    _name = 'car.brand'
    _rec_name = 'display_name'

    name = fields.Char(required=True, string='Brand Name')
    image = fields.Binary(string='Logo')
    description = fields.Text(string='Description')
    agency_ids = fields.Many2many('car.agency', string='Agencies', required=True)


    # New
    country_of_origin = fields.Selection([("germany","Germany"),("usa","USA"),("uk","UK")],string="Origin")
    created_date = fields.Date(string="Date Creation" ,readonly=True)
    modified_date = fields.Date(string="Last Modified", readonly=True, default=fields.Datetime.now)


    # Computed field for record name
    display_name = fields.Char(compute='_compute_display_name', store=True, string='Display Name')

    def action_view_cars(self):
        """will send user to the related car form"""
        action = self.env.ref('car_agency_management.car_vehicle_view_action').read()[0]
        action['domain'] = [('brand_id', '=', self.id)]
        return action

    @api.depends('name')
    def _compute_display_name(self):
        """set the _rec_name to the brand name"""
        for rec in self:
            rec.display_name = f"{rec.name}"


    #NEW
    @api.model
    def create(self, vals):
        """
        once a brand is created will set date creation and
        modified date to current date
        :return:car_Brand
        """
        vals['created_date'] = fields.Datetime.now()
        vals['modified_date'] = fields.Datetime.now()
        return super(CarBrand, self).create(vals)

    def write(self, vals):
        """
        once a brand is modified will set a car modified date to current date
        :return:car_brand
        """
        vals['modified_date'] = fields.Datetime.now()
        return super(CarBrand, self).write(vals)