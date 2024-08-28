from odoo import models, fields, api

class MaintenanceWizard(models.TransientModel):
    _name = 'maintenance.wizard'
    _description = 'Maintenance Wizard'

    car_id = fields.Many2one('car.vehicle', string='Car', required=True,readonly=True)
    maintenance_date = fields.Date(string='Maintenance Date', required=True, default=fields.Date.today)
    maintenance_type = fields.Selection([
        ('repair', 'Repair'),
        ('service', 'Service'),
        ('inspection', 'Inspection'),
        ('other', 'Other'),
    ], string='Maintenance Type', required=True)
    description = fields.Text(string='Description')

    def create_maintenance(self):
        self.env['car.maintenance'].create({
            'car_id': self.car_id.id,
            'maintenance_date': self.maintenance_date,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
        })


