import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { TimePeriodPicker } from '@/components/filters/TimePeriodPicker'
import { SearchableMultiSelect } from '@/components/filters/SearchableMultiSelect'
import { useFilterStore } from '@/store/filterStore'
import { useFilterOptions } from '@/hooks/useFilterOptions'
import { BUSINESS_VERTICALS } from '@/types/filters'

export function FilterBar() {
  const { filters, setBusinessVerticals, setProducts, setSuppliers, setCustomers, clearAll } = useFilterStore()
  const { options, isLoading } = useFilterOptions()

  const activeCount =
    filters.businessVerticals.length + filters.products.length + filters.suppliers.length + filters.customers.length

  return (
    <div className="flex items-center gap-2 border-b border-border/60 bg-background/60 px-6 py-2.5 backdrop-blur-sm">
      <TimePeriodPicker />
      <Separator orientation="vertical" className="h-6" />
      <SearchableMultiSelect
        label="Vertical"
        options={[...BUSINESS_VERTICALS]}
        selected={filters.businessVerticals}
        onChange={setBusinessVerticals}
      />
      <SearchableMultiSelect
        label="Product"
        options={options.products}
        selected={filters.products}
        onChange={setProducts}
        loading={isLoading}
      />
      <SearchableMultiSelect
        label="Supplier"
        options={options.suppliers}
        selected={filters.suppliers}
        onChange={setSuppliers}
        loading={isLoading}
      />
      <SearchableMultiSelect
        label="Customer"
        options={options.customers}
        selected={filters.customers}
        onChange={setCustomers}
        loading={isLoading}
      />
      {activeCount > 0 && (
        <Button variant="ghost" size="sm" className="h-9 gap-1.5 text-muted-foreground" onClick={clearAll}>
          <X className="h-3.5 w-3.5" />
          Clear filters
        </Button>
      )}
    </div>
  )
}
