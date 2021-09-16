# -*- coding: utf-8 -*-

{
    'name': 'Partially/Semi Finished good Manufacturing Order in Odoo',
    'version': '13.0.0.8',
    'sequence': 4,
    'price': 49,
    'currency': "EUR",
    'summary': 'Apps helps finish partially Manufacturing Order Manufacturing Partial Produce Order Partial Manufacturing order mrp Partial order Semi Finished Manufacturing Order Partial mrp order partially finish order partially finish Manufacturing mo partial mo',
    'description': """Manufacturing partially finished for less then planned quantity
    Manufacturing Partial Produce Order , Semi-Finished Good , Semi-Finished order , Semi-Finished product , 
    Manufacturing Partialy finish order Semi Finished good Manufacturing Order, Partial Finish Order
    Manufacturing Partial Finished Order , Partially completed orders , half completed orders, work in process orders
    Manufacturing Partially Finished Order, Semi Finished product order , Semi Finished work orders 
    mrp partial order
    partial mrp order
    half finished Manufacturing order
    Manufacturing partial workorder
    Manufacturing partial work order
    Manufacturing partial order finish
    partial MO
    MO partial process
    MO partial order
    MO partial, semi finish Order,  Manufacturing semi finish Order, half completed order, mrp Semi Finished product order, mrp Semi Finished order, 
    mrp partial produce
    Partial Production order
    Partial Manufacturing order
    partially Manufacturing order
    half finished order
    complete manufacturing with partial qty.
    complete manufacturing with partial quantity.
    Manufacturing complete order with less then planned qty
    Manufacturing finished order less then planned quantity

Fabrication partiellement finie pour moins de quantité prévue
     Ordre de fabrication de produits partiels
     Fabrication Partially finish order
     mrp ordre partiel
     MO partiel
     MRP produit partiel
     Commande de production partielle
     Ordre de fabrication partiel
     commande partiellement manufacturière
     commande semi-finie
     fabrication complète avec quantité partielle.
     fabrication complète avec quantité partielle.
     Fabrication complète de la commande avec moins de quantité planifiée
     Fabrication fini ordre moins que la quantité prévue

Fabricación parcialmente terminada por menos cantidad planificada
     Fabricación de pedido parcial de productos
     Fabricación parcial de la orden de acabado
     mrp orden parcial
     MO parcial
     mrp produce parcial
     Orden de producción parcial
     Orden de fabricación parcial
     orden de fabricación parcial
     orden a medio terminar
     fabricación completa con cantidad parcial
     fabricación completa con cantidad parcial.
     Fabricación completa con menos cantidad planificada
     La fabricación terminó la orden menos de la cantidad planificada

التصنيع انتهى جزئيا للكمية الأقل من المخطط
     تصنيع إنتاج جزئية
     تصنيع أجل الانتهاء Partialy
     طلب جزئي mrp
     مو جزئية
     تنتج جزئية mrp
     أمر الإنتاج الجزئي
     ترتيب التصنيع الجزئي
     جزئيا ترتيب التصنيع
     نصف النظام النهائي
     التصنيع الكامل مع الكمية الجزئية.
     التصنيع الكامل مع كمية جزئية.
     تصنيع طلب كامل بأقل الكمية المخطط لها
     تصنيع الانتهاء من النظام أقل من الكمية المخطط لها

Produção parcialmente concluída por menos que a quantidade planejada
     Ordem de Produção Parcial de Fabricação
     Fabricação Partialy terminar ordem
     pedido parcial mrp
     MO parcial
     produto parcial mrp
     Ordem de produção parcial
     Pedido de Fabrico Parcial
     parcialmente ordem de fabricação
     ordem meio terminada
     fabricação completa com quantidade parcial.
     fabricação completa com quantidade parcial.
     Pedido completo de fabricação com menos do que o valor planejado
     Fabricação de ordem finalizada menos do que a quantidade planejada

    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','mrp'],
    'data': [
        "views/mrp_production_view.xml",
        "views/mrp_workorder_view.xml",
        "wizard/mrp_partial_qty_wizard.xml",
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/2JVwyPVxQu4',
    "images":["static/description/Banner.png"],
}
