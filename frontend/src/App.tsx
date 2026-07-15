import { Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { OverviewPage } from '@/pages/OverviewPage'
import { CapitalFlowPage } from '@/pages/CapitalFlowPage'
import { PaymentTermsPage } from '@/pages/PaymentTermsPage'
import { PillarPlaceholder } from '@/pages/PillarPlaceholder'
import { PILLARS } from '@/types/common'

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/capital-flow" element={<CapitalFlowPage />} />
        <Route path="/capital-flow/payment-terms" element={<PaymentTermsPage />} />
        {PILLARS.filter((pillar) => pillar.id !== 'capital-flow').map((pillar) => (
          <Route
            key={pillar.id}
            path={pillar.route}
            element={<PillarPlaceholder name={pillar.name} description={pillar.description} />}
          />
        ))}
      </Routes>
    </AppShell>
  )
}

export default App
