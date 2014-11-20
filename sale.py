# -*- coding: utf-8 -*-
##############################################################################
#
#    sale  modify for JoinTD
#    Copyright (C) 2014 xingyun (<http://www.join.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields,osv
from openerp import netsvc
from openerp.tools.translate import _
import logging  # 新增 

logger = logging.getLogger(__name__)  #重新定义

class sale_order(osv.osv):
    
    _inherit = "sale.order"
    def action_cancel(self, cr, uid, ids, context=None):

        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        for sale in self.browse(cr, uid, ids, context=context):
            for inv in sale.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
            sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line],
                    {'state': 'cancel'})
        for sale_order in self.browse(cr, uid, ids, context=context):
            purchase_order_object= self.pool.get('purchase.order')  
            purchase_ids=purchase_order_object.search(cr, uid, [('origin', '=', sale_order.name)], context=context);
            for purchase in purchase_order_object.browse(cr, uid,purchase_ids, context=context):
               for pick in purchase.picking_ids:
                    if pick.state not in ('draft','cancel'):
                       raise osv.except_osv(
                           _('Unable to cancel this purchase order.'),
                           _('First cancel all receptions related to this purchase order.'))
               for pick in purchase.picking_ids:
                   wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
               for inv in purchase.invoice_ids:
                   if inv and inv.state not in ('cancel','draft'):
                       raise osv.except_osv(
                           _('Unable to cancel this purchase order.'),
                           _('You must first cancel all receptions related to this purchase order.'))
                   if inv:
                       wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
            purchase_order_object.write(cr,uid,purchase_ids,{'state':'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        logger.log(3, " one  %s  two%s:   three  %s" %('123', '123', '123'))


        return True
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: