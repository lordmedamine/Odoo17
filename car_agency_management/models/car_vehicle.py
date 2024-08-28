from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CarVehicle(models.Model):
    _name = 'car.vehicle'
    _description = 'Car Vehicle'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    registration_number = fields.Char(required=True, string='Registration Number')
    model = fields.Char(required=True, string='Model')
    mileage = fields.Float(string='Mileage')
    status = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance','Maintenance')
    ], required=True, string='Status', readonly=True, default="available")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    brand_id = fields.Many2one('car.brand', string='Brand')
    agency_id = fields.Many2one('car.agency', string='Agency',domain="[('brand_id', '=', brand_id)]")
    customer_id = fields.Many2many('res.partner', string="Customer")

    # Computed field to get the brand image
    brand_image = fields.Binary(related='brand_id.image', string='Brand Image', readonly=True)

    # Computed field for record name
    display_name = fields.Char(compute='_compute_display_name', store=True, string='Display Name')

    car_color = fields.Selection([
        ('#FFFFFF', 'White'),
        ('#000000', 'Black'),
        ('#FF0000', 'Red'),
        ('#0000FF', 'Blue'),
        ('#008000', 'Green'),
        ('#808080', 'Gray'),
        ('#C0C0C0', 'Silver'),
        ('#FFFF00', 'Yellow'),
        ('#FFA500', 'Orange'),
        ('#800080', 'Purple')
    ], default='#FFFFFF', string='Car Color')
    maintenance_record = fields.One2many('car.maintenance','car_id',string="Maintenance Record",tracking=1)
    # line_ids = fields.One2many('vehicle.lines', 'car_vehicle',tracking=True)
    history_ids = fields.One2many('car.history', 'car_id',tracking=True)
    # line_ids2 = fields.One2many('vehicle.ratting', 'car_vehicle',tracking=True)
    ratting_lines= fields.One2many('vehicle.ratting', 'vehicle',tracking=True)
    rating = fields.Selection([('awful','Awful'),('very_bad','Very Bad'),('bad','Bad'),('normal','Normal'),('good','Good'),('very_good','Very Good')],default='good',readonly=True)


    #average rating field
    average_rating = fields.Selection([
        ('awful', 'Awful'),
        ('very_bad', 'Very Bad'),
        ('bad', 'Bad'),
        ('normal', 'Normal'),
        ('good', 'Good'),
        ('very_good', 'Very Good')
    ], default='good', compute='_compute_average_rating', store=True)

    _sql_constraints = [
        ('registration_number_unique', 'unique(registration_number)', 'The registration number must be unique!'),
        ('registration_number_length_check', 'CHECK(length(registration_number) = 8)',
         'The registration number must be exactly 8 digits!')
    ]

    def check_date(self):
        """
        to change status to available if rent duration ended
        """
        today = fields.Date.today()
        cars_to_update = self.search([
            ('end_date', '<', today)
        ])
        cars_to_update.write({'status': 'available'})

        properties_to_update = self.search([
            ('end_date', '>=', today)
        ])
        properties_to_update.write({'status': 'rented'})

    @api.constrains('end_date')
    def _check_end_date_geater_than_start_date(self):
        """
        will make sure that rent_end date is after beginning date
        """
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError('end date can\'t be before start date')

    @api.depends('model', 'registration_number')
    def _compute_display_name(self):
        """
        rec_name will be set to model + registration number
        """
        for rec in self:
            rec.display_name = f"{rec.model} - {rec.registration_number}"



    def open_rate_wizard(self):
        """
        open rating wizard
        :return:action
        """
        action = self.env['ir.actions.actions']._for_xml_id('car_agency_management.action_car_rating_wizard')
        action['context'] = {'default_vehicle_id': self.id}
        return action

    #creating a method to create the history lines
    def create_history_line(self,client,rent_date,rent_duration):
        """c
        reating a history line for the car
        :return car_history:
        """
        self.env['vehicle.lines'].create({
            'client':client,
            'rent_date':rent_date,
            'rent_duration':rent_duration,
            'car_vehicle': self.id,
        })

    def maintenance_done(self):
        self.status="available"


    def send_to_maintenance(self):
        self.status="maintenance"
        """
        create a maintenance for the car and change status to maintenance
        :return : action
        """
        action = self.env['ir.actions.actions']._for_xml_id('car_agency_management.action_maintenance_wizard')
        action['context'] = {'default_car_id': self.id}
        return action



    #_compute_average_rating
    @api.depends('ratting_lines.rating_value')
    def _compute_average_rating(self):
        """
        will calculate average rating based on the ratting from users
        :return:average ratting value
        """
        def rating_to_numeric(rating):
            return {
                'awful': 1,
                'very_bad': 2,
                'bad': 3,
                'normal': 4,
                'good': 5,
                'very_good': 6
            }.get(rating, 4)  # Default to 'normal' if not found

        def numeric_to_rating(value):
            if value < 1.5:
                return 'awful'
            elif value < 2.5:
                return 'very_bad'
            elif value < 3.5:
                return 'bad'
            elif value < 4.5:
                return 'normal'
            elif value < 5.5:
                return 'good'
            else:
                return 'very_good'

        for vehicle in self:
            if vehicle.ratting_lines:
                ratings = [rating_to_numeric(line.rating_value) for line in vehicle.ratting_lines]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
                    vehicle.average_rating = numeric_to_rating(avg_rating)
                else:
                    vehicle.average_rating = False
            else:
                vehicle.average_rating = False

    #Fixed the Rating system
    def create_line(self, rating_value, comments, vehicle_id, user_id):
        """
        creating a rating line by user for the current car
        :return:ratting_line
        """
        self.env['vehicle.ratting'].create({
            'rating_user': user_id,
            'rating_value': rating_value,
            'comments': comments,
            'vehicle': vehicle_id,
            'rating_date': fields.Datetime.now(),
        })
        self._compute_average_rating()

    def update_status(self):
        """
        if rent duration ended car status will be back to available
        """
        current_datetime = datetime.now()
        records_to_update = self.search([('end_date', '<', current_datetime), ('status', '==', 'rented')])
        for record in records_to_update:
            record.status = 'available'



class vehicleLines_pagethree(models.Model):
    _name = 'vehicle.ratting'

    car_vehicle = fields.Many2one('car.vehicle')

    # page_thee
    rating_user = fields.Many2one('res.partner')
    rating_value = fields.Selection([('awful','Awful'),('very_bad','Very Bad'),('bad','Bad'),('normal','Normal'),('good','Good'),('very_good','Very Good')],default='good')

    comments = fields.Text()
    vehicle = fields.Many2one('car.vehicle')
    rating_date = fields.Datetime(string='Rating Date', default=fields.Datetime.now)
