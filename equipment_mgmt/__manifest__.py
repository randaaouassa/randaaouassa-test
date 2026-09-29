{
    'name': 'Equipment Management',
    'version': '17.0.1.0.0',
    'category': 'Operations',
    'summary': 'Manage company equipment and employee assignments',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
