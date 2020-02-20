{
    "name": "Coop - Parental Leave",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "summary": "Custom settings for Parental Leave",
    "author": "La Louve, Druidoo",
    "website": "http://www.lalouve.net",
    "license": "AGPL-3",
    "depends": [
        "coop_shift",
        "coop_membership"
    ],
    "data": [
        # Classical Data
        "views/view_shift_leave.xml",
        # Custom Data
        "data/ir_cron.xml",
        "data/email_template_data.xml",
    ],
    "installable": True,
}
