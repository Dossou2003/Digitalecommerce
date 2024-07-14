from django.contrib import admin
from DigitalWaves.models import  CustomUser, Categorie, Produit, Commande, Paiement, Panier, ProduitPanier, ProduitCommande, Facture

admin.site.site_header = "E-Commerce DigitalWaves"
admin.site.site_title = "DigitalWaves Admin"
admin.site.index_title = "AHOUANSOU & AGUE"


class AdminProduit(admin.ModelAdmin):
 list_display= ('nom', 'slug', 'description', 'prix', 'stock', 'categorie', 'image', 'actif', 'date_à_jour')
 search_fields= ('nom','date_à_jour')
 list_editable= ('prix', 'stock', 'actif')
class AdminCommande(admin.ModelAdmin):
 list_display= ('nom', 'email', 'adresse', 'ville', 'pays', 'quantite_totale', 'date_commande', 'statut')
  
admin.site.register(Produit, AdminProduit)
admin.site.register(Categorie)
admin.site.register(Commande, AdminCommande)
admin.site.register(Paiement)
admin.site.register(CustomUser)
admin.site.register(Panier)
admin.site.register(ProduitPanier)
admin.site.register(ProduitCommande)
admin.site.register(Facture)



