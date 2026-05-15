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

  it('shows placeholder style when no state is selected', () => {
    render(<UserDetailsStep formData={baseFormData} onChange={onChange} />)

    const select = screen.getByRole('combobox')
    expect(select).toHaveClass('bg-white', 'text-gray-400')
  })

  it('shows readable selected text and option styles', () => {
    render(
      <UserDetailsStep
        formData={{ ...baseFormData, state: 'Andhra Pradesh' }}
        onChange={onChange}
      />
    )

    const select = screen.getByRole('combobox')
    const andhraOption = screen.getByRole('option', { name: 'Andhra Pradesh' })

    expect(select).toHaveClass('bg-white', 'text-gray-900')
    expect(andhraOption).toHaveClass('bg-white', 'text-gray-900')
  })

  it('calls onChange with selected state', () => {
    render(<UserDetailsStep formData={baseFormData} onChange={onChange} />)

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Assam' } })

    expect(onChange).toHaveBeenCalledWith('state', 'Assam')
  })
})
