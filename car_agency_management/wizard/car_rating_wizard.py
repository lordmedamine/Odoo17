from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CarRatingWizard(models.TransientModel):
    _name = 'rating.wizard'
    _description = 'Car Rating Wizard'

    rating_value = fields.Selection([('awful','Awful'),('very_bad','Very Bad'),('bad','Bad'),('normal','Normal'),('good','Good'),('very_good','Very Good')],default='good')

    comments = fields.Text(string='Comments')
    vehicle_id = fields.Many2one('car.vehicle', string='Vehicle', required=True,readonly=True)
    user_id = fields.Many2one('res.partner', string='User', default=lambda self: self.env.user.partner_id,readonly=True)

    # Fixed the Rating system
    def submit_rating(self):
        self.vehicle_id.create_line(
            self.rating_value,
            self.comments,
            self.vehicle_id.id,
            self.user_id.id
        )
        self.vehicle_id._compute_average_rating()
        return {'type': 'ir.actions.act_window_close'}  # Close the wizard