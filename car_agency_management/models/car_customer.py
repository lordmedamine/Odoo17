from odoo import models, fields , api


class CarCustomer(models.Model):
    _inherit = 'res.partner'

    car_ids = fields.Many2many('car.vehicle' , string='Cars')
