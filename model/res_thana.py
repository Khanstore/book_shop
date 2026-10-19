from odoo import fields, models, api, _




class Thana(models.Model):
    _name = 'res.thana'
    _description = 'Thana'
    _order = 'name'

    name = fields.Char(string='Thana Name', required=True ,translate=True)
    state_id = fields.Many2one('res.country.state', string='District', required=True)
    _sql_constraints = [
        ('name_state_uniq', 'unique(state_id, name)', 'The name of the Thana must be unique by District/State!')
    ]

    @api.depends('state_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.state_id.code})"