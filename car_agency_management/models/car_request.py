from datetime import timedelta
from odoo import models, fields, api


class CarRequest(models.Model):
    _name = 'car.request'
    _description = 'Car Request'
    _rec_name = 'display_name'

    # Computed field for record name
    display_name = fields.Char(compute='_compute_display_name', store=True, string='Display Name')

    available_car = fields.Many2one('car.vehicle', 'Car', domain=[('status', '=', 'available')])
    invoice_id = fields.One2many('car.invoice','request_ids')

    customer_id = fields.Many2one('res.partner', 'Customer',groups="car_agency_management.admin_group")

    car_agency = fields.Many2one('car.agency',related="available_car.agency_id",string ='Agency')
    responsible_mail = fields.Char(related='car_agency.responsible_mail', string='Res Mail', store=True)


    car_name = fields.Char(related='available_car.display_name')



    status = fields.Selection(
        [('draft', 'Draft'),
         ('pending', 'Pending'),
         ('confirmed', 'Confirmed'),
         ('refused', 'Refused')],
        default="draft"
    )

    start_date = fields.Date()
    rent_duration = fields.Integer()
    end_date = fields.Date()

    def action_draft_request(self):
        for record in self:
            record.status = 'draft'

    @api.depends('car_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.car_name} "

    @api.onchange('start_date', 'rent_duration')
    def _onchange_dates(self):
        if self.start_date and self.rent_duration:
            end_date = self.start_date + timedelta(days=self.rent_duration)
            self.end_date = fields.Date.to_string(end_date)

    def action_send_request(self):
        """
        Customer will send a request to rent the selected
        car and wait for respond from admin he will get a mail to tell
        him that request was sent and wait for confirmation
        """
        for record in self:
            if record.status == 'draft':
                record.status = 'pending'
                self.send_car_request_email()

    def action_confirm_request(self):
        """ admin will confirm the customer request
        a history will be created and car status will be changed to rented
        :return:invoice_view_form
        """
        for record in self:
            record.available_car.status="rented"
            record.available_car.start_date=self.start_date
            record.available_car.end_date = self.start_date + timedelta(days=self.rent_duration)
            if record.status == 'pending':
                record.status = 'confirmed'
                self.create_history_record()
                invoice = self.env['car.invoice'].create({
                    'rent_duration':self.rent_duration,
                    'invoice_type': 'rent',
                    'car_id': self.available_car.id,
                    'customer_id': self.customer_id.id,
                    'request_ids': self.id
                })
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_id': invoice.id,
                    'res_model': 'car.invoice',
                    'target': 'current',
                }

    def check_invoice(self):
        """
        user will be sent to the invoice form related to the request made
        :return:invoice view form
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'res_model': 'car.invoice',
            'target': 'current',
        }




    def create_history_record(self):
        """
        creating the car history
        :return:car_history
        """
        for rec in self:
            rec.env['car.history'].create({
                'client': self.customer_id.id,
                'car_id': self.available_car.id,
                'agency': self.car_agency.id,
                'start_date': self.start_date,
                'rent_duration': self.rent_duration,
            })

    def action_decline_request(self):
        """
        change request status to refused if request is declined
        """
        for record in self:
            if record.status == 'pending':
                record.status = 'refused'


    def send_car_request_email(self):
        """
        process to send the mail to the use once he will submit his request
        :return:mail
        """
        # Get the email template
        template = self.env.ref('car_agency_management.car_request_email_template')

        # Ensure that the template exists
        if template:
            # Send the email for each record in the self
            for request in self:
                template.send_mail(request.id, force_send=True)
                print('mail sent ')

    def unlink(self):
        """
        changing car status to available once a request is deleted
        """
        for rec in self:
            rec.available_car.status='available'
        res = super(CarRequest, self).unlink()
        return res