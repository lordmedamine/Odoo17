from odoo import models, fields, api

class CarVehicle(models.Model):
    _name = 'car.agency'
    _description = 'Car Agency'

    name = fields.Char()
    responsible_id = fields.Many2one('res.partner', required=True, string='Responsible Person')
    responsible_mail = fields.Char(related='responsible_id.email', string='Res Mail', store=True)

    car_ids = fields.One2many('car.vehicle', 'agency_id', string='Cars')
    brand_id = fields.Many2many('car.brand', string='Brand')

    _sql_constraints = [
        ('responsible_id_not_null', 'CHECK(responsible_id IS NOT NULL)', 'The responsible person must be specified!')
    ]

    def action_view_cars(self):
        """
         will send user to the related car form
         :return: action
         """
        action = self.env.ref('car_agency_management.car_vehicle_view_action').read()[0]
        action['domain'] = [('agency_id', '=', self.id)]
        return action