from odoo import fields, models, api, _


class ResThana(models.Model):
    _name = 'res.thana'
    _description = 'Thana'
    _rec_name = 'name'

    name = fields.Char(string='Thana Name',translate=True, required=True)
    # code = fields.Char(string='Thana Code', required=True, help='Unique code for the Thana')
    state_id = fields.Many2one('res.country.state', string='District',  help='District to which this Thana belongs')
    country_id = fields.Many2one('res.country', string='Country', related='state_id.country_id', store=True,
                                 readonly=True, help='Country to which this Thana belongs')