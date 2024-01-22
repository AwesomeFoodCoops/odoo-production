
def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        DELETE FROM stock_inventory_category_group_line
        WHERE group_id ISNULL
    """)
    return
