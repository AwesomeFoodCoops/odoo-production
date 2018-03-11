#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import division
import erppeek
import sys
from config_prod import odoo_configuration_user
#from config_test import odoo_configuration_user
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re


###############################################################################
# Odoo Connection
###############################################################################


def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

##################################################################
##########                  SET LOGGER                  ##########
##################################################################
class Logger(object):
    def __init__(self, filename='Default.log'):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

log_file = 'log_' + datetime.now().strftime("%Y-%m-%d %H_%M_%s")+'.log'
print "stdout = ./"+log_file
sys.stdout = Logger(log_file)
print datetime.now().strftime("%Y-%m-%d %H_%M_%s")

###############################################################################
# Script
###############################################################################

liste_immo_2016 = [
{'name':'0016 Qualiconsult /virt 130117','category_id':3,'invoice_line_id':86718,'amount_total':160,'dotation_2016':6.03},
{'name':'0017 Qualiconsult real 1/6 2/6','category_id':3,'invoice_line_id':86719,'amount_total':1500,'dotation_2016':48.21},
{'name':'0024 Qualiconsult attestation','category_id':3,'invoice_line_id':86720,'amount_total':600,'dotation_2016':13.57},
{'name':'0023 Qualiconsult CT et RVRAT','category_id':3,'invoice_line_id':86721,'amount_total':1000,'dotation_2016':22.62},
{'name':'0025 GpeFluide tude tech sold','category_id':3,'invoice_line_id':87004,'amount_total':1000,'dotation_2016':9.13},
{'name':'0021 Namixis coord SSI - 5 r c','category_id':3,'invoice_line_id':87005,'amount_total':780,'dotation_2016':20.43},
{'name':'0013 qualicslt r al trvx 6/6 v','category_id':3,'invoice_line_id':98358,'amount_total':500,'dotation_2016':32.14},
{'name':'0012 qualicslt suivi trvx 5/5','category_id':3,'invoice_line_id':98359,'amount_total':608,'dotation_2016':41.74},
{'name':'0010 Qualiconsult suivi travx','category_id':3,'invoice_line_id':98360,'amount_total':608,'dotation_2016':47.29},
{'name':'0008 Qualiconsult travx 5/6','category_id':3,'invoice_line_id':98361,'amount_total':500,'dotation_2016':43.06},
{'name':'0007 Qualiconsult suivi 3/5','category_id':3,'invoice_line_id':98362,'amount_total':608,'dotation_2016':55.73},
{'name':'0006 Qualiconsult NH/virt 08/6','category_id':3,'invoice_line_id':98364,'amount_total':1216,'dotation_2016':127.39},
{'name':'0005 Qualiconsult honos trvx v','category_id':3,'invoice_line_id':98367,'amount_total':500,'dotation_2016':58.13},
{'name':'0004 GpeFluides Etude NH','category_id':3,'invoice_line_id':98368,'amount_total':500,'dotation_2016':64.09},
{'name':'0003 Phaz Elec F334 Travx Elec','category_id':3,'invoice_line_id':98369,'amount_total':1468,'dotation_2016':200.39},
{'name':'0009 EaudeParis branchement RI','category_id':3,'invoice_line_id':98372,'amount_total':670,'dotation_2016':53.97},
{'name':'0001 Namixis suivi 3/3','category_id':3,'invoice_line_id':108652,'amount_total':346.66,'dotation_2016':17.2},
{'name':'0011 Namixis Hono coord SSI+su','category_id':3,'invoice_line_id':108760,'amount_total':1127,'dotation_2016':81.84},
{'name':'0014 Namixis cood SSI honos su','category_id':3,'invoice_line_id':108762,'amount_total':346.66,'dotation_2016':22.01},
{'name':'0015 EauxdeParis branchement D','category_id':3,'invoice_line_id':108806,'amount_total':3267.15,'dotation_2016':173.73},
{'name':'0019 LAGAE / virt Peinture trv','category_id':3,'invoice_line_id':108853,'amount_total':1500.82,'dotation_2016':43.48},
{'name':'0020 JLJ Concept Install. Ince','category_id':3,'invoice_line_id':108854,'amount_total':1127,'dotation_2016':31.31},
{'name':'0022 Panofrance /ch3074911 Men','category_id':3,'invoice_line_id':108856,'amount_total':1161.03,'dotation_2016':29.49},
{'name':'0018 Orange Installation c bla','category_id':3,'invoice_line_id':109381,'amount_total':1254.45,'dotation_2016':37.83},
{'name':'0042 Axess rayonnages chb froi','category_id':9,'invoice_line_id':80379,'amount_total':4027.2,'dotation_2016':35.8},
{'name':'0049 BIZERBA balance3 SCII-100','category_id':12,'invoice_line_id':109087,'amount_total':2100,'dotation_2016':110.83},
{'name':'0048 BIZERBA bal tiquettage v','category_id':12,'invoice_line_id':109088,'amount_total':6950,'dotation_2016':1046.36},
{'name':'0059 LDLC CAISSE 4 souris logi','category_id':13,'invoice_line_id':107289,'amount_total':24.98,'dotation_2016':1.97},
{'name':'0058 LDLC CAISSE 4','category_id':13,'invoice_line_id':107288,'amount_total':38.33,'dotation_2016':3.02},
{'name':'0055 LDLC CAISSE 4 Netgear GS1','category_id':13,'invoice_line_id':107285,'amount_total':116.33,'dotation_2016':9.16},
{'name':'0056 LDLC CAISSE 4 Samsung SSD','category_id':13,'invoice_line_id':107286,'amount_total':199.83,'dotation_2016':15.73},
{'name':'0057 LDLC CAISSE 4 Impr. Epson','category_id':13,'invoice_line_id':107287,'amount_total':599.83,'dotation_2016':47.21},
{'name':'0050 PC21. MatInfo Caisse 1','category_id':13,'invoice_line_id':109094,'amount_total':403.57,'dotation_2016':59.41},
{'name':'0054 PC21 /cb 4 KingstonRAM CA','category_id':13,'invoice_line_id':109172,'amount_total':152.72,'dotation_2016':12.3},
{'name':'0053 PC21 /cb 4 shuttle CAISSE','category_id':13,'invoice_line_id':109171,'amount_total':630.56,'dotation_2016':50.8},
{'name':'0052 NDF ZK CAISSE 1','category_id':13,'invoice_line_id':110036,'amount_total':45.83,'dotation_2016':6.45},
{'name':'0060 Biocreation bois Install / Matériel vrac','category_id':13,'invoice_line_id':109220,'amount_total':10051.68,'dotation_2016':217.79},
{'name':'0001 LDLC VIDEO 16 licences','category_id':2,'invoice_line_id':107279,'amount_total':533.25,'dotation_2016':125.91},
{'name':'0043 JBG frigo RDH-2,5-H4','category_id':10,'invoice_line_id':109089,'amount_total':6270,'dotation_2016':532.95},
{'name':'0045 JBG x2 frigos SNA-2,342-H','category_id':10,'invoice_line_id':109091,'amount_total':11760,'dotation_2016':999.6},
{'name':'0044 JBG frigo x2 RDH-3.75-L2','category_id':10,'invoice_line_id':109090,'amount_total':13644,'dotation_2016':1159.74},
{'name':'0038 LDLC Reseau routeur','category_id':6,'invoice_line_id':107284,'amount_total':120.79,'dotation_2016':9.51},
{'name':'0037 PC21 /cb RESEAU c balages','category_id':6,'invoice_line_id':109170,'amount_total':64,'dotation_2016':5.16},
{'name':'0035 PC21 /cb RESEAU Commut GS','category_id':6,'invoice_line_id':109168,'amount_total':114.4,'dotation_2016':9.22},
{'name':'0001 PC21 /cb RESEAU CommutGS7','category_id':6,'invoice_line_id':109166,'amount_total':275.94,'dotation_2016':22.23},
{'name':'0034 PC21 /cb RESEAU CommutGS7','category_id':6,'invoice_line_id':109167,'amount_total':275.94,'dotation_2016':22.23},
{'name':'0036 PC21 /cb RESEAU 6 pack wi','category_id':6,'invoice_line_id':109169,'amount_total':792.33,'dotation_2016':63.83},
{'name':'0039 AES print Imprimante badg','category_id':7,'invoice_line_id':108857,'amount_total':965,'dotation_2016':75.06},
{'name':'0040 multiaxe 8 cam ras AxisM1','category_id':7,'invoice_line_id':108860,'amount_total':1872,'dotation_2016':145.6},
{'name':'0029 LDLC PC sal. 5 souris log','category_id':4,'invoice_line_id':107280,'amount_total':31.21,'dotation_2016':3.77},
{'name':'0028 LDLC PC sal. 4 clav. logi','category_id':4,'invoice_line_id':107281,'amount_total':47.92,'dotation_2016':2.46},
{'name':'0026 5 DELL Latitude E7470/i7-','category_id':4,'invoice_line_id':109218,'amount_total':6950,'dotation_2016':682.13},
{'name':'0027 PC21 /cb 5 Ecrans DELL','category_id':4,'invoice_line_id':109095,'amount_total':838.5,'dotation_2016':67.55},
{'name':'0031 LDLC SERVEUR 2PC Brix6','category_id':5,'invoice_line_id':107282,'amount_total':833.25,'dotation_2016':65.58},
{'name':'0030 PC21 /cb Rack Synlogy SER','category_id':5,'invoice_line_id':109165,'amount_total':1081.76,'dotation_2016':87.14},
{'name':'0032 PC21 seagate HDD ST4000','category_id':5,'invoice_line_id':109219,'amount_total':531.8,'dotation_2016':38.9},
{'name':'0033 LDLC Digitus 3 tablettes+','category_id':5,'invoice_line_id':109222,'amount_total':62.17,'dotation_2016':3.28},
{'name':'0040 Tible bois menuiserie/cb','category_id':8,'invoice_line_id':108928,'amount_total':527.46,'dotation_2016':14.36},
{'name':'0041 Tible menuiserie/cb','category_id':8,'invoice_line_id':108929,'amount_total':819.31,'dotation_2016':15.93},
{'name':'0047 Monetik Cashlogy monnayeu','category_id':11,'invoice_line_id':109084,'amount_total':126,'dotation_2016':6.93},
{'name':'0046 Monetik Cashlogy monnayeu','category_id':11,'invoice_line_id':109041,'amount_total':8579,'dotation_2016':471.85},
]

