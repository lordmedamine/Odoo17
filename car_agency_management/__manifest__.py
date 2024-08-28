{
    'name': 'Car Agency Management',
    'author': 'Oueriemmi',
    'category': 'Uncategorized',
    'version': '17.0.0.1.0',
    'depends': ['base', 'account','mail'
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/car_rating_wizard_view.xml',
        'wizard/car_maintenance_wizard_view.xml',
        'reports/history_report.xml',
        'reports/Request_report.xml',
        'reports/invoice_report.xml',
        'views/car_brand_view.xml',
        'views/car_agency_view.xml',
        'views/car_vehicle_view.xml',
        'views/car_customer_view.xml',
        'views/car_maintenance_view.xml',
        'views/price_config_view.xml',
        'views/car_history_view.xml',
        'views/car_request_view.xml',
        'views/car_invoice_view.xml',
        'data/mail_template.xml',
        'data/reminder_template.xml',
        'views/base_menu_view.xml',
    ],
    'assets': {
        'web.assets_backend': ['car_agency_management/static/src/css/car_brand.css',
                               'car_agency_management/static/src/css/car_vehicle.css']
    },
    'application': True,
}
