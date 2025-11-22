document.addEventListener('DOMContentLoaded', function(){
  window.buy = async function(movieId){
    const qtyEl = document.getElementById(`qty-${movieId}`);
    const qty = Number(qtyEl?.value || 1);

    try {
      const res = await fetch('/create-checkout-session', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({movie_id: movieId, qty})
      });

      const data = await res.json();
      if(!res.ok){
        alert(data.detail || 'Could not create checkout session');
        return;
      }

      // Redirect to Stripe Checkout
      if(data.url){
        window.location.href = data.url;
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  }
});