#TODO : ajouter à la main la fiche immo de dev Odoo 2016
#TODO : vier les champs asset_* des invoice lines dont les fiches immo ont été supprimées
#   > celles de dev odoo 2016
#   > 0060 Biocreation bois Install
#   > ID invoice line in  [109220, 110035, 114553, 114985]

# https://github.com/AwesomeFoodCoops/odoo-production/blob/9.0/odoo/addons/account_asset/account_asset.py

def suppression_immo_2016():

    immo_2017 = openerp.AccountAssetAsset.browse([('date', '<', '2017-01-01')],order='id')

    #Supprimer toutes les immos et écritures antérieur au 1er janvier 2017
    for immo in immo_2017:
        print "=================",immo.id," => ",immo.name.encode('utf-8')
        print "     > nombre de ligne d'amortissement", len(immo.depreciation_line_ids)
        for asset_line in immo.depreciation_line_ids :
            print "         > Amortissement ",asset_line.id, "=>", asset_line.name.encode('utf-8')
            #supprimer les écritures passées
            m = asset_line.move_id
            if m:
                print "               > Ecriture de l'amortissement ",m.id, "=>", m.name.encode('utf-8')
                #m = openerp.AccountMove.browse([('id', '=', move_id.id)])
                print m.button_cancel()
                print "                      > Ecriture annulée (remise en brouillon)"
                #print m.state="draft"
                print openerp.AccountMove.unlink(m.id)
                print "                      > Ecriture supprimée"
                #TODO : vérifier qu'il n'y a pas besoin de remettre à l'état brouillon dans certains cas
            #supprimer les lignes de dépréciation
            openerp.AccountAssetDepreciationLine.unlink(asset_line.id)
            print "     > Amortissement supprimé"
        #supprimer les fiches immos
        print "Tous les ammortissements ont été supprimés pour l'immo ID=",immo.id
        print immo.write({'state': 'draft'})
        print "Fiche remise à l'état brouillon."
        print openerp.AccountAssetAsset.unlink(immo.id)
        print "Fiche immo supprimée."

