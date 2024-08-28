from datetime import timedelta

from odoo import models, fields , api


class CarHistory(models.Model):
    _name = "car.history"
    _rec_name = "display_name"

    client = fields.Many2one('res.partner')
    car_id = fields.Many2one('car.vehicle')
    agency = fields.Many2one('car.agency')

    car_RN= fields.Char(related="car_id.registration_number")
    start_date = fields.Date()
    end_date = fields.Date()
    rent_duration = fields.Integer()
    rent_end = fields.Date()

    # Computed field for record name
    display_name = fields.Char(compute='_compute_display_name', store=True, string='Display Name')

    def action_view_car(self):
        """
        will send user to related car form
        :return : action
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.car_id.id,
            'res_model': 'car.vehicle',
            'target': 'current',
        }

    def action_view_customer(self):
        """
        will send user to relater customer form
        :return:view form
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.client.id,
            'res_model': 'res.partner',
            'target': 'current',
        }


    @api.depends('car_RN')
    def _compute_display_name(self):
        """
        set the display name for the rec_name to car registration number
        """
        for rec in self:
            rec.display_name = f"{rec.car_RN}"

    @api.model
    def create(self, vals):
        """
        once a car history is created end_date will be calculated
        based on start_date and duration of the rent
        """
        if 'start_date' in vals and 'rent_duration' in vals:
            start_date = fields.Date.from_string(vals['start_date'])
            end_date = start_date + timedelta(days=vals['rent_duration'])
            vals['end_date'] = fields.Date.to_string(end_date)


        # Create the history record
        record = super(CarHistory, self).create(vals)


        return record