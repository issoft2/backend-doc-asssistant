<!-- BillingPage.vue -->
<template>
  <div class="billing-container">
    <Card>
      <template #title>Choose Payment Method</template>
      <template #content>
        <!-- Gateway Selection -->
        <div class="gateway-selector">
          <label>Payment Provider:</label>
          <Dropdown 
            v-model="selectedGateway"
            :options="gateways"
            optionLabel="name"
            optionValue="id"
            placeholder="Select gateway"
            class="w-full"
          />
        </div>

        <!-- Plan Selection -->
        <div class="plan-selector mt-4">
          <DataTable :value="plans" selectionMode="single" v-model:selection="selectedPlan">
            <Column field="name" header="Plan"></Column>
            <Column field="price_monthly" header="Price">
              <template #body="{ data }">
                {{ formatCurrency(data.price_monthly, selectedGateway) }}
              </template>
            </Column>
          </DataTable>
        </div>

        <!-- Pay Button -->
        <Button 
          v-if="selectedGateway && selectedPlan"
          label="Pay Now" 
          @click="checkout"
          :loading="loading"
          class="w-full mt-4"
          severity="success"
        />
      </template>
    </Card>
  </div>
</template>

<script setup>
const selectedGateway = ref(null)
const selectedPlan = ref(null)
const loading = ref(false)
const gateways = ref([])


onMounted(async () => {
  const { data } = await api.get('/billing/gateways')
  gateways.value = data.gateways
})

// Dynamic currency based on gateway
const formatCurrency = (price, gatewayId) => {
  const gateway = gateways.value.find(g => g.id === gatewayId)
  const symbol = gateway?.currencies[0] === 'NGN' ? '₦' : '$'
  return `${symbol}${price.toLocaleString()} / mo`
}

async function checkout() {
  loading.value = true
  try {
    const { data } = await api.post('/billing/checkout', {
      provider: selectedGateway.value,
      plan_id: selectedPlan.value.id
    })
    window.location.href = data.url  // Redirect to Stripe/Paystack/Flutterwave
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.billing-container {
  max-width: 600px;
  margin: 0 auto;
}
.gateway-selector {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
