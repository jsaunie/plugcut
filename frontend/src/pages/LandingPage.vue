<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import CommissionCalculator from '@/components/landing/CommissionCalculator.vue'
import CtaBand from '@/components/landing/CtaBand.vue'
import FaqSection from '@/components/landing/FaqSection.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import HowItWorks from '@/components/landing/HowItWorks.vue'
import MarqueeStrip from '@/components/landing/MarqueeStrip.vue'
import PillarsSection from '@/components/landing/PillarsSection.vue'
import TheFooter from '@/components/landing/TheFooter.vue'
import TheHeader from '@/components/landing/TheHeader.vue'
import PerforatedDivider from '@/components/shared/PerforatedDivider.vue'
import { useSeo } from '@/shared/seo'

const { t } = useI18n()
useSeo({
  title: t('seo.landingTitle'),
  description: t('seo.landingDescription'),
  path: '/',
})
</script>

<template>
  <TheHeader />
  <main>
    <HeroSection />
    <MarqueeStrip />
    <HowItWorks />
    <PillarsSection />
    <CommissionCalculator />
    <PerforatedDivider />
    <FaqSection />
    <CtaBand />
  </main>
  <TheFooter />
</template>
