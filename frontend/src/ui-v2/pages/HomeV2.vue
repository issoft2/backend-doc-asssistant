<!--ui-v2/pages/HomeV2.vue-->
<template>
  <MarketingLayout>
    <!-- Above the fold -->
    <HeroSection />

    <!-- Core Value Props -->
    <FeatureSection />

      <!-- Human touch -->
    <ContactSection class="border-4 border-red-500 min-h-[200px]" />

    
    <!-- Explanation -->
    <HowItWork/>

    <!-- Conversation -->
    <CTASection />


    <!-- Legal / Trust-->
    <FooterSection />
  </MarketingLayout>

</template>

<script setup>

// import the layout
import MarketingLayout from '../layouts/MarketingLayout.vue'


// import the sections
import HeroSection from '../sections/HeroSection.vue'
import FeatureSection from '../sections/FeatureSection.vue'
import HowItWork from '../sections/HowItWork.vue'
import CTASection from '../sections/CTASection.vue'


import ContactSection from '../sections/ContactSection.vue'

import FooterSection from '../sections/FooterSection.vue'

</script>