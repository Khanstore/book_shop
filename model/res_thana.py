from odoo import fields, models, api, _


# class CountryState(models.Model):
#     _description = "Country state"
#     _name = 'res.country.state'
#     _order = 'code'
#     _rec_names_search = ['name', 'code']
#
#     country_id = fields.Many2one('res.country', string='Country', required=True)
#     name = fields.Char(string='State Name', required=True,
#                help='Administrative divisions of a country. E.g. Fed. State, Department, Canton')
#     code = fields.Char(string='State Code', help='The state code.', required=True)
#
#     _sql_constraints = [
#         ('name_code_uniq', 'unique(country_id, code)', 'The code of the state must be unique by country!')
#     ]
#
#     @api.model
#     def name_search(self, name='', args=None, operator='ilike', limit=100):
#         result = []
#         domain = args or []
#         # first search by code (with =ilike)
#         if operator not in expression.NEGATIVE_TERM_OPERATORS and name:
#             states = self.search_fetch(expression.AND([domain, [('code', '=like', name)]]), ['display_name'], limit=limit)
#             result.extend((state.id, state.display_name) for state in states.sudo())
#             domain = expression.AND([domain, [('id', 'not in', states.ids)]])
#             if limit is not None:
#                 limit -= len(states)
#                 if limit <= 0:
#                     return result
#         # normal search
#         result.extend(super().name_search(name, domain, operator, limit))
#         return result
#
#     @api.model
#     def _search_display_name(self, operator, value):
#         domain = super()._search_display_name(operator, value)
#         if value and operator not in expression.NEGATIVE_TERM_OPERATORS:
#             if operator in ('ilike', '='):
#                 domain = expression.OR([
#                     domain, self._get_name_search_domain(value, operator),
#                 ])
#             elif operator == 'in':
#                 domain = expression.OR([
#                     domain,
#                     *(self._get_name_search_domain(name, '=') for name in value),
#                 ])
#         if country_id := self.env.context.get('country_id'):
#             domain = expression.AND([domain, [('country_id', '=', country_id)]])
#         return domain
#
#     def _get_name_search_domain(self, name, operator):
#         m = re.fullmatch(r"(?P<name>.+)\((?P<country>.+)\)", name)
#         if m:
#             return [
#                 ('name', operator, m['name'].strip()),
#                 '|', ('country_id.name', 'ilike', m['country'].strip()),
#                 ('country_id.code', '=', m['country'].strip()),
#             ]
#         return [expression.FALSE_LEAF]
#
#     @api.depends('country_id')
#     def _compute_display_name(self):
#         for record in self:
#             record.display_name = f"{record.name} ({record.country_id.code})"

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