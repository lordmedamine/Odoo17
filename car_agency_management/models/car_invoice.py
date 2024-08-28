from datetime import datetime, timedelta

from odoo import models, fields, api

class CarInvoice(models.Model):
    _name = 'car.invoice'
    _description = 'Car Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    invoice_type = fields.Selection([('rent', 'Rent Payment'), ('maintenance', 'Maintenance Payment')], readonly=True)

    maintenance_ids = fields.Many2one('car.maintenance', 'invoice_id')
    request_ids = fields.Many2one('car.request', 'invoice_id')

    invoice_id = fields.Char()
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.context_today, readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    car_id = fields.Many2one(
        'car.vehicle',
        string='Car'
        , readonly=True    )
    agency_id = fields.Many2one('car.agency', related="car_id.agency_id", string='Agency')
    rental_start_date = fields.Date(
        string='Rental Start Date',
        related='car_id.start_date',
        readonly=True
    )
    rental_end_date = fields.Date(
        string='Rental End Date',
        related='car_id.end_date',
        readonly=True
    )
    rent_duration = fields.Integer()
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', readonly=True)
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ], string='Payment Status', default='pending', required=True)
    due_date = fields.Date(string='Due Date')

    day_coast = fields.Float(string='Price Per Day', compute='_compute_day_coast')

    @api.depends('car_id')
    def _compute_day_coast(self):
        """
        get car daily cost from the config based on the
        car ranting
        """
        # Define the mapping between average rating and price fields
        rating_to_price_field = {
            'awful': 'zero_star_price',
            'very_bad': 'one_star_price',
            'bad': 'two_star_price',
            'normal': 'three_star_price',
            'good': 'four_star_price',
            'very_good': 'five_star_price',
        }

        for record in self:
            if record.car_id:
                star_rating = record.car_id.average_rating

                price_field = rating_to_price_field.get(star_rating, 'default_price')

                config_settings = self.env['ir.config_parameter'].sudo()
                price = float(config_settings.get_param(f'car_agency_management.{price_field}', default=0.0))
                record.day_coast = price

    @api.depends('day_coast')
    def _compute_total_amount(self):
        """
        calculate the total amount to pay
        based on the rent duration and daily coast
        """
        for record in self :
            record.total_amount=record.day_coast*record.rent_duration

    def rent_duration_mail(self):
        """
        a mail will be sent to user one the rent will
        end within 1 day as a reminder
        :return :mail
        """
        print('mail sent')
        for record in self:
            today = datetime.now()
            end_date = datetime.now() + timedelta(days=1)
            if end_date == today:
                template = self.env.ref('car_agency_management.car_reminder_email_template')
                if template:
                    template.send_mail(record.id, force_send=True)
                    print('mail sent')

        
        
        
    def action_view_report(self):
        """
        invoice report
        :return : action
        """
        return self.env.ref('car_agency_management.invoice_report').report_action(self)




class InvoiceLine(models.Model):
    _name = 'invoice.line'
