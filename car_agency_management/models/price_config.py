from odoo import fields, models,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    price = fields.Integer()
    zero_star_price = fields.Integer()
    one_star_price = fields.Integer()
    two_star_price = fields.Integer()
    three_star_price = fields.Integer()
    four_star_price = fields.Integer()
    five_star_price = fields.Integer()

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env['ir.config_parameter'].sudo()
        config_parameters.set_param('car_agency_management.zero_star_price', self.zero_star_price)
        config_parameters.set_param('car_agency_management.one_star_price', self.one_star_price)
        config_parameters.set_param('car_agency_management.two_star_price', self.two_star_price)
        config_parameters.set_param('car_agency_management.three_star_price', self.three_star_price)
        config_parameters.set_param('car_agency_management.four_star_price', self.four_star_price)
        config_parameters.set_param('car_agency_management.five_star_price', self.five_star_price)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameters = self.env['ir.config_parameter'].sudo()
        res.update({
            'zero_star_price': float(config_parameters.get_param('car_agency_management.zero_star_price', default=0.0)),
            'one_star_price': float(config_parameters.get_param('car_agency_management.one_star_price', default=0.0)),
            'two_star_price': float(config_parameters.get_param('car_agency_management.two_star_price', default=0.0)),
            'three_star_price': float(config_parameters.get_param('car_agency_management.three_star_price', default=0.0)),
            'four_star_price': float(config_parameters.get_param('car_agency_management.four_star_price', default=0.0)),
            'five_star_price': float(config_parameters.get_param('car_agency_management.five_star_price', default=0.0)),
        })
        return res


