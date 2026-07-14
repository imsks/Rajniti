import { fireEvent, render, screen } from '@testing-library/react'
import UserDetailsStep from '@/components/onboarding/UserDetailsStep'

const onChange = jest.fn()

const baseFormData = {
  phone: '',
  state: '',
  city: '',
  age_group: '',
}

describe('UserDetailsStep', () => {
  beforeEach(() => {
    onChange.mockReset()
  })

  it('shows the placeholder option when no state is selected', () => {
    render(<UserDetailsStep formData={baseFormData} onChange={onChange} />)

    const select = screen.getByRole('combobox') as HTMLSelectElement
    expect(select.value).toBe('')
    // Token-driven select adapts to dark mode; empty state is tinted subtle.
    expect(select).toHaveClass('bg-surface', 'text-content-subtle')
    expect(
      screen.getByRole('option', { name: 'Select your state' }),
    ).toBeInTheDocument()
  })

  it('reflects the selected state', () => {
    render(
      <UserDetailsStep
        formData={{ ...baseFormData, state: 'Andhra Pradesh' }}
        onChange={onChange}
      />
    )

    const select = screen.getByRole('combobox') as HTMLSelectElement
    expect(select.value).toBe('Andhra Pradesh')
    expect(select).toHaveClass('bg-surface', 'text-content')
    expect(
      screen.getByRole('option', { name: 'Andhra Pradesh' }),
    ).toBeInTheDocument()
  })

  it('calls onChange with selected state', () => {
    render(<UserDetailsStep formData={baseFormData} onChange={onChange} />)

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Assam' } })

    expect(onChange).toHaveBeenCalledWith('state', 'Assam')
  })
})
