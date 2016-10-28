{
    'version': '20161017',
    'databases': [],  # let's empty to apply to all db
    'description': '',
    'modules_to_upgrade': [
        'base',
        'barcodes_generate',
        'coop_shift_state',
        'pos_automatic_cashdrawer',
        'pos_payment_terminal',
        'pos_payment_terminal_return',
        'product_supplierinfo_discount',
    ],  # to install/update
    'pre-load': [],  # only .sql
    'post-load': [],  # .sql and .yml
}
