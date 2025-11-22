document.addEventListener('DOMContentLoaded', function(){
  window.buy = async function(movieId){
    const qtyEl = document.getElementById(`qty-${movieId}`);
    const qty = Number(qtyEl?.value || 1);

    const res = await fetch('/create_order', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({movie_id: movieId, qty})
    });

    const data = await res.json();
    if(!res.ok){
      alert(data.detail || 'Could not create order');
      return;
    }

    const options = {
      key: data.key,
      amount: data.amount,
      currency: data.currency,
      name: 'Movie Tickets',
      description: 'Purchase',
      order_id: data.order_id,
      handler: async function(response){
        const verifyRes = await fetch('/verify', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(response)
        });
        const verifyData = await verifyRes.json();
        if(verifyRes.ok){
          window.location = `/success?payment_id=${verifyData.payment_id}`;
        } else {
          alert('Payment verification failed');
        }
      },
      prefill: {name:'', email:''},
      theme: {color:'#F37254'}
    };

    const rzp = new Razorpay(options);
    rzp.open();
  }
});
