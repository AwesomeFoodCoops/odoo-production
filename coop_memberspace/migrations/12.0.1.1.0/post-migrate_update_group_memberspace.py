from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Add memberspace group to all portal user
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        memberspace_group = env.ref('coop_memberspace.group_memberspace', False)
        portal_group = env.ref('base.group_portal', False)
        if memberspace_group and portal_group:
            mgid = memberspace_group.id
            pgid = portal_group.id
            sql = '''
                select uid from res_groups_users_rel
                where gid in ({mgid}, {pgid}) and uid in (
                    select uid from res_groups_users_rel where gid={pgid}
                )
                group by uid having count(1) = 1;
            '''.format(mgid=mgid, pgid=pgid)
            cr.execute(sql)
            uids = [x[0] for x in cr.fetchall()]
            if uids:
                vals = {'groups_id': [(4, mgid)]}
                users = env['res.users'].browse(uids)
                users.write(vals)
