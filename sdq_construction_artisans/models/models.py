# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _, time
from odoo.exceptions import UserError


class sdq_construction_artisans(models.Model):
    _name = 'construction.artisans'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('construction.artisans') or _('New')
        result = super(sdq_construction_artisans, self).create(vals)
        return result

    name_seq = fields.Char(string='ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))

    name = fields.Char(string="Nom De l'Artisans", track_visibility="always", required=True)
    project_id = fields.Char(string="project", required=True)
    category = fields.Char(string="Departement", track_visibility="always")
    date = fields.Date('Date de signature', track_visibility="always", required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    company_id = fields.Many2one(
        'res.company', readonly='True', string='Société',
        default=lambda self: self.env['res.company']._company_default_get())
    notes = fields.Text(string="Déscription")
    signed_contract = fields.Binary(string="Document signé", track_visibility="always")
    order_line = fields.One2many('construction.artisans.order.lines', 'order_id')
    # state = fields.Selection([
    #     ('en cours', 'En Cours'),
    #     ('payée', 'Payée'),
    # ], string='Status', readonly=True, default='en cours')
    state = fields.Selection([
        ('en cours', 'En Cours'),
        ('paid', 'Paid'),
    ], string='Status', readonly=True, default='en cours')
    # order_id = fields.Many2one('product.template', string='Order Reference', index=True)
    agreed_amount = fields.Float(string="Agreed Amount", track_visibility="always")
    advance_amount = fields.Float(string="Totale des avances", track_visibility="always", readonly=True,
                                  compute='compute_advances_subtotal')
    rest_amount = fields.Float(string=' Totale Restant', track_visibility="always", readonly=True,
                               compute='compute_rest_total')

    def action_confirm(self):
        for rec in self:
            rec.state = 'en cours'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Appointment Confirmed... Thanks You',
                    'type': 'rainbow_man',
                }
            }

    def action_done(self):
        for rec in self:
            rec.state = 'en cours'

    @api.depends('agreed_amount', 'advance_amount', 'rest_amount')
    def compute_rest_total(self):
        if self.agreed_amount > self.advance_amount:
            self.rest_amount = self.agreed_amount - self.advance_amount
        elif self.agreed_amount < self.advance_amount:
            raise UserError(_("Sorry! Agreed Amount must be greather than Advanced Amount"))

    @api.depends('order_line')
    def compute_advances_subtotal(self):
        self.advance_amount = 0
        if self.order_line:
            self.advance_amount = sum(self.order_line.mapped('total_amount'))


class construction(models.Model):
    _name = 'construction.artisans.order.lines'

    artisan_name = fields.Char(string="Nom De l'Artisan", readonly=True)
    date = fields.Date('Date', track_visibility="always", required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    avance = fields.Float(string="Price")
    motif = fields.Text(string="Motif")
    total_amount = fields.Float(string="Montant")
    order_id = fields.Many2one('construction.artisans.order.lines', string='Order Reference', index=True)

