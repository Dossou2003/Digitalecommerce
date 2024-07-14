document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('panier') == null) {
        var panier = {};
    } else {
        panier = JSON.parse(localStorage.getItem('panier'));
    }

    function updateCartCount() {
        var count = 0;
        for (var key in panier) {
            count += panier[key]['quantite'];
        }
        document.getElementById('panier').innerText = count;
    }

  
    document.querySelectorAll('.panier').forEach(function(button) {
        button.addEventListener('click', function() {
            var productid = this.getAttribute('data-id');
            var productnom = this.getAttribute('data-nom');
            var productprix = parseFloat(this.getAttribute('data-prix'));

            if (panier[productid]) {
                panier[productid]['quantite'] += 1;
            } else {
                panier[productid] = {
                    'nom': productnom,
                    'prix': productprix,
                    'quantite': 1
                };
            }

            localStorage.setItem('panier', JSON.stringify(panier));
            alert('Produit ajouté avec succès');
            updateCartCount();
        });
    });

    updateCartCount();
});
