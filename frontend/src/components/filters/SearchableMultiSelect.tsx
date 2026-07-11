import { useState } from 'react'
import { Check, ChevronDown, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { cn } from '@/lib/utils'

interface SearchableMultiSelectProps {
  label: string
  options: string[]
  selected: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  loading?: boolean
}

export function SearchableMultiSelect({ label, options, selected, onChange, placeholder, loading }: SearchableMultiSelectProps) {
  const [open, setOpen] = useState(false)

  function toggle(value: string) {
    onChange(selected.includes(value) ? selected.filter((v) => v !== value) : [...selected, value])
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        aria-expanded={open}
        render={
          <Button
            variant="outline"
            size="sm"
            className="h-9 min-w-[140px] justify-between gap-2 border-border/60 bg-white/40 font-normal dark:bg-white/5"
          />
        }
      >
        <span className="flex items-center gap-1.5 truncate">
          <span className="text-muted-foreground">{label}</span>
          {selected.length > 0 && (
            <Badge variant="secondary" className="h-5 rounded-full px-1.5 font-mono text-[10px]">
              {selected.length}
            </Badge>
          )}
        </span>
        <ChevronDown className="h-3.5 w-3.5 shrink-0 opacity-50" />
      </PopoverTrigger>
      <PopoverContent className="w-64 p-0" align="start">
        <Command>
          <CommandInput placeholder={placeholder ?? `Search ${label.toLowerCase()}...`} />
          <CommandList>
            <CommandEmpty>{loading ? 'Loading…' : 'No results found.'}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => {
                const isSelected = selected.includes(option)
                return (
                  <CommandItem key={option} onSelect={() => toggle(option)}>
                    <div
                      className={cn(
                        'flex h-4 w-4 items-center justify-center rounded-sm border border-primary',
                        isSelected ? 'bg-primary text-primary-foreground' : 'opacity-50',
                      )}
                    >
                      {isSelected && <Check className="h-3 w-3" />}
                    </div>
                    <span className="truncate">{option}</span>
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </CommandList>
          {selected.length > 0 && (
            <div className="flex items-center justify-between border-t border-border/60 px-2 py-1.5">
              <span className="text-[11px] text-muted-foreground">{selected.length} selected</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 gap-1 px-2 text-[11px] text-muted-foreground"
                onClick={() => onChange([])}
              >
                <X className="h-3 w-3" />
                Clear
              </Button>
            </div>
          )}
        </Command>
      </PopoverContent>
    </Popover>
  )
}
