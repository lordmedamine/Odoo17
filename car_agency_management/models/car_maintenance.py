from email.policy import default

from odoo import models, fields, api

class CarMaintenance(models.Model):
    _name = 'car.maintenance'
    _description = 'Car Maintenance Record'
    _rec_name = 'display_name'

    # Computed field for record name
    display_name = fields.Char(compute='_compute_display_name', store=True, string='Display Name')
    car_name = fields.Char(related='car_id.display_name')

    car_id = fields.Many2one('car.vehicle', string='Car', required=True)
    invoice_id = fields.One2many('car.invoice','maintenance_ids')
    maintenance_date = fields.Date(string='Maintenance Date', required=True, default=fields.Date.today)
    invoice_created = fields.Boolean(default=False)
    maintenance_type = fields.Selection([
        ('repair', 'Repair'),
        ('service', 'Service'),
        ('inspection', 'Inspection'),
        ('other', 'Other'),
    ], string='Maintenance Type', required=True)
    description = fields.Text(string='Description')
    cost = fields.Float(string='Cost')

    def create_invoice(self):
        """
        create the invoice for the current maintenance
        :return:car_invoice
        """
        self.invoice_created = True
        invoice = self.env['car.invoice'].create({
            'car_id': self.car_id.id,
            'total_amount': self.cost,
            'maintenance_ids':self.id,
            'invoice_type':'maintenance'

        })
        print(self.invoice_created)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': invoice.id,
            'res_model': 'car.invoice',
            'target': 'current',
        }

    def check_invoice(self):
        """
        user will be sent to the invoice form related to the current
        maintenance
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'res_model': 'car.invoice',
            'target': 'current',
        }
    @api.depends('car_name')
    def _compute_display_name(self):
        """
        rec_name will be set to car_name
        """
        for rec in self:
            rec.display_name = f"{rec.car_name} "