def reprise_immo_2016():
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print "     ETAPE DE SUPPRESSION TERMINEE"
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

    #Recréer les fiches immo et les dépreciation line
    for immo_2016 in liste_immo_2016:
        print "================="
        print immo_2016
        invoice_line = openerp.AccountInvoiceLine.browse([('id','=',immo_2016['invoice_line_id'])])[0]
        asset_category = invoice_line.asset_category_id

        amount_total = immo_2016['amount_total']
        value = amount_total # ATTENTION : pour la invoice line 107288 leprix d'achat est 60€ mais seuls 38,33 sont amortissables
        dotation_2016 = immo_2016['dotation_2016']
        residual_amount = amount_total - dotation_2016
        #deprec_by_month = invoice_line.invoice_id.currency_id.round(amount_total / (asset_category.method_number * asset_category.method_period))
        deprec_by_month = round(amount_total / (asset_category.method_number * asset_category.method_period), 2)
        seq = 1

        #Check taht amount_total = amount of the invoice line
        if amount_total != invoice_line.price_subtotal_signed :
            print "         => Erreur : amount_total != value "

        asset_dic = {
            'name':immo_2016['name'],
            'code':invoice_line.name,
            'value' : value,
            'type' : 'purchase',
            'category_id' : asset_category.id,
            'company_id': invoice_line.invoice_id.company_id.id,
            'currency_id': 1,
            'date' : invoice_line.invoice_id.date_invoice,
            'state' : 'open',
            'partner_id' : invoice_line.partner_id.id,
            'method': asset_category.method,
            'method_number': asset_category.method_number,
            'method_period': asset_category.method_period,
            'method_end': asset_category.method_end,
            'method_progress_factor': asset_category.method_progress_factor,
            'method_time': asset_category.method_time,
            'prorata': asset_category.prorata,
            'salvage_value' : 0.0,
            'invoice_id' : invoice_line.invoice_id.id,
            'note' : "# Reprise immo 2016 : 1 seule écriture du "+ datetime.strptime(invoice_line.invoice_id.date_invoice,'%Y-%m-%d').strftime('%d/%m/%Y') +"(date de facturation) au 31/12/2016 pour coller aux comptes 2016 puis une écriture par mois pour permettre d'avoir des situations mensuelles.",
        }
        print asset_dic
        asset = openerp.AccountAssetAsset.create(asset_dic)
        print "Asset créé", asset, asset.id
        # à la création d'une fiche immo, le board est toujours auto-calculé.
        # Remove old unposted depreciation lines.
        print asset.depreciation_line_ids.id
        openerp.AccountAssetDepreciationLine.unlink(asset.depreciation_line_ids.id)
        print "Tous les ammortissements ont été supprimés."
        commands=[]


        depreciation_2016 = {
            'amount': dotation_2016,
            'asset_id': asset.id,
            'sequence': seq,
            'name': invoice_line.name + '/' + str(seq),
            'remaining_value': residual_amount,
            'depreciated_value': value - residual_amount,
            'depreciation_date': '2016-12-31',
        }
        print "depreciation_2016", depreciation_2016
        openerp.AccountAssetDepreciationLine.create(depreciation_2016)
        print "depreciation_2016 OK"

        print "deprec_by_month", deprec_by_month

        while (residual_amount > 0.0):
            seq += 1
            if residual_amount > deprec_by_month :
                print "             residual_amount > deprec_by_month"
                amount_periode = deprec_by_month
                residual_amount -= amount_periode
            else :
                print "             residual_amount <= deprec_by_month"
                amount_periode = residual_amount
                residual_amount  = 0.0

            deprec = {
                'amount':amount_periode,
                'asset_id': asset.id,
                'sequence': seq,
                'name': asset.name + '/' + str(seq) + '# Reprise immo du '+ datetime.strptime(asset.date,'%Y-%m-%d').strftime('%d/%m/%Y') +' au 31/12/2016',
                'remaining_value': residual_amount,
                'depreciated_value': value - residual_amount,
                'depreciation_date': (datetime.strptime('2016-12-31','%Y-%m-%d') + relativedelta(months=seq-1)).strftime('%Y-%m-%d'),
            }
            print "         > depreciation", seq, deprec
            openerp.AccountAssetDepreciationLine.create(deprec)
            print "depreciation", seq, "OK"

        asset = openerp.AccountAssetAsset.browse([('id','=',asset.id)])[0]
        check_amount=0.0
        for i in asset.depreciation_line_ids:
            check_amount += i.amount
        print "check_amount", check_amount
        print "amount total", immo_2016['amount_total']
        if abs(check_amount - immo_2016['amount_total']) > 0.000001:
            print "         ==> Erreur total depreciation : ", abs(check_amount - immo_2016['amount_total'])
        else :
            print "TOTAL OK"
        exit()

#suppression_immo_2016()
#reprise_immo_2016()

print "\n>>>>>>> DONE >>>>>>>>>>"
print datetime.now().strftime("%Y-%m-%d %H_%M_%s")